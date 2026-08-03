# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyen Quoc Anh
**Nhóm:** Chưa cập nhật
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

Độ tương tự cosine cao nghĩa là hai vector có hướng gần giống nhau, tức là nội dung/ngữ nghĩa của hai đoạn văn bản giống nhau hoặc liên quan chặt chẽ. Giá trị càng gần 1 thì mức độ đồng hướng càng lớn.

**Ví dụ có độ tương tự CAO:**

- Câu A: Sinh viên đăng ký học phần trong cổng học vụ.
- Câu B: Sinh viên đăng ký môn học qua cổng học vụ.
- Tại sao tương đồng: Hai câu nói cùng một hành động và cùng ngữ cảnh học vụ, chỉ khác cách diễn đạt.

**Ví dụ có độ tương tự THẤP:**

- Câu A: Học phần có thể yêu cầu tiên quyết.
- Câu B: Trời hôm nay nhiều mây và gió.
- Tại sao khác: Hai câu không cùng chủ đề, không chia sẻ ngữ nghĩa đáng kể.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> _Viết 1-2 câu:_

Cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings vì nó so sánh hướng của vector thay vì độ lớn tuyệt đối. Với embedding văn bản, hướng vector thường quan trọng hơn khoảng cách gốc tọa độ, nên cosine ổn định hơn khi độ dài vector thay đổi.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> _Trình bày phép tính:_

Với `chunk_size = 500` và `overlap = 50`, bước nhảy là `500 - 50 = 450`.

Số chunk xấp xỉ:

`1 + ceil((10000 - 500) / 450) = 1 + ceil(9500 / 450) = 1 + 22 = 23`

Đáp án: **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> _Viết 1-2 câu:_

Nếu overlap tăng lên 100 thì bước nhảy giảm còn 400, nên số chunk tăng lên khoảng 25. Overlap lớn hơn giúp giữ ngữ cảnh giữa các chunk tốt hơn, nhưng đổi lại tăng độ dư thừa và chi phí lưu trữ/truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

> _Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?_

Tôi dùng regex `(?<=[.!?])\s+` để tách câu theo dấu kết thúc câu rồi ghép lại thành chunk theo `max_sentences_per_chunk`. Các trường hợp biên như chuỗi rỗng, nhiều khoảng trắng, hoặc đầu vào chỉ có một câu đều được trả về an toàn dưới dạng danh sách chunk hợp lệ.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

> _Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?_

`RecursiveChunker` thử tách văn bản theo thứ tự ưu tiên của các separator, từ đoạn lớn đến nhỏ. Base case là khi đoạn hiện tại đã ngắn hơn `chunk_size`, hoặc khi không còn separator phù hợp thì cắt thẳng theo độ dài cố định để không bị kẹt đệ quy.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

> _Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?_

Tôi lưu mỗi tài liệu thành một record chuẩn hóa gồm `id`, `content`, `metadata`, và `embedding`; trong chế độ mặc định, dữ liệu được giữ trong bộ nhớ để test ổn định. Khi tìm kiếm, tôi lấy embedding của câu hỏi rồi tính điểm theo tích vô hướng với các vector đã lưu; vì embedding trong lab đã được chuẩn hóa, cách này tương đương với cosine ranking.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

> _Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?_

Tôi lọc theo metadata trước khi chạy truy xuất để giảm tập ứng viên và giữ đúng điều kiện tìm kiếm. Việc xóa được thực hiện bằng cách loại toàn bộ record có `metadata['doc_id']` trùng với tài liệu cần xóa, đồng thời trả về `True/False` để biết có xóa được gì hay không.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

> _Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?_

Tác tử lấy top-k chunk từ store, ghép chúng thành phần `Context` và đặt câu hỏi ở cuối prompt để mô hình trả lời dựa trên ngữ cảnh đã truy xuất. Cách này giúp RAG tách rõ bước retrieval và bước generation, nên dễ kiểm tra xem câu trả lời có bám dữ liệu hay không.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
collected 42 items

============================= 42 passed in 0.12s =============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A                                                       | Câu B                                                    | Dự đoán | Điểm thực tế | Đúng?         |
| --- | ----------------------------------------------------------- | -------------------------------------------------------- | ------- | ------------ | ------------- |
| 1   | Sinh viên đăng ký học phần trong cổng học vụ.               | Sinh viên đăng ký môn học qua cổng học vụ.               | cao     | -0.001509    | Không         |
| 2   | Thư viện có dịch vụ mượn tài liệu.                          | Người dùng cần mang thẻ định danh khi mượn.              | cao     | -0.080959    | Không         |
| 3   | Học phần có thể yêu cầu tiên quyết.                         | Trời hôm nay nhiều mây và gió.                           | thấp    | 0.008643     | Không         |
| 4   | Khi gặp lỗi trùng lịch, sinh viên điều chỉnh lớp học phần.  | Khi bị trùng lịch, sinh viên đổi lớp học phần trước hạn. | cao     | -0.038027    | Không         |
| 5   | Đăng ký học phần cần kiểm tra điều kiện trước khi xác nhận. | Thư viện cho mượn tài liệu và không gian học tập.        | thấp    | -0.011987    | Đúng một phần |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> _Viết 2-3 câu:_

Kết quả bất ngờ nhất là các cặp câu có nghĩa gần nhau vẫn cho điểm rất thấp hoặc âm. Điều này cho thấy mock embeddings trong lab chỉ phù hợp để kiểm thử tính ổn định của code, không dùng để kết luận chất lượng ngữ nghĩa hay so sánh chiến lược retrieval.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| #   | Câu hỏi (Query)                               | Top-1 Chunk truy xuất được (tóm tắt)                                          | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
| --- | --------------------------------------------- | ----------------------------------------------------------------------------- | ---------- | ------------------------------ | ------------------------------- |
| 1   | Sinh viên đăng ký học phần ở đâu?             | `k3-library-services` - dịch vụ thư viện, mượn tài liệu và không gian học tập | 0.210453   | Không                          | `Answer based on context.`      |
| 2   | Học phần có thể yêu cầu gì trước khi đăng ký? | `k3-course-registration` - điều kiện trước khi xác nhận đăng ký               | 0.100874   | Có                             | `Answer based on context.`      |
| 3   | Nếu bị trùng lịch thì sinh viên cần làm gì?   | `k3-library-services` - dịch vụ thư viện                                      | 0.272676   | Không                          | `Answer based on context.`      |
| 4   | Thư viện cung cấp những dịch vụ nào?          | `k3-course-registration` - đăng ký học phần                                   | 0.016774   | Không                          | `Answer based on context.`      |
| 5   | Người dùng cần mang gì khi mượn tài liệu?     | `k3-course-registration` - đăng ký học phần                                   | -0.038728  | Không                          | `Answer based on context.`      |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> _Viết 2-3 câu:_

Tôi học được rằng với mock embeddings, top-1 có thể sai rất xa nhưng top-3 vẫn còn giữ được chunk liên quan, nên cần đọc cả bức tranh thay vì chỉ nhìn một kết quả đầu tiên. Tôi cũng thấy rõ việc dùng local embedder ở Giai đoạn 2 là cần thiết nếu muốn so sánh chiến lược chunking và metadata một cách có ý nghĩa.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                        | Điểm tự đánh giá |
| ----------------------------------------------- | ---------------- |
| Khởi động (Warm-up)                             | 5 / 5            |
| Hướng tiếp cận của tôi (My Approach)            | 10 / 10          |
| Hoàn thiện code (Core Implementation — tests)   | 30 / 30          |
| Dự đoán độ tương tự (Similarity Predictions)    | 5 / 5            |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10          |
| **Tổng phần cá nhân**                           | **60 / 60**      |
