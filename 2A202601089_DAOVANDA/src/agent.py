import re
from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(
        self,
        question: str,
        top_k: int = 3,
        metadata_filter: dict | None = None,
    ) -> str:
        if metadata_filter:
            results = self.store.search_with_filter(
                question,
                top_k=top_k,
                metadata_filter=metadata_filter,
            )
        else:
            results = self.store.search(question, top_k=top_k)

        context = "\n\n".join(
            self._format_source(index, result)
            for index, result in enumerate(results, start=1)
        )
        if not context:
            context = "(Không tìm thấy ngữ cảnh liên quan trong cơ sở tri thức.)"

        prompt = (
            "# Vai trò\n"
            "Bạn là trợ lý hỏi đáp RAG. Chỉ trả lời bằng thông tin có trong "
            "phần <context>; nếu ngữ cảnh không đủ, hãy nói rõ phần còn thiếu.\n\n"
            "# Yêu cầu bắt buộc\n"
            "1. Xác định đúng chính sách hoặc quy trình mà câu hỏi đề cập; bỏ "
            "qua các đoạn lân cận không cùng chủ đề.\n"
            "2. Trước khi viết câu trả lời, hãy âm thầm lập danh sách kiểm kê "
            "mọi chi tiết liên quan trực tiếp trong nguồn: số lượng, thời lượng, "
            "tần suất theo ngày/tuần, thời điểm được đặt trước, điều kiện, ngoại "
            "lệ, trách nhiệm, các bước xử lý và hậu quả.\n"
            "3. Trả lời đầy đủ từng mục trong danh sách kiểm kê. Đặc biệt, "
            "không được bỏ sót bất kỳ con số hoặc mốc thời gian liên quan nào "
            "trong cùng chính sách, kể cả khi câu hỏi không gọi tên trực tiếp "
            "mốc đó.\n"
            "4. Trước khi hoàn tất, đối chiếu lại câu trả lời với nguồn và bổ "
            "sung mọi chi tiết liên quan còn thiếu. Không trình bày danh sách "
            "kiểm kê hay quá trình suy luận.\n"
            "5. Sau mỗi ý, ghi nhãn [Nguồn n] đúng với nguồn đã sử dụng. Không "
            "suy đoán hoặc thêm kiến thức bên ngoài.\n\n"
            f"<context>\n{context}\n</context>\n\n"
            f"<question>\n{question}\n</question>\n\n"
            "<answer>"
        )
        answer = self.llm_fn(prompt).strip()
        supporting_paragraph = self._best_supporting_paragraph(
            question,
            results[0]["content"] if results else "",
        )
        if supporting_paragraph:
            answer = (
                f"{answer}\n\n"
                "Thông tin đối chiếu trực tiếp từ chính sách: "
                f"{supporting_paragraph} [Nguồn 1]"
            )
        return answer

    @staticmethod
    def _format_source(index: int, result: dict) -> str:
        metadata = result.get("metadata") or {}
        doc_id = metadata.get("doc_id", result.get("id", "unknown"))
        source_url = metadata.get("source_url", metadata.get("source", "unknown"))
        chunk_index = metadata.get("chunk_index", "unknown")
        return (
            f"[Nguồn {index}: doc_id={doc_id}; chunk={chunk_index}; "
            f"url={source_url}]\n{result['content']}"
        )

    @staticmethod
    def _best_supporting_paragraph(question: str, content: str) -> str:
        """Chọn đoạn top-1 liên quan nhất để câu trả lời luôn kiểm chứng được."""

        stop_words = {
            "ai",
            "bao",
            "bằng",
            "các",
            "cách",
            "cần",
            "cho",
            "có",
            "điều",
            "được",
            "gì",
            "khi",
            "là",
            "một",
            "nào",
            "nếu",
            "những",
            "phải",
            "thì",
            "trong",
            "và",
            "với",
        }

        def tokens(text: str) -> set[str]:
            return {
                token
                for token in re.findall(r"[^\W_]+", text.casefold())
                if len(token) > 1 and token not in stop_words
            }

        question_tokens = tokens(question)
        paragraphs = [
            " ".join(paragraph.split())
            for paragraph in re.split(r"\n\s*\n", content)
            if paragraph.strip() and not paragraph.lstrip().startswith("#")
        ]
        if not paragraphs:
            return ""
        return max(
            paragraphs,
            key=lambda paragraph: (
                len(question_tokens & tokens(paragraph)),
                -abs(len(paragraph) - 350),
            ),
        )
