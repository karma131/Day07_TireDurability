#!/usr/bin/env python3
"""Run the five K3 benchmark queries for Person 1's fixed-size baseline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingest import build_knowledge_base  # noqa: E402
from src import FixedSizeChunker, LocalEmbedder  # noqa: E402


DATA_DIR = PROJECT_ROOT / "data" / "vinuni_library_services"
OUTPUT_PATH = PROJECT_ROOT / "report" / "benchmark_person1_results.json"

BENCHMARKS = [
    {
        "query": "Sinh viên đại học được mượn tối đa bao nhiêu tài liệu, trong bao lâu và được gia hạn trong điều kiện nào?",
        "metadata_filter": {"audience": "student"},
        "relevant_doc_ids": {"vinuni-undergraduate-borrowing"},
        "gold_answer": "Tối đa 3 tài liệu trong 2 tuần; gia hạn một lần thêm 1 tuần nếu chưa quá hạn và không có người khác yêu cầu.",
    },
    {
        "query": "Một nhóm được đặt phòng học thư viện tối đa bao lâu, bao nhiêu lần và điều gì xảy ra nếu đến muộn?",
        "metadata_filter": None,
        "relevant_doc_ids": {"vinuni-library-room-booking", "vinuni-library-access-policy"},
        "gold_answer": "Tối đa 2 giờ/phiên, 2 phiên/ngày và 4 phiên/tuần; vắng trong 10 phút đầu thì phòng được giải phóng.",
    },
    {
        "query": "Thiết bị thư viện được mượn trong bao lâu, phải trả lúc nào và khi nào bị xem là thất lạc?",
        "metadata_filter": None,
        "relevant_doc_ids": {"vinuni-library-access-policy", "vinuni-undergraduate-borrowing"},
        "gold_answer": "Mượn trong 1 ngày làm việc, trả trực tiếp tại quầy tầng một trước giờ đóng cửa 15 phút; quá hạn trên 5 ngày được xem là thất lạc.",
    },
    {
        "query": "Sinh viên truy cập tài nguyên điện tử từ ngoài trường bằng cách nào và cần lưu ý gì khi dùng máy tính công cộng?",
        "metadata_filter": None,
        "relevant_doc_ids": {"vinuni-undergraduate-borrowing"},
        "gold_answer": "Đăng nhập bằng VinUni ID, chỉ dùng cho mục đích cá nhân và phi thương mại, đồng thời đóng trình duyệt sau khi dùng máy công cộng.",
    },
    {
        "query": "Sinh viên đã trả sách nhưng tài khoản vẫn báo quá hạn thì cần kiểm tra và xử lý theo các bước nào?",
        "metadata_filter": None,
        "relevant_doc_ids": {"vinuni-library-faq"},
        "gold_answer": "Xác nhận đã trả qua máy self-check hoặc trạm trả 24/7, kiểm tra email xác nhận, rồi liên hệ Information Desk nếu tài khoản chưa cập nhật.",
    },
]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("Loading multilingual embedding model...")
    embedder = LocalEmbedder()
    store = build_knowledge_base(
        data_dir=DATA_DIR,
        embedding_fn=embedder,
        chunker=FixedSizeChunker(chunk_size=500, overlap=50),
        collection_name="person1_baseline",
    )

    output: dict = {
        "strategy": "FixedSizeChunker(chunk_size=500, overlap=50)",
        "embedding_model": embedder._backend_name,
        "collection_size": store.get_collection_size(),
        "queries": [],
    }

    relevant_count = 0
    for number, benchmark in enumerate(BENCHMARKS, start=1):
        metadata_filter = benchmark["metadata_filter"]
        if metadata_filter:
            results = store.search_with_filter(
                benchmark["query"],
                top_k=3,
                metadata_filter=metadata_filter,
            )
        else:
            results = store.search(benchmark["query"], top_k=3)

        serialized_results = []
        for rank, result in enumerate(results, start=1):
            metadata = result.get("metadata") or {}
            serialized_results.append(
                {
                    "rank": rank,
                    "score": round(float(result["score"]), 4),
                    "doc_id": metadata.get("doc_id"),
                    "chunk_index": metadata.get("chunk_index"),
                    "audience": metadata.get("audience"),
                    "content": " ".join(result["content"].split()),
                }
            )

        relevant_in_top3 = any(
            result["doc_id"] in benchmark["relevant_doc_ids"]
            for result in serialized_results
        )
        relevant_count += int(relevant_in_top3)
        output["queries"].append(
            {
                "number": number,
                "query": benchmark["query"],
                "metadata_filter": metadata_filter,
                "gold_answer": benchmark["gold_answer"],
                "relevant_in_top3": relevant_in_top3,
                "results": serialized_results,
            }
        )

        top1 = serialized_results[0] if serialized_results else None
        print("\n" + "=" * 80)
        print(f"CÂU {number}: {benchmark['query']}")
        print(f"Filter: {metadata_filter}")
        print(f"Relevant in top-3: {'YES' if relevant_in_top3 else 'NO'}")
        if top1:
            print(
                f"Top-1: score={top1['score']:.4f}, "
                f"doc_id={top1['doc_id']}, chunk_index={top1['chunk_index']}"
            )
        for result in serialized_results:
            print(
                f"  Top-{result['rank']}: {result['score']:.4f} | "
                f"{result['doc_id']} | chunk {result['chunk_index']}"
            )

    output["relevant_queries_in_top3"] = relevant_count
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nTop-3 relevant: {relevant_count}/5")
    print(f"Full UTF-8 results saved to: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
