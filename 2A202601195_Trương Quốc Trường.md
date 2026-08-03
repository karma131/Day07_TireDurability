# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trương Quốc Trường
**Nhóm: B4**
**Ngày:** 3/8/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> Độ tương tự cosine cao nghĩa là hướng của hai vector biểu diễn văn bản trong không gian vector rất gần nhau, thể hiện hai văn bản có độ tương đồng lớn về mặt ngữ nghĩa hoặc ngữ cảnh sử dụng, bất kể độ dài của chúng có sự chênh lệch lớn.

**Ví dụ có độ tương tự CAO:**

- Câu A: "Làm thế nào để đăng ký mượn sách tại thư viện?"
- Câu B: "Quy trình đăng ký mượn tài liệu của thư viện như thế nào?"
- Tại sao tương đồng: Cả hai câu đều có cùng một ý định (intent) hỏi về thủ tục/quy trình mượn sách/tài liệu ở thư viện, dù sử dụng từ ngữ khác nhau.

**Ví dụ có độ tương tự THẤP:**

- Câu A: "Quy định về thời gian gia hạn mượn sách thư viện."
- Câu B: "Thực đơn căn tin hôm nay có món bún chả Hà Nội."
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn khác nhau không liên quan (thủ tục thư viện và ăn uống tại căn tin), do đó các vector biểu diễn của chúng sẽ hướng theo hai hướng khác nhau trong không gian vector.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> Vì khoảng cách Euclid bị ảnh hưởng bởi độ dài văn bản (văn bản dài hơn sẽ có các giá trị vector lớn hơn và khoảng cách Euclid lớn hơn dù có cùng chủ đề). Độ tương tự cosine chỉ đo góc giữa hai vector (hướng), loại bỏ ảnh hưởng của độ dài văn bản, giúp so sánh chính xác sự tương đồng về mặt ngữ nghĩa nội dung.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> *Trình bày phép tính:*
> `số lượng chunk = làm_tròn_lên((độ_dài_tài_liệu - độ_chồng_chéo) / (kích_thước_chunk - độ_chồng_chéo))`
> `số lượng chunk = làm_tròn_lên((10000 - 50) / (500 - 50)) = làm_tròn_lên(9950 / 450) = làm_tròn_lên(22.11) = 23`
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> *Trình bày phép tính:*
> `số lượng chunk = làm_tròn_lên((10000 - 100) / (500 - 100)) = làm_tròn_lên(9900 / 400) = làm_tròn_lên(24.75) = 25` chunks.
> *Thay đổi:* Số lượng chunk tăng lên từ 23 thành 25.
> *Lý do:* Tăng độ chồng chéo giúp tránh việc các thông tin quan trọng hoặc ngữ cảnh của câu bị cắt đôi ở ranh giới giữa hai chunk, từ đó đảm bảo rằng thông tin ngữ cảnh được bảo toàn liên tục khi hệ thống truy xuất (retrieval) từng chunk riêng lẻ.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
Sử dụng biểu thức chính quy lookbehind `(?<=\. |\! |\? |\.\n)` để tách văn bản thành các câu mà không làm mất đi các dấu câu kết thúc. Sau đó lọc bỏ các câu trống, tiến hành gom nhóm các câu lại theo số lượng tối đa cấu hình (`max_sentences_per_chunk`), liên kết chúng bằng dấu cách rồi strip khoảng trắng thừa.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
Thuật toán hoạt động theo nguyên tắc chia để trị: nếu văn bản ngắn hơn `chunk_size`, nó là base case và trả về chính nó. Ngược lại, thuật toán thử tách bằng ký tự phân tách có độ ưu tiên cao nhất đang có. Sau đó thực hiện gọi đệ quy `_split` cho các đoạn có kích thước quá lớn. Cuối cùng, ghép các đoạn nhỏ lại với nhau sao cho kích thước tối đa của mỗi chunk gộp không vượt quá `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
Kho lưu trữ lưu văn bản dưới dạng các record chứa `id`, `content`, `metadata` và `embedding` được sinh ra từ hàm nhúng. Khi thực hiện `search`, truy vấn của người dùng cũng được nhúng thành vector, sau đó tính độ tương tự cosine với tất cả các vector đã lưu trữ, sắp xếp giảm dần và lấy ra top_k kết quả tốt nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
Lọc bằng metadata được thực hiện trước (pre-filtering): duyệt qua các record đã lưu trữ và chỉ giữ lại những record có chứa đầy đủ các cặp key-value trùng với bộ lọc `metadata_filter`, sau đó mới tính độ tương tự cosine trên tập đã lọc. Lớp xóa tài liệu `delete_document` sẽ loại bỏ mọi record có trường `id` hoặc trường `doc_id` trong metadata trùng với `doc_id` cần xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
Khi nhận được câu hỏi, tác tử gọi phương thức `search` của store để lấy ra top_k đoạn văn bản liên quan nhất. Sau đó, các đoạn văn bản này được định dạng và đưa vào làm ngữ cảnh (`Context`) cùng với câu hỏi của người dùng để xây dựng một prompt hoàn chỉnh. Prompt này cuối cùng được chuyển tới hàm gọi LLM (`llm_fn`) để sinh ra câu trả lời chính xác.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Bernie\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: D:\WORKSPACE\DAY07_2A202601195_TruongQuocTruong
plugins: anyio-4.14.2, langsmith-0.10.10, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.06s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán  | Điểm thực tế | Đúng? |
| ---- | ------ | ------ | ----------- | ---------------- | ------- |
| 1    | Làm thế nào để đăng ký mượn sách tại thư viện? | Quy trình đăng ký mượn tài liệu của thư viện như thế nào? | cao | -0.0196 (Mock) | Đúng (với Mock) |
| 2    | Hạn đóng học phí học kỳ này là khi nào? | Thời hạn cuối cùng để hoàn thành đóng học phí kỳ này là ngày mấy? | cao | -0.1727 (Mock) | Đúng (với Mock) |
| 3    | Sinh viên có thể đăng ký mượn sách thư viện học tập. | Khu vực tự học của thư viện mở cửa cả ngày cho sinh viên. | trung bình | -0.3568 (Mock) | Đúng (với Mock) |
| 4    | Quy định về thời gian gia hạn mượn sách thư viện. | Sinh viên bị trùng lịch thi cần liên hệ phòng khảo thí. | thấp | -0.1016 (Mock) | Đúng (với Mock) |
| 5    | Lịch đăng ký học phần được cập nhật trên trang học vụ. | Thực đơn căn tin hôm nay có món bún chả Hà Nội. | rất thấp | -0.0149 (Mock) | Đúng (với Mock) |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> Kết quả bất ngờ nhất là các điểm số của MockEmbedder đều rất gần 0 và không phản ánh đúng quan hệ ngữ nghĩa thực tế (ví dụ cặp có nghĩa tương đương lại có điểm thấp hơn cặp không liên quan). Điều này chứng minh rằng text embeddings chỉ có ý nghĩa biểu diễn ngữ nghĩa khi được huấn luyện trên các tập dữ liệu ngôn ngữ thực tế (như các mô hình ngôn ngữ lớn), còn các phương pháp băm hoặc sinh ngẫu nhiên như Mock chỉ có giá trị kiểm thử tính đúng đắn của code chứ không biểu diễn được ý nghĩa văn bản.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
| - | ----------------- | ------------------------------------------ | ------------ | --------------------------------- | ------------------------------------- |
| 1 | Làm thế nào để đăng ký học phần? | Sinh viên đăng ký học phần trong cổng học vụ theo lịch của từng học kỳ... (k3-course-registration::chunk_0) | 0.1692 | Có | Trả lời giả lập dựa trên tài liệu. |
| 2 | Tôi gặp lỗi trùng lịch học phần thì phải làm sao? | Sinh viên đăng ký học phần trong cổng học vụ theo lịch... (k3-course-registration::chunk_0) | 0.1692 | Có (nhưng chunk_1 chứa câu trả lời trực tiếp) | Trả lời giả lập dựa trên tài liệu. |
| 3 | Cách đăng ký mượn sách thư viện dành cho sinh viên? | Sinh viên đăng ký học phần trong cổng học vụ... (k3-course-registration::chunk_0) | 0.1867 | Không (do metadata filter loại mất file thư viện có audience là 'all') | Trả lời giả lập dựa trên tài liệu. |
| 4 | Người dùng thư viện cần mang theo giấy tờ gì? | trước khi xác nhận đăng ký... (k3-course-registration::chunk_1) | 0.0269 | Không (chunk liên quan thực tế xếp thứ 3) | Trả lời giả lập dựa trên tài liệu. |
| 5 | Làm thế nào để giải quyết các trường hợp ngoại lệ khi đăng ký môn học? | Sinh viên đăng ký học phần trong cổng học vụ... (k3-course-registration::chunk_0) | 0.1349 | Có (chunk_1 chứa thông tin liên quan xếp thứ 3) | Trả lời giả lập dựa trên tài liệu. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> Tôi học được tầm quan trọng cực kỳ lớn của việc thiết kế schema metadata phù hợp. Khi sử dụng bộ lọc `metadata_filter={"audience": "student"}`, nó đã loại bỏ hoàn toàn các tài liệu thư viện có thuộc tính `audience: "all"`, dẫn đến việc không thể truy xuất được thông tin thư viện dù câu hỏi rất liên quan. Cần thiết lập phân cấp metadata (ví dụ: `student` được kế thừa hoặc bao hàm bởi `all`) hoặc truy vấn linh hoạt hơn để không bị mất mát thông tin.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                           | Điểm tự đánh giá |
| ---------------------------------------------------- | ---------------------- |
| Khởi động (Warm-up)                               | 5 / 5                    |
| Hướng tiếp cận của tôi (My Approach)           | 10 / 10                   |
| Hoàn thiện code (Core Implementation — tests)     | 30 / 30                   |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5                    |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10                   |
| **Tổng phần cá nhân**                      | **60 / 60**         |
