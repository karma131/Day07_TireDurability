# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Ngọc Ánh
**Nhóm:** TireDurability
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai vector embedding có hướng gần nhau, nên hai đoạn văn thường nói về cùng chủ đề hoặc có ý nghĩa ngữ nghĩa gần nhau. Điểm càng gần 1 thì mức tương đồng theo hướng càng lớn.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên được mượn tối đa ba cuốn sách trong hai tuần.
- Câu B: Thời hạn mượn ba tài liệu của sinh viên đại học là 14 ngày.
- Tại sao tương đồng: Hai câu diễn đạt cùng một quy định mượn sách bằng từ ngữ khác nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Sinh viên có thể đặt phòng học nhóm qua Microsoft Outlook.
- Câu B: Món phở cần được nấu từ nước dùng và các loại gia vị.
- Tại sao khác: Hai câu thuộc hai chủ đề không liên quan là dịch vụ thư viện và ẩm thực.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity tập trung vào hướng của vector, tức mẫu phân bố đặc trưng ngữ nghĩa, thay vì độ lớn tuyệt đối. Vì vậy nó ít bị ảnh hưởng bởi khác biệt về độ dài hoặc magnitude của embedding hơn khoảng cách Euclid, đặc biệt khi các vector đã được chuẩn hóa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính: `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22,11)`.
>
> Đáp án: **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, số chunk là `ceil((10000 - 100) / (500 - 100)) = ceil(24,75) = 25`, tức tăng từ 23 lên 25. Overlap lớn hơn giúp giữ lại ngữ cảnh nằm sát ranh giới giữa hai chunk, nhưng làm tăng số vector, chi phí lưu trữ và khả năng trả về nội dung trùng lặp.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Vai trò và chiến lược cá nhân

Tôi đảm nhận nhiệm vụ **tổng hợp dữ liệu và chạy baseline**. Chiến lược cá nhân là `FixedSizeChunker(chunk_size=500, overlap=50)`, được chọn làm đường cơ sở vì đơn giản, có tham số rõ ràng và tạo điều kiện so sánh công bằng với FixedSize cấu hình khác, SentenceChunker, RecursiveChunker và custom chunker theo heading của các thành viên còn lại.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])(?:[ \t]+|\r?\n+)` để tách tại khoảng trắng hoặc xuống dòng ngay sau dấu kết thúc câu, đồng thời giữ dấu câu trong nội dung. Các câu được loại bỏ khoảng trắng thừa rồi gom theo `max_sentences_per_chunk`; văn bản rỗng hoặc chỉ có khoảng trắng trả về danh sách rỗng và tham số nhỏ hơn 1 được đưa về 1.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử lần lượt các separator theo mức ưu tiên `\n\n`, `\n`, `. `, khoảng trắng và cuối cùng là ký tự. Base case là đoạn hiện tại không vượt quá `chunk_size`; nếu hết separator hoặc gặp separator rỗng, đoạn được cắt trực tiếp theo số ký tự. Các phần nhỏ được ghép lại đến giới hạn, còn phần quá lớn tiếp tục được chia đệ quy bằng separator tiếp theo.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuyển thành record gồm ID nội bộ duy nhất, content, metadata và embedding; metadata được tự bổ sung `doc_id` nếu thiếu. Store ưu tiên ChromaDB khi có sẵn và fallback sang danh sách in-memory. Khi tìm kiếm, query được embedding bằng cùng hàm, tính dot product với từng record, sắp xếp score giảm dần và lấy tối đa `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc record theo tất cả cặp key-value của metadata trước, sau đó mới tính similarity trên tập ứng viên còn lại; cách này vừa giảm nhiễu vừa đúng yêu cầu metadata pre-filtering. `delete_document` xóa toàn bộ record có `metadata['doc_id']` trùng với ID cần xóa và trả về `True` chỉ khi thực sự có ít nhất một record bị loại bỏ.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent lấy top-k chunk từ store, đánh số từng nguồn rồi ghép content và `source_url` thành khối Context. Prompt yêu cầu mô hình chỉ trả lời dựa trên context, phải nói không đủ thông tin nếu evidence chưa đủ, sau đó chèn nguyên câu hỏi và gọi `llm_fn`. Cách này giúp câu trả lời có căn cứ và vẫn cho phép thay thế LLM thật hoặc hàm giả lập khi kiểm thử.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
=============================== test session starts ================================
platform win32 -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0 -- D:\Vin\Lab07\DAY07_2A202601643_NguyenNgocAnh\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\Vin\Lab07\DAY07_2A202601643_NguyenNgocAnh
plugins: anyio-4.14.2
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED  [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED        [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED   [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED         [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED        [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED  [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED   [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED  [ 66%]
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

================================ 42 passed in 0.12s ================================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Điểm thực tế được tính bằng cosine similarity trên embedding của mô hình `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên được mượn tối đa ba cuốn sách trong hai tuần. | Sinh viên đại học có thể giữ ba tài liệu trong 14 ngày. | Cao | 0.6639 | Đúng |
| 2 | Nhóm có thể đặt phòng học tối đa hai giờ mỗi phiên. | Mỗi lượt sử dụng phòng học nhóm không được vượt quá 120 phút. | Cao | 0.6254 | Đúng |
| 3 | Thư viện đóng cửa vào ngày lễ quốc gia. | Cách nấu phở cần nước dùng và gia vị. | Thấp | -0.0342 | Đúng |
| 4 | Sinh viên truy cập tài nguyên trực tuyến từ ngoài trường bằng VinUni ID. | Tài khoản VinUni cho phép sinh viên đăng nhập cơ sở dữ liệu thư viện từ xa. | Cao | 0.7468 | Đúng |
| 5 | Sinh viên đại học được mượn ba tài liệu trong hai tuần. | Học viên cao học được mượn năm tài liệu trong một tháng. | Cao | 0.7771 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 5 bất ngờ nhất vì đạt 0.7771, cao hơn cả hai cặp diễn đạt gần như tương đương ở câu 1 và câu 2, dù hai câu áp dụng cho đối tượng, số lượng và thời hạn mượn khác nhau. Embedding nắm rất mạnh chủ đề và cấu trúc ngữ nghĩa chung “đối tượng được mượn số tài liệu trong một khoảng thời gian”, nhưng không bảo đảm phân biệt chính xác mọi con số và điều kiện. Vì vậy semantic similarity không đồng nghĩa với tính đúng của chính sách; hệ thống RAG vẫn cần metadata filter và evidence cụ thể.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên đại học được mượn tối đa bao nhiêu tài liệu, trong bao lâu và được gia hạn trong điều kiện nào? | `vinuni-undergraduate-borrowing`, chunk 0: tối đa 3 tài liệu/2 tuần, gia hạn một lần thêm 1 tuần nếu đủ điều kiện | 0.7185 | Có — đúng ngay top-1 sau filter `audience=student` | Sinh viên đại học được mượn tối đa 3 tài liệu trong 2 tuần. Sách được gia hạn một lần thêm 1 tuần nếu chưa quá hạn và không có người dùng khác yêu cầu. |
| 2 | Một nhóm được đặt phòng học thư viện tối đa bao lâu, bao nhiêu lần và điều gì xảy ra nếu đến muộn? | `vinuni-library-room-booking`, chunk 0: 2 giờ/phiên, 2 phiên/ngày, 4 phiên/tuần và đặt trước tối đa 1 tuần | 0.6881 | Có, nhưng chunk bị cắt trước chi tiết đến muộn 10 phút | Mỗi nhóm được đặt tối đa 2 giờ/phiên, 2 phiên/ngày và 4 phiên/tuần, có thể đặt trước tối đa 1 tuần. Context top-3 chưa cung cấp đủ thông tin để kết luận điều gì xảy ra khi nhóm đến muộn. |
| 3 | Thiết bị thư viện được mượn trong bao lâu, phải trả lúc nào và khi nào bị xem là thất lạc? | `vinuni-library-access-policy`, chunk 3: mượn 1 ngày làm việc, trả trước đóng cửa 15 phút, quá hạn trên 5 ngày coi là thất lạc | 0.7360 | Có — đúng ngay top-1 | Thiết bị được mượn trong 1 ngày làm việc và phải trả trực tiếp tại quầy lưu hành tầng một, chậm nhất 15 phút trước giờ đóng cửa. Nếu quá hạn trên 5 ngày, thiết bị được xem là thất lạc và người mượn phải trả chi phí thay thế. |
| 4 | Sinh viên truy cập tài nguyên điện tử từ ngoài trường bằng cách nào và cần lưu ý gì khi dùng máy tính công cộng? | `vinuni-undergraduate-borrowing`, chunk 2: dùng VinUni ID, đóng trình duyệt trên máy công cộng và chỉ dùng tài nguyên phi thương mại | 0.7686 | Có — đúng ngay top-1 | Sinh viên đăng nhập tài nguyên từ ngoài trường bằng VinUni ID. Khi dùng máy tính công cộng phải đóng trình duyệt sau khi hoàn tất; tài nguyên chỉ được dùng cho mục đích cá nhân, phi thương mại và phải tuân thủ bản quyền. |
| 5 | Sinh viên đã trả sách nhưng tài khoản vẫn báo quá hạn thì cần kiểm tra và xử lý theo các bước nào? | `vinuni-library-faq`, chunk 1: kiểm tra máy/trạm trả, email xác nhận rồi liên hệ Information Desk | 0.7135 | Có — đúng ngay top-1 | Trước tiên, xác nhận sách đã được trả qua máy self-check hoặc trạm trả sách 24/7. Sau đó kiểm tra email xác nhận trả sách; nếu tài khoản vẫn chưa cập nhật thì liên hệ nhân viên tại Information Desk. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5 / 5**

**Nhận xét failure case:** Câu 2 truy xuất đúng tài liệu ở top-1, nhưng `FixedSizeChunker(chunk_size=500, overlap=50)` cắt chunk trước điều kiện “đến muộn quá 10 phút”. Chunk tiếp theo chứa điều kiện này không xuất hiện trong top-3, cho thấy fixed-size baseline có thể tìm đúng chủ đề nhưng vẫn bỏ sót một điều kiện quan trọng nằm qua ranh giới chunk.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Qua phần so sánh/demo nội bộ, tôi học được rằng tìm đúng tài liệu chưa có nghĩa là context đã chứa đủ mọi điều kiện. RecursiveChunker của Đào Văn Đà giữ ranh giới đoạn tốt hơn baseline fixed-size và lấy được phần policy bổ sung cho câu đặt phòng, trong khi chunk của tôi bị cắt trước quy tắc đến muộn 10 phút. Tôi cũng thấy metadata filter đặc biệt quan trọng ở câu hỏi mượn sách: lọc `audience=student` giúp loại chính sách dành cho cao học/giảng viên dù các tài liệu có từ khóa và độ tương tự rất gần nhau.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 9 / 10 |
| **Tổng phần cá nhân** | **59 / 60** |
