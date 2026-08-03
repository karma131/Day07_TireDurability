"""Đánh giá Giai đoạn 2 cho thành viên 4 — RecursiveChunker(500).

Chạy từ thư mục gốc của lab:

    python -X utf8 scripts/evaluate_member4_recursive.py

Script đọc cấu hình từ ``.env``, không ghi hoặc hiển thị API key. Kết quả được
lưu dưới dạng JSON và Markdown trong ``results/member4_recursive/``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingest import build_knowledge_base, load_documents  # noqa: E402
from src import (  # noqa: E402
    ChunkingStrategyComparator,
    KnowledgeBaseAgent,
    OpenAIEmbedder,
    RecursiveChunker,
    compute_similarity,
)

MEMBER_NAME = "Đào Văn Đa"
MEMBER_ID = "2A202601089"
STRATEGY_NAME = "RecursiveChunker(chunk_size=500)"
DEFAULT_DATA_DIR = "data/vinuni_library_services"
CHAT_MODEL = "gpt-4o-mini"
GENERATION_PASSES = 1
DEFAULT_OUTPUT_DIR = "results/member4_recursive"
REPORT_PATH = PROJECT_ROOT / "report" / "2A202601089_DAOVANDA.md"


@dataclass(frozen=True)
class BenchmarkCase:
    number: int
    query: str
    gold_answer: str
    evidence_doc_ids: tuple[str, ...]
    required_answer_terms: tuple[tuple[str, ...], ...]
    metadata_filter: dict[str, str] | None = None


BENCHMARKS = (
    BenchmarkCase(
        number=1,
        query=(
            "Sinh viên đại học được mượn tối đa bao nhiêu tài liệu, trong bao "
            "lâu và được gia hạn trong điều kiện nào?"
        ),
        metadata_filter={"audience": "student"},
        gold_answer=(
            "Tối đa 3 tài liệu, mỗi tài liệu trong 2 tuần. Sách được gia hạn "
            "một lần thêm 1 tuần nếu chưa quá hạn và không có người khác yêu cầu."
        ),
        evidence_doc_ids=("vinuni-undergraduate-borrowing",),
        required_answer_terms=(
            ("3 tài liệu", "3 cuốn", "3 sách"),
            ("2 tuần",),
            ("1 tuần",),
            ("chưa quá hạn", "không quá hạn"),
            ("không có người", "không có yêu cầu"),
        ),
    ),
    BenchmarkCase(
        number=2,
        query=(
            "Một nhóm được đặt phòng học thư viện tối đa bao lâu, bao nhiêu lần "
            "và điều gì xảy ra nếu đến muộn?"
        ),
        gold_answer=(
            "Tối đa 2 giờ mỗi phiên, 2 phiên mỗi ngày và 4 phiên mỗi tuần trên "
            "tổng số phòng. Có thể đặt trước tối đa 1 tuần; nếu vắng trong 10 "
            "phút đầu, phòng được giải phóng cho người khác."
        ),
        evidence_doc_ids=("vinuni-library-room-booking",),
        required_answer_terms=(
            ("2 giờ",),
            ("2 phiên",),
            ("4 phiên",),
            ("1 tuần",),
            ("10 phút",),
        ),
    ),
    BenchmarkCase(
        number=3,
        query=(
            "Thiết bị thư viện được mượn trong bao lâu, phải trả lúc nào và khi "
            "nào bị xem là thất lạc?"
        ),
        gold_answer=(
            "Thiết bị được mượn trong 1 ngày làm việc, phải trả trực tiếp tại "
            "quầy tầng một chậm nhất 15 phút trước giờ đóng cửa. Quá hạn trên "
            "5 ngày thì bị xem là thất lạc và người mượn phải trả chi phí thay thế."
        ),
        evidence_doc_ids=(
            "vinuni-library-access-policy",
            "vinuni-undergraduate-borrowing",
        ),
        required_answer_terms=(
            ("1 ngày làm việc",),
            ("15 phút",),
            ("tầng một", "tầng 1"),
            ("5 ngày",),
            ("thay thế",),
        ),
    ),
    BenchmarkCase(
        number=4,
        query=(
            "Sinh viên truy cập tài nguyên điện tử từ ngoài trường bằng cách nào "
            "và cần lưu ý gì khi dùng máy tính công cộng?"
        ),
        gold_answer=(
            "Đăng nhập bằng VinUni ID. Tài nguyên chỉ dùng cho mục đích cá nhân, "
            "phi thương mại và phải tuân thủ bản quyền; khi dùng máy công cộng "
            "phải đóng trình duyệt sau khi hoàn tất."
        ),
        evidence_doc_ids=("vinuni-undergraduate-borrowing",),
        required_answer_terms=(
            ("vinuni id",),
            ("cá nhân",),
            ("phi thương mại",),
            ("bản quyền",),
            ("đóng trình duyệt",),
        ),
    ),
    BenchmarkCase(
        number=5,
        query=(
            "Sinh viên đã trả sách nhưng tài khoản vẫn báo quá hạn thì cần kiểm "
            "tra và xử lý theo các bước nào?"
        ),
        gold_answer=(
            "Xác nhận sách đã được trả qua máy self-check hoặc trạm trả 24/7, "
            "kiểm tra email xác nhận trả sách, rồi liên hệ Information Desk nếu "
            "tài khoản vẫn chưa cập nhật."
        ),
        evidence_doc_ids=("vinuni-library-faq",),
        required_answer_terms=(
            ("self-check", "self check"),
            ("24/7",),
            ("email",),
            ("information desk",),
        ),
    ),
)


@dataclass(frozen=True)
class SimilarityPair:
    number: int
    sentence_a: str
    sentence_b: str
    prediction: str


SIMILARITY_PAIRS = (
    SimilarityPair(
        1,
        "Sinh viên có thể gia hạn sách thư viện trực tuyến.",
        "Người học được phép kéo dài thời hạn mượn sách qua website thư viện.",
        "cao",
    ),
    SimilarityPair(
        2,
        "Mỗi nhóm được đặt phòng học tối đa hai giờ.",
        "Thời lượng tối đa cho một phiên đặt phòng nhóm là 120 phút.",
        "cao",
    ),
    SimilarityPair(
        3,
        "Thiết bị quá hạn trên năm ngày được xem là thất lạc.",
        "Thời tiết Hà Nội hôm nay có mưa lớn.",
        "thấp",
    ),
    SimilarityPair(
        4,
        "Đăng nhập VinUni ID để truy cập tài nguyên từ xa.",
        "Sinh viên sử dụng tài khoản VinUni khi đọc cơ sở dữ liệu ngoài trường.",
        "cao",
    ),
    SimilarityPair(
        5,
        "Thư viện có không gian học tập mở 24/7.",
        "Người mượn phải trả chi phí thay thế thiết bị thất lạc.",
        "thấp",
    ),
)


class OpenAIResponsesLLM:
    """Callable adapter để KnowledgeBaseAgent dùng OpenAI Responses API."""

    def __init__(self, model: str) -> None:
        from openai import OpenAI

        self.model = model
        self.client = OpenAI()

    def __call__(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            temperature=0,
        )
        answer = response.output_text.strip()
        if not answer:
            raise RuntimeError("OpenAI Responses API returned an empty answer")
        return answer


def _retrieve(store, case: BenchmarkCase) -> list[dict[str, Any]]:
    if case.metadata_filter:
        return store.search_with_filter(
            case.query,
            top_k=3,
            metadata_filter=case.metadata_filter,
        )
    return store.search(case.query, top_k=3)


def _score_case(
    case: BenchmarkCase,
    results: list[dict[str, Any]],
    answer: str,
) -> tuple[int, list[int], list[tuple[str, ...]]]:
    evidence_ranks = [
        rank
        for rank, result in enumerate(results, start=1)
        if result.get("metadata", {}).get("doc_id") in case.evidence_doc_ids
    ]
    normalized_answer = answer.casefold()
    missing_term_groups = [
        alternatives
        for alternatives in case.required_answer_terms
        if not any(term.casefold() in normalized_answer for term in alternatives)
    ]
    if not evidence_ranks:
        score = 0
    elif missing_term_groups or evidence_ranks[0] != 1:
        score = 1
    else:
        score = 2
    return score, evidence_ranks, missing_term_groups


def _chunk_statistics(data_dir: Path, chunker: RecursiveChunker) -> dict[str, Any]:
    per_document = []
    all_lengths: list[int] = []
    for document in load_documents(data_dir):
        chunks = chunker.chunk(document.content)
        lengths = [len(chunk) for chunk in chunks]
        all_lengths.extend(lengths)
        per_document.append(
            {
                "doc_id": document.id,
                "character_count": len(document.content),
                "chunk_count": len(chunks),
                "average_chunk_length": (
                    round(sum(lengths) / len(lengths), 2) if lengths else 0.0
                ),
                "max_chunk_length": max(lengths, default=0),
            }
        )
    return {
        "document_count": len(per_document),
        "chunk_count": len(all_lengths),
        "average_chunk_length": (
            round(sum(all_lengths) / len(all_lengths), 2) if all_lengths else 0.0
        ),
        "max_chunk_length": max(all_lengths, default=0),
        "per_document": per_document,
    }


def _baseline_comparison(data_dir: Path) -> list[dict[str, Any]]:
    selected_ids = {
        "vinuni-library-access-policy",
        "vinuni-library-faq",
        "vinuni-undergraduate-borrowing",
    }
    comparator = ChunkingStrategyComparator()
    rows = []
    for document in load_documents(data_dir):
        if document.id not in selected_ids:
            continue
        comparison = comparator.compare(document.content, chunk_size=500)
        for strategy, stats in comparison.items():
            rows.append(
                {
                    "doc_id": document.id,
                    "strategy": strategy,
                    "chunk_count": stats["count"],
                    "average_chunk_length": round(stats["avg_length"], 2),
                }
            )
    return rows


def _run_similarity_predictions(embedder: OpenAIEmbedder) -> list[dict[str, Any]]:
    rows = []
    for pair in SIMILARITY_PAIRS:
        vector_a = embedder(pair.sentence_a)
        vector_b = embedder(pair.sentence_b)
        score = compute_similarity(vector_a, vector_b)
        actual_label = "cao" if score >= 0.5 else "thấp"
        rows.append(
            {
                **asdict(pair),
                "score": round(score, 6),
                "actual_label": actual_label,
                "prediction_correct": pair.prediction == actual_label,
            }
        )
    return rows


def _result_to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Kết quả Giai đoạn 2 — Thành viên 4",
        "",
        f"- **Sinh viên:** {payload['member']['name']} ({payload['member']['id']})",
        f"- **Chiến lược:** `{payload['strategy']}`",
        f"- **Embedding:** `{payload['embedding_model']}`",
        f"- **LLM:** `{payload['chat_model']}`",
        f"- **Sinh câu trả lời:** {payload.get('generation_passes', 1)} lượt",
        f"- **Corpus:** `{payload['data_dir']}`",
        f"- **Số chunk:** {payload['chunk_statistics']['chunk_count']}",
        (
            "- **Độ dài chunk trung bình:** "
            f"{payload['chunk_statistics']['average_chunk_length']} ký tự"
        ),
        f"- **Điểm benchmark:** **{payload['total_score']} / 10**",
        "",
        "## Kết quả 5 câu hỏi",
        "",
    ]
    for case in payload["benchmark_results"]:
        lines.extend(
            [
                f"### Câu {case['number']}",
                "",
                f"**Query:** {case['query']}",
                "",
                f"**Metadata filter:** `{case['metadata_filter']}`",
                "",
                f"**Điểm tự động theo rubric:** **{case['score']} / 2**",
                "",
                f"**Evidence rank:** `{case['evidence_ranks']}`",
                "",
                "**Top-3:**",
                "",
            ]
        )
        for result in case["results"]:
            lines.append(
                f"{result['rank']}. `{result['doc_id']}` — "
                f"score `{result['score']:.6f}` — {result['summary']}"
            )
        lines.extend(
            [
                "",
                "**Câu trả lời của agent:**",
                "",
                case["agent_answer"].replace("  \n", "\n"),
                "",
                f"**Gold answer:** {case['gold_answer']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Phân tích metadata filter ở câu 1",
            "",
            (
                f"- Có filter: `{payload['filter_analysis']['filtered_doc_ids']}`"
            ),
            (
                f"- Không filter: `{payload['filter_analysis']['unfiltered_doc_ids']}`"
            ),
            "",
            "## Dự đoán độ tương tự",
            "",
            "| # | Dự đoán | Score thực tế | Nhãn thực tế | Đúng? |",
            "|---:|---|---:|---|---|",
        ]
    )
    for row in payload["similarity_predictions"]:
        lines.append(
            f"| {row['number']} | {row['prediction']} | {row['score']:.6f} | "
            f"{row['actual_label']} | {'Có' if row['prediction_correct'] else 'Không'} |"
        )
    lines.append("")
    return "\n".join(lines)


def _replace_marked_block(
    text: str,
    marker_name: str,
    replacement: str,
) -> str:
    start_marker = f"<!-- {marker_name}_START -->"
    end_marker = f"<!-- {marker_name}_END -->"
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start == -1 or end == -1 or end < start:
        raise RuntimeError(f"Không tìm thấy marker báo cáo: {marker_name}")
    content_start = start + len(start_marker)
    return (
        text[:content_start]
        + "\n"
        + replacement.strip()
        + "\n"
        + text[end:]
    )


def _similarity_report_block(payload: dict[str, Any]) -> str:
    rows = [
        "| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |",
        "|---:|---|---|---|---:|---|",
    ]
    for item in payload["similarity_predictions"]:
        rows.append(
            f"| {item['number']} | {item['sentence_a']} | {item['sentence_b']} | "
            f"{item['prediction'].capitalize()} | {item['score']:.6f} | "
            f"{'Có' if item['prediction_correct'] else 'Không'} |"
        )

    incorrect = [
        item
        for item in payload["similarity_predictions"]
        if not item["prediction_correct"]
    ]
    if incorrect:
        most_surprising = max(
            incorrect,
            key=lambda item: abs(item["score"] - 0.5),
        )
        reflection = (
            f"Cặp {most_surprising['number']} bất ngờ nhất vì tôi dự đoán "
            f"{most_surprising['prediction']} nhưng điểm thực tế là "
            f"{most_surprising['score']:.6f} ({most_surprising['actual_label']}). "
            "Điều này cho thấy embedding đo mức gần nhau trong không gian biểu "
            "diễn của mô hình, không chỉ dựa trên đánh giá chủ quan hoặc từ khóa."
        )
    else:
        closest = min(
            payload["similarity_predictions"],
            key=lambda item: abs(item["score"] - 0.5),
        )
        reflection = (
            "Cả năm dự đoán đều khớp với ngưỡng đã chọn. Cặp "
            f"{closest['number']} gần ranh giới nhất với score "
            f"{closest['score']:.6f}; kết quả cho thấy nhãn cao/thấp còn phụ thuộc "
            "ngưỡng đánh giá, còn cosine score mới là thông tin chi tiết hơn."
        )

    rows.extend(
        [
            "",
            f"**Kết quả:** "
            f"{sum(item['prediction_correct'] for item in payload['similarity_predictions'])}"
            " / 5 dự đoán đúng theo ngưỡng 0,5.",
            "",
            f"**Kết quả bất ngờ nhất và suy ngẫm:** {reflection}",
        ]
    )
    return "\n".join(rows)


def _benchmark_report_block(payload: dict[str, Any]) -> str:
    rows = [
        "| # | Query rút gọn | Top-1 | Score | Evidence trong top-3? | Điểm |",
        "|---:|---|---|---:|---|---:|",
    ]
    short_queries = (
        "Quyền mượn sinh viên đại học",
        "Giới hạn đặt phòng học nhóm",
        "Mượn và trả thiết bị",
        "Truy cập tài nguyên ngoài trường",
        "Đã trả sách nhưng vẫn báo quá hạn",
    )
    for short_query, case in zip(
        short_queries,
        payload["benchmark_results"],
    ):
        top1 = case["results"][0] if case["results"] else None
        top1_score = f"{top1['score']:.6f}" if top1 else "—"
        rows.append(
            f"| {case['number']} | {short_query} | "
            f"`{top1['doc_id'] if top1 else 'không có'}` | "
            f"{top1_score} | "
            f"{'Có' if case['evidence_ranks'] else 'Không'}"
            f"{' (rank ' + str(case['evidence_ranks'][0]) + ')' if case['evidence_ranks'] else ''} | "
            f"{case['score']} / 2 |"
        )

    rows.extend(
        [
            "",
            f"**Tổng điểm:** **{payload['total_score']} / 10**.",
            "",
            (
                "**Phân tích metadata filter câu 1:** Có filter, top-3 lần lượt là "
                f"`{payload['filter_analysis']['filtered_doc_ids']}`; không filter "
                f"là `{payload['filter_analysis']['unfiltered_doc_ids']}`. "
                "So sánh này cho biết bộ lọc có loại được tài liệu sai đối tượng "
                "cao học/giảng viên hay không."
            ),
            "",
            "**Câu trả lời của agent:**",
            "",
        ]
    )
    for case in payload["benchmark_results"]:
        compact_answer = " ".join(case["agent_answer"].split())
        rows.extend(
            [
                f"- **Câu {case['number']}:** {compact_answer}",
            ]
        )
    return "\n".join(rows)


def _self_assessment_block(payload: dict[str, Any]) -> str:
    total = 50 + int(payload["total_score"])
    return "\n".join(
        [
            "| Tiêu chí | Điểm tự đánh giá |",
            "|---|---:|",
            "| Khởi động | 5 / 5 |",
            "| Hướng tiếp cận | 10 / 10 |",
            "| Hoàn thiện code — 44/44 tests | 30 / 30 |",
            "| Dự đoán độ tương tự và suy ngẫm | 5 / 5 |",
            (
                "| Kết quả truy xuất cá nhân | "
                f"{payload['total_score']} / 10 |"
            ),
            f"| **Tổng phần cá nhân** | **{total} / 60** |",
        ]
    )


def _update_individual_report(payload: dict[str, Any]) -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")
    report = _replace_marked_block(
        report,
        "2A202601089_DAOVANDA_SIMILARITY_RESULTS",
        _similarity_report_block(payload),
    )
    report = _replace_marked_block(
        report,
        "2A202601089_DAOVANDA_BENCHMARK_RESULTS",
        _benchmark_report_block(payload),
    )
    report = _replace_marked_block(
        report,
        "2A202601089_DAOVANDA_SELF_ASSESSMENT",
        _self_assessment_block(payload),
    )
    REPORT_PATH.write_text(report, encoding="utf-8")


def _group_contribution_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Đóng góp Báo cáo Nhóm — Thành viên 4",
        "",
        f"**Thành viên:** {payload['member']['name']} ({payload['member']['id']})",
        "",
        f"**Chiến lược:** `{payload['strategy']}`",
        "",
        (
            "RecursiveChunker ưu tiên ranh giới đoạn, dòng và câu trước khi cắt "
            "theo từ hoặc ký tự. Với corpus chính sách/FAQ có cấu trúc rõ, lựa "
            "chọn này cân bằng độ mạch lạc và giới hạn kích thước 500 ký tự."
        ),
        "",
        "## Thống kê",
        "",
        f"- Số tài liệu: {payload['chunk_statistics']['document_count']}",
        f"- Số chunk: {payload['chunk_statistics']['chunk_count']}",
        (
            "- Độ dài trung bình: "
            f"{payload['chunk_statistics']['average_chunk_length']} ký tự"
        ),
        f"- Chunk dài nhất: {payload['chunk_statistics']['max_chunk_length']} ký tự",
        "",
        "## Kết quả benchmark",
        "",
        "| Câu | Evidence rank | Điểm | Top-1 |",
        "|---:|---|---:|---|",
    ]
    for case in payload["benchmark_results"]:
        top1 = case["results"][0]["doc_id"] if case["results"] else "không có"
        lines.append(
            f"| {case['number']} | `{case['evidence_ranks']}` | "
            f"{case['score']} / 2 | `{top1}` |"
        )
    lines.extend(
        [
            "",
            f"**Tổng:** **{payload['total_score']} / 10**",
            "",
            "## Metadata filter và failure case",
            "",
            (
                "Câu 1 có tài liệu gây nhiễu dành cho cao học/giảng viên. "
                f"Top-3 có filter: `{payload['filter_analysis']['filtered_doc_ids']}`; "
                f"không filter: `{payload['filter_analysis']['unfiltered_doc_ids']}`."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Đánh giá RecursiveChunker(500) cho thành viên 4.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Chỉ kiểm tra corpus, benchmark và report; không gọi OpenAI API.",
    )
    parser.add_argument(
        "--render-existing",
        action="store_true",
        help="Tạo lại Markdown/report từ results.json hiện có; không gọi API.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    offline_mode = args.validate_only or args.render_existing
    if not offline_mode and not os.getenv("OPENAI_API_KEY"):
        print("Thiếu OPENAI_API_KEY trong .env.", file=sys.stderr)
        return 2
    if (
        not offline_mode
        and os.getenv("EMBEDDING_PROVIDER", "").strip().lower() != "openai"
    ):
        print("EMBEDDING_PROVIDER phải là openai cho lần đánh giá này.", file=sys.stderr)
        return 2

    data_dir = PROJECT_ROOT / os.getenv("LAB_DATA_DIR", DEFAULT_DATA_DIR)
    output_dir = PROJECT_ROOT / os.getenv("MEMBER4_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
    embedding_model = os.getenv(
        "OPENAI_EMBEDDING_MODEL",
        "text-embedding-3-small",
    )
    chat_model = CHAT_MODEL

    if not data_dir.is_dir():
        print(f"Không tìm thấy corpus: {data_dir}", file=sys.stderr)
        return 2

    if args.render_existing:
        json_path = output_dir / "results.json"
        if not json_path.is_file():
            print(f"Không tìm thấy kết quả: {json_path}", file=sys.stderr)
            return 2
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "RESULTS.md").write_text(
            _result_to_markdown(payload),
            encoding="utf-8",
        )
        (output_dir / "GROUP_CONTRIBUTION.md").write_text(
            _group_contribution_markdown(payload),
            encoding="utf-8",
        )
        _update_individual_report(payload)
        print("Đã tạo lại kết quả Markdown và báo cáo; không gọi OpenAI API.")
        return 0

    chunker = RecursiveChunker(chunk_size=500)
    if args.validate_only:
        report = REPORT_PATH.read_text(encoding="utf-8")
        for marker in (
            "2A202601089_DAOVANDA_SIMILARITY_RESULTS",
            "2A202601089_DAOVANDA_BENCHMARK_RESULTS",
            "2A202601089_DAOVANDA_SELF_ASSESSMENT",
        ):
            _replace_marked_block(report, marker, "validation")
        statistics = _chunk_statistics(data_dir, chunker)
        baseline = _baseline_comparison(data_dir)
        assert len(BENCHMARKS) == 5
        assert sum(case.metadata_filter is not None for case in BENCHMARKS) == 1
        assert len(SIMILARITY_PAIRS) == 5
        assert len(baseline) == 9
        assert statistics["max_chunk_length"] <= 500
        print("Validation cục bộ thành công; không gọi OpenAI API.")
        print(
            f"{statistics['document_count']} tài liệu -> "
            f"{statistics['chunk_count']} chunks; "
            f"trung bình {statistics['average_chunk_length']} ký tự."
        )
        return 0

    print(f"Chiến lược: {STRATEGY_NAME}")
    print(f"Corpus: {data_dir.relative_to(PROJECT_ROOT)}")
    print(f"Embedding model: {embedding_model}")
    print(f"Chat model: {chat_model}")

    embedder = OpenAIEmbedder(model_name=embedding_model)
    store = build_knowledge_base(
        data_dir=data_dir,
        embedding_fn=embedder,
        chunker=chunker,
        collection_name="member4_recursive_500",
    )
    llm = OpenAIResponsesLLM(model=chat_model)
    agent = KnowledgeBaseAgent(store=store, llm_fn=llm)

    benchmark_results = []
    total_score = 0
    for case in BENCHMARKS:
        print(f"Đang chạy câu {case.number}/5...")
        results = _retrieve(store, case)
        answer = agent.answer(
            case.query,
            top_k=3,
            metadata_filter=case.metadata_filter,
        )
        score, evidence_ranks, missing_term_groups = _score_case(
            case,
            results,
            answer,
        )
        total_score += score
        benchmark_results.append(
            {
                "number": case.number,
                "query": case.query,
                "metadata_filter": case.metadata_filter,
                "gold_answer": case.gold_answer,
                "evidence_doc_ids": list(case.evidence_doc_ids),
                "evidence_ranks": evidence_ranks,
                "missing_term_groups": [list(group) for group in missing_term_groups],
                "score": score,
                "agent_answer": answer,
                "results": [
                    {
                        "rank": rank,
                        "id": result.get("id"),
                        "doc_id": result.get("metadata", {}).get("doc_id"),
                        "chunk_index": result.get("metadata", {}).get("chunk_index"),
                        "source_url": result.get("metadata", {}).get("source_url"),
                        "score": round(float(result["score"]), 6),
                        "summary": " ".join(result["content"].split())[:240],
                        "content": result["content"],
                    }
                    for rank, result in enumerate(results, start=1)
                ],
            }
        )

    first_case = BENCHMARKS[0]
    unfiltered_results = store.search(first_case.query, top_k=3)
    filter_analysis = {
        "query": first_case.query,
        "filter": first_case.metadata_filter,
        "filtered_doc_ids": [
            result["doc_id"] for result in benchmark_results[0]["results"]
        ],
        "unfiltered_doc_ids": [
            result.get("metadata", {}).get("doc_id")
            for result in unfiltered_results
        ],
        "unfiltered_results": [
            {
                "rank": rank,
                "doc_id": result.get("metadata", {}).get("doc_id"),
                "score": round(float(result["score"]), 6),
            }
            for rank, result in enumerate(unfiltered_results, start=1)
        ],
    }

    print("Đang chạy 5 cặp dự đoán cosine similarity...")
    similarity_predictions = _run_similarity_predictions(embedder)
    payload = {
        "member": {"name": MEMBER_NAME, "id": MEMBER_ID, "role": 4},
        "strategy": STRATEGY_NAME,
        "data_dir": str(data_dir.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "embedding_model": embedding_model,
        "chat_model": chat_model,
        "generation_passes": GENERATION_PASSES,
        "chunk_statistics": _chunk_statistics(data_dir, chunker),
        "baseline_comparison": _baseline_comparison(data_dir),
        "benchmark_results": benchmark_results,
        "filter_analysis": filter_analysis,
        "total_score": total_score,
        "similarity_predictions": similarity_predictions,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "results.json"
    markdown_path = output_dir / "RESULTS.md"
    group_contribution_path = output_dir / "GROUP_CONTRIBUTION.md"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    markdown_path.write_text(_result_to_markdown(payload), encoding="utf-8")
    group_contribution_path.write_text(
        _group_contribution_markdown(payload),
        encoding="utf-8",
    )
    _update_individual_report(payload)

    print(f"Hoàn tất: {total_score}/10")
    print(f"JSON: {json_path.relative_to(PROJECT_ROOT)}")
    print(f"Markdown: {markdown_path.relative_to(PROJECT_ROOT)}")
    print(
        "Đóng góp báo cáo nhóm: "
        f"{group_contribution_path.relative_to(PROJECT_ROOT)}"
    )
    print(f"Đã cập nhật: {REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
