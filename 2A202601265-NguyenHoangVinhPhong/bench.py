from __future__ import annotations

import os
from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent
from src.chunking import RecursiveChunker
from src.embeddings import _mock_embed, LocalEmbedder

DATA_DIR = os.getenv("LAB_DATA_DIR", "data/vinuni_library_services")


def get_embedder():
    provider = os.getenv("EMBEDDING_PROVIDER", "mock").strip().lower()
    if provider == "local":
        try:
            return LocalEmbedder()
        except Exception:
            return _mock_embed
    return _mock_embed


def main():
    embedder = get_embedder()
    # 1. Chọn chiến lược cá nhân: SentenceChunker (max_sentences_per_chunk=3)
    from src.chunking import SentenceChunker
    chunker = SentenceChunker(max_sentences_per_chunk=3)
    print(f"=== Running Benchmark Suite with Strategy: {chunker.__class__.__name__} (max_sentences_per_chunk=3) ===")
    print(f"Thư mục dữ liệu (Corpus): {DATA_DIR}")

    # 2. Nạp toàn bộ corpus bằng ingest.build_knowledge_base
    store = build_knowledge_base(DATA_DIR, embedding_fn=embedder, chunker=chunker)
    print(f"Đã nạp {store.get_collection_size()} chunk vào EmbeddingStore.\n")

    # 3. Chạy 5 benchmark query đã chốt
    agent = KnowledgeBaseAgent(store=store, llm_fn=lambda prompt: "[DEMO LLM] Answer based on retrieved context.")

    queries = [
        (
            "Sinh viên đại học được mượn tối đa bao nhiêu tài liệu và trong thời hạn bao lâu?",
            "Sinh viên đại học được mượn tối đa 3 tài liệu trong 2 tuần (gia hạn 1 lần 1 tuần).",
            {"audience": "student", "category": "borrowing"},
        ),
        (
            "Quy định và các bước đặt phòng học nhóm tại thư viện qua Microsoft Outlook như thế nào?",
            "Mở Calendar trong Outlook > New Meeting > Rooms. Tối đa 2h/phiên, 2 phiên/ngày cho nhóm từ 2 người.",
            {"category": "room-booking"},
        ),
        (
            "Làm thế nào để xem hạn trả sách và gia hạn sách trực tuyến?",
            "Đăng nhập website thư viện, mở My Library Account và chọn RENEW ALL hoặc LOAN > RENEW.",
            {"category": "self-service-help"},
        ),
        (
            "Học viên cao học và giảng viên được mượn tối đa bao nhiêu tài liệu?",
            "Cao học mượn 5 tài liệu/1 tháng (gia hạn 1 lần 2 tuần); Giảng viên mượn 5 tài liệu/6 tháng.",
            {"audience": "faculty"},
        ),
        (
            "Thời hạn mượn thiết bị thư viện là bao lâu và quy định xử lý khi quá hạn trên 5 ngày?",
            "Mượn 1 ngày làm việc, trả trước 15 phút giờ đóng cửa. Quá hạn trên 5 ngày tính là thất lạc và bồi thường chi phí.",
            None,
        ),
    ]

    for index, (q_text, gold_ans, meta_filter) in enumerate(queries, 1):
        print(f"--------------------------------------------------")
        print(f"Query {index}: {q_text}")
        print(f"Gold Answer: {gold_ans}")
        print(f"Metadata Filter: {meta_filter}")

        results = store.search_with_filter(q_text, top_k=3, metadata_filter=meta_filter)
        print(f"Top-{len(results)} Chunk truy xuất được:")
        for idx, res in enumerate(results, 1):
            source = res["metadata"].get("source", res["metadata"].get("doc_id", "N/A"))
            print(f"  [{idx}] score={res['score']:.4f} | id={res['id']} | source={source}")
            print(f"      Preview: {res['content'][:120].replace(chr(10), ' ')}...")

        ans = agent.answer(q_text, top_k=3)
        print(f"Agent Answer: {ans}\n")


if __name__ == "__main__":
    main()
