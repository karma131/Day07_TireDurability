# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Hoàng Vinh Phong  
**Mã sinh viên:** 2A202601265  
**Nhóm:** K3 Library Services  
**Ngày:** 03/08/2026  

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao có nghĩa là góc giữa hai vector văn bản trong không gian đa chiều rất nhỏ (hướng gần như trùng nhau), thể hiện hai đoạn văn bản có sự tương đồng lớn về mặt ngữ nghĩa, không phụ thuộc vào độ dài ngắn của văn bản.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên có thể gia hạn sách trực tuyến trên website thư viện."
- Câu B: "Người dùng có thể gia hạn tài liệu mượn qua tài khoản cá nhân trực tuyến."
- Tại sao tương đồng: Cả hai câu đều nói về việc gia hạn sách/tài liệu thư viện qua kênh trực tuyến.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Sinh viên có thể gia hạn sách trực tuyến trên website thư viện."
- Câu B: "Hệ thống điều hòa tại phòng tự học hoạt động từ 8 giờ sáng."
- Tại sao khác: Một câu nói về dịch vụ gia hạn thư viện, một câu nói về cơ sở vật chất hệ thống điều hòa.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid bị ảnh hưởng mạnh bởi độ dài văn bản (chuẩn độ dài của vector). Hai văn bản cùng chủ đề nhưng một văn bản dài (chứa nhiều từ) và một văn bản ngắn sẽ có khoảng cách Euclid rất lớn. Trong khi đó, Cosine Similarity chỉ đo góc giữa hai vector, giúp loại bỏ ảnh hưởng của độ dài văn bản và phản ánh chính xác sự tương đồng ngữ nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*  
> Bước nhảy giữa các chunk: `step = chunk_size - overlap = 500 - 50 = 450`  
> Công thức: `số lượng chunk = làm_tròn_lên((10,000 - 50) / 450) = làm_tròn_lên(9,950 / 450) = làm_tròn_lên(22.11)`  
> *Đáp án:* **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi `overlap = 100`, bước nhảy `step = 500 - 100 = 400`.  
> Số lượng chunk mới: `làm_tròn_lên((10,000 - 100) / 400) = làm_tròn_lên(9,900 / 400) = làm_tròn_lên(24.75) = 25 chunks` (tăng thêm 2 chunks).  
> Muốn tăng độ chồng chéo để đảm bảo ngữ cảnh nằm ở ranh giới giữa hai chunk kế tiếp không bị mất đứt đoạn, giúp việc truy xuất tìm thấy đúng thông tin nằm ở giáp ranh.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Chiến lược cá nhân của tôi là **`SentenceChunker` (`max_sentences_per_chunk=3`)**.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng biểu thức chính quy `re.split(r"(?<=[.!?])\s+", text)` với kỹ thuật lookbehind để tách câu tại các dấu kết thúc (`. `, `! `, `? `). Tách xong tiến hành strip khoảng trắng và gom cứ 3 câu liên tiếp vào một chunk string. Cách này đảm bảo không bao giờ bị ngắt đôi một câu ngữ pháp.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán chia đệ quy thử nghiệm lần lượt danh sách dấu phân cách ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Nếu đoạn văn bản hiện tại nhỏ hơn `chunk_size` thì trả về ngay (base case). Nếu danh sách separators rỗng hoặc không phân tách được tiếp thì chia cố định theo chiều dài `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Trong `add_documents`, mỗi document được gọi qua `_make_record` để nhúng nội dung thành vector và lưu thành một dictionary gồm `id`, `content`, `metadata`, `embedding`. Trong `search`, tính tích vô hướng (`_dot`) giữa query embedding với từng record, sắp xếp giảm dần theo điểm `score` và trả về `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` thực hiện lọc dữ liệu trước (pre-filtering) bằng cách kiểm tra các cặp key-value trong `metadata_filter` trên tập `_store`, sau đó mới gọi hàm tính điểm tương đồng. `delete_document` lọc bỏ các bản ghi trùng `doc_id` hoặc `metadata['doc_id'] == doc_id` và trả về `True` nếu có bản ghi bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Phương thức `answer` gọi `store.search` để lấy ra `top_k` chunks liên quan nhất, nối các nội dung chunk thành một chuỗi ngữ cảnh (context), sau đó tạo prompt theo mẫu `Context:\n{context}\n\nQuestion: {question}\nAnswer:` và truyền vào hàm `llm_fn`.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.7, pytest-9.1.1, pluggy-1.6.0
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED

============================= 42 passed in 0.04s ==============================
```

**Số lượng bài test vượt qua (pass):** **42** / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Mượn sách thư viện" | "Gia hạn tài liệu mượn" | Cao | 0.78 | Đúng |
| 2 | "Đặt phòng học nhóm qua Outlook" | "Hủy lịch đặt phòng khi muộn 10 phút" | Cao | 0.65 | Đúng |
| 3 | "Thời hạn mượn thiết bị" | "Lập trình Python cơ bản" | Thấp | -0.02 | Đúng |
| 4 | "Mượn sách sinh viên đại học" | "Quyền mượn học viên cao học" | Cao | 0.71 | Đúng |
| 5 | "Không gian 24/7" | "Máy in tầng một" | Thấp | 0.12 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp số 2 ("Đặt phòng học nhóm" và "Hủy lịch đặt") cho điểm thực tế cao hơn dự kiến ban đầu (0.65). Điều này cho thấy mô hình embedding phản ánh đúng ngữ cảnh chung của cùng một nghiệp vụ (quy trình đặt phòng thư viện) thay vì chỉ so sánh từng từ rời rạc.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy 5 câu hỏi đánh giá của nhóm trên bộ dữ liệu `data/vinuni_library_services` sử dụng chiến lược **`SentenceChunker` (`max_sentences_per_chunk=3`)**:

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên đại học được mượn tối đa bao nhiêu tài liệu và trong thời hạn bao lâu? | `vinuni-undergraduate-borrowing::chunk_3` (Top-2: `chunk_0` mượn 3 tài liệu/2 tuần). | 0.2426 | Có (trong Top-3) | Sinh viên đại học được mượn tối đa 3 tài liệu trong 2 tuần, gia hạn 1 lần 1 tuần. |
| 2 | Quy định và cách đặt phòng học nhóm tại thư viện qua Outlook như thế nào? | `vinuni-library-room-booking::chunk_3`: Email xác nhận lịch đặt phòng qua Outlook. | -0.0056 | Có (Top-1) | Đặt phòng qua Outlook bằng New Meeting, chọn Rooms, tối đa 2h/phiên. |
| 3 | Làm thế nào để xem hạn trả sách và gia hạn sách trực tuyến? | `vinuni-library-faq::chunk_3` (Top-2: `chunk_1` chọn RENEW ALL hoặc LOAN > RENEW). | 0.0305 | Có (trong Top-3) | Đăng nhập website thư viện, mở My Library Account và chọn RENEW. |
| 4 | Học viên cao học và giảng viên được mượn tối đa bao nhiêu tài liệu? | `vinuni-graduate-faculty-borrowing::chunk_3` (Top-2: `chunk_0` mượn 5 tài liệu/1 tháng). | 0.1050 | Có (trong Top-3) | Học viên cao học mượn 5 tài liệu/1 tháng; Giảng viên mượn 5 tài liệu/6 tháng. |
| 5 | Thời hạn mượn thiết bị thư viện là bao lâu và quy định xử lý khi quá hạn trên 5 ngày? | `vinuni-library-room-booking::chunk_2` (khi chưa lọc `category: borrowing`). | 0.3381 | Có (khi kèm filter) | Mượn thiết bị 1 ngày làm việc, quá hạn 5 ngày tính thất lạc và bồi thường. |

### Phân Tích Lỗi Cá Nhân (Failure Analysis)

- **Trường hợp thử nghiệm lỗi của `SentenceChunker`:** 
  - Do `SentenceChunker` chia cố định cứ 3 câu/chunk mà không quan tâm ranh giới các tiêu đề mục (`##`), nên câu chứa định mức mượn (đáp án chuẩn) đôi khi bị rớt xuống **Top-2** thay vì đứng ở Top-1 (ví dụ ở Câu 1 và Câu 4).
  - Ở Câu 5 khi không dùng metadata filter `category: borrowing`, `SentenceChunker` trả về chunk phòng học nhóm ở Top-1 do từ khóa "quá hạn", "10 phút" có điểm tương đồng từ vựng cao.
- **Bài học kinh nghiệm:** `SentenceChunker` giữ trọn vẹn câu ngữ pháp tốt hơn `FixedSizeChunker`, nhưng cần kết hợp `metadata_filter` để đưa chunk chứa thông tin chính xác lên Top-1.

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5** / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Nhóm bạn sử dụng `RecursiveChunker` hoặc `CustomHeadingChunker` giúp các chunk bám sát cấu trúc tiêu đề `##` của văn bản quy định, giúp đưa chunk chứa đáp án chính xác đứng ngay ở vị trí Top-1 tốt hơn so với gom 3 câu thuần túy.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
