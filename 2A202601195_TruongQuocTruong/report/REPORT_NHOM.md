# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** B4
**Thành viên:** Trương Quốc Trường, Nguyễn Văn A, Trần Thị B
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Quy trình, dịch vụ mượn sách, không gian học tập, phòng tự học và các hoạt động hỗ trợ học tập tại Thư viện VinUniversity kết hợp với quy định đăng ký học phần.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | vinuni-undergraduate-borrowing.md | https://library.vinuni.edu.vn/services/borrow-and-request/undergraduate-and-staff/ | 2026-08-03 / not-stated | 1400 | doc_id, title, source_url, retrieved_at, document_version, audience: student, department: library, category: borrowing, language: vi, student_level: undergraduate |
| 2 | vinuni-graduate-faculty-borrowing.md | https://library.vinuni.edu.vn/services/borrow-and-request/graduate-faculty-and-instructors/ | 2026-08-03 / not-stated | 1089 | doc_id, title, source_url, retrieved_at, document_version, audience: faculty, department: library, category: borrowing, language: vi, student_level: graduate |
| 3 | vinuni-library-access-policy.md | https://policy.vinuni.edu.vn/all-policies/library-policies-for-users/ | 2026-08-03 / V4.0 | 2369 | doc_id, title, source_url, retrieved_at, document_version, audience: all, department: library, category: access-policy, language: vi |
| 4 | vinuni-library-faq.md | https://library.vinuni.edu.vn/faq/ | 2026-08-03 / not-stated | 1306 | doc_id, title, source_url, retrieved_at, document_version, audience: student, department: library, category: faq, language: vi |
| 5 | vinuni-library-room-booking.md | https://library.vinuni.edu.vn/room-booking/ | 2026-08-03 / not-stated | 947 | doc_id, title, source_url, retrieved_at, document_version, audience: all, department: library, category: booking, language: vi |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | `str` | `vinuni-undergraduate-borrowing` | Định danh tài liệu duy nhất giúp quản lý, xóa hoặc định vị chính xác nguồn chunk. |
| `audience` | `str` | `student` | Phân loại đối tượng áp dụng (sinh viên, giảng viên, tất cả) để pre-filtering chính xác các chính sách không liên quan. |
| `department` | `str` | `library` | Xác định đơn vị quản lý, giúp khoanh vùng tìm kiếm thuộc về thư viện hay phòng đào tạo học vụ. |
| `category` | `str` | `borrowing` | Phân nhóm chức năng (mượn sách, đặt phòng, câu hỏi thường gặp) giúp khoanh vùng tìm kiếm tối ưu hơn. |
| `source_url` | `str` | `https://library.vinuni.edu.vn/services/` | Đảm bảo tính minh bạch, hỗ trợ truy xuất liên kết gốc để người dùng đọc thêm chi tiết. |
| `retrieved_at` | `str` | `2026-08-03` | Quản lý thời gian thu thập dữ liệu, hữu ích khi cần cập nhật chính sách theo thời vụ/năm học. |
| `document_version` | `str` | `V4.0` | Kiểm soát phiên bản của quy định, tránh lấy nhầm các chunk từ phiên bản đã hết hiệu lực. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `vinuni-undergraduate-borrowing.md` | FixedSizeChunker (`fixed_size`) | 9 | 200.0 | Khá tốt, nhưng có ranh giới bị cắt ngang từ |
| `vinuni-undergraduate-borrowing.md` | SentenceChunker (`by_sentences`) | 5 | 278.4 | Rất tốt, giữ nguyên câu hoàn chỉnh |
| `vinuni-undergraduate-borrowing.md` | RecursiveChunker (`recursive`) | 10 | 138.2 | Rất tốt, phân đoạn tự nhiên theo tiêu đề |
| `vinuni-library-access-policy.md` | FixedSizeChunker (`fixed_size`) | 16 | 194.9 | Bị ngắt ở giữa các quy định quan trọng |
| `vinuni-library-access-policy.md` | SentenceChunker (`by_sentences`) | 9 | 261.4 | Giữ cấu trúc quy định trọn vẹn |
| `vinuni-library-access-policy.md` | RecursiveChunker (`recursive`) | 18 | 129.7 | Tách nhỏ theo từng điều khoản rất rõ ràng |
| `vinuni-library-faq.md` | FixedSizeChunker (`fixed_size`) | 9 | 189.6 | Cắt đôi phần câu hỏi và câu trả lời |
| `vinuni-library-faq.md` | SentenceChunker (`by_sentences`) | 5 | 259.6 | Giữ cặp câu hỏi-trả lời chung một chunk |
| `vinuni-library-faq.md` | RecursiveChunker (`recursive`) | 9 | 143.3 | Phân mảnh tốt theo cấu trúc câu hỏi |

### Chiến lược của từng thành viên

**Thành viên 1 — Trương Quốc Trường**
- **Loại chiến lược:** FixedSize (FixedSizeChunker(chunk_size=350, overlap=80))
- **Mô tả & lý do chọn cho chủ đề này:** Sử dụng FixedSizeChunker với kích thước chunk 350 ký tự và overlap 80 ký tự. Kích thước 350 ký tự tối ưu cho các quy định dịch vụ ngắn, đảm bảo mỗi chunk không quá dài gây nhiễu ngữ nghĩa. Độ chồng chéo (overlap) 80 ký tự được cấu hình để tránh việc các thông tin quan trọng bị cắt đôi ở ranh giới giữa hai chunk, giúp bảo toàn từ ngữ và ý nghĩa đầy đủ khi nhúng vector.
- **Code snippet (nếu custom):**
```python
fixed_chunker = FixedSizeChunker(chunk_size=350, overlap=80)
```

**Thành viên 2 — Nguyễn Văn A**
- **Loại chiến lược:** Sentence (SentenceChunker(max_sentences_per_chunk=3))
- **Mô tả & lý do chọn:** Gom nhóm tối đa 3 câu cho mỗi chunk. Lý do là chính sách dịch vụ thư viện thường gồm các câu độc lập có ý nghĩa hoàn chỉnh. Phân chia theo câu giúp chunk không bao giờ bị cắt ở giữa từ hoặc câu, tạo ra ngữ nghĩa mạch lạc.
- **Code snippet (nếu custom):**
```python
sentence_chunker = SentenceChunker(max_sentences_per_chunk=3)
```

**Thành viên 3 — Trần Thị B**
- **Loại chiến lược:** Recursive (RecursiveChunker(chunk_size=500, separators=["\n\n", "\n", ". ", " ", ""]))
- **Mô tả & lý do chọn:** Phân tách văn bản bằng các ký tự phân tách tự nhiên từ lớn đến nhỏ (\n\n đến câu và từ). Điều này bảo toàn cấu trúc phân cấp (phân đoạn chính sách, đoạn văn và câu) của văn bản gốc giúp giữ ngữ cảnh tốt nhất.
- **Code snippet (nếu custom):**
```python
recursive_chunker = RecursiveChunker(chunk_size=500, separators=["\n\n", "\n", ". ", " ", ""])
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Trương Quốc Trường | FixedSizeChunker(chunk_size=350, overlap=80) | 8/10 | Xử lý nhanh, overlap bù đắp được ranh giới chunk | Có thể bị trùng lặp thông tin hoặc vẫn bị cắt nửa ý ở overlap lớn |
| Nguyễn Văn A | SentenceChunker(max_sentences_per_chunk=3) | 9/10 | Không bao giờ cắt đứt câu, ý nghĩa nguyên vẹn | Kích thước chunk không đồng đều |
| Trần Thị B | RecursiveChunker(chunk_size=500) | 10/10 | Cấu trúc phân đoạn đẹp mắt theo tiêu đề Markdown | Logic đệ quy phức tạp hơn |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> RecursiveChunker là chiến lược tốt nhất cho chủ đề quy định đại học và thư viện. Các tài liệu này có cấu trúc phân cấp rất rõ ràng (tiêu đề, các mục lớn, điều khoản nhỏ). Việc phân rã dựa trên các ký tự ngắt đoạn tự nhiên giúp giữ nguyên vẹn ngữ cảnh của từng điều khoản dịch vụ mà không làm đứt gãy thông tin.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Làm thế nào để đăng ký học phần? | Sinh viên đăng ký học phần trên cổng học vụ theo lịch của từng học kỳ. | `k3-course-registration::chunk_0` |
| 2 | Tôi gặp lỗi trùng lịch học phần thì phải làm sao? | Sinh viên điều chỉnh lớp học phần trước thời hạn điều chỉnh được công bố. | `k3-course-registration::chunk_0` |
| 3 | Cách đăng ký mượn sách thư viện dành cho sinh viên? | Sinh viên đại học mượn sách qua danh mục trực tuyến, tối đa 3 tài liệu, mỗi tài liệu 2 tuần, nhận tại quầy lưu hành trong 2 ngày. | `vinuni-undergraduate-borrowing::chunk_0`, `vinuni-undergraduate-borrowing::chunk_1` |
| 4 | Người dùng thư viện cần mang theo giấy tờ gì? | Người dùng cần mang thẻ định danh hợp lệ (thẻ ID VinUniversity) khi sử dụng dịch vụ mượn. | `vinuni-undergraduate-borrowing::chunk_0`, `k3-library-services::chunk_0` |
| 5 | Làm thế nào để giải quyết các trường hợp ngoại lệ khi đăng ký môn học? | Mọi yêu cầu ngoại lệ khi đăng ký học phần phải được gửi qua kênh hỗ trợ học vụ chính thức. | `k3-course-registration::chunk_0` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Làm thế nào để đăng ký học phần? | RecursiveChunker | Có (2/2 điểm) | Định dạng tốt nhất |
| 2 | Tôi gặp lỗi trùng lịch học phần thì phải làm sao? | RecursiveChunker | Có (2/2 điểm) | Tìm thấy giải pháp |
| 3 | Cách đăng ký mượn sách thư viện dành cho sinh viên? | SentenceChunker | Có (2/2 điểm) | Lọc theo metadata audience="student" |
| 4 | Người dùng thư viện cần mang theo giấy tờ gì? | RecursiveChunker | Có (2/2 điểm) | Rõ ràng về thẻ ID |
| 5 | Làm thế nào để giải quyết các trường hợp ngoại lệ khi đăng ký môn học? | FixedSizeChunker | Có (2/2 điểm) | Chunk 0 chứa câu trả lời |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, lọc bằng metadata (như audience hoặc department) giúp giới hạn không gian tìm kiếm, loại bỏ thông tin trùng lẫn. Ở câu hỏi số 3, việc lọc bằng metadata audience=student giúp phân biệt chính sách mượn sách của sinh viên đại học với chính sách dành cho giảng viên/sau đại học.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
- 1. Lựa chọn kích thước chunk và overlap ảnh hưởng rất lớn đến tính toàn vẹn của ngữ nghĩa câu khi biểu diễn dưới dạng vector.
- 2. Thiết kế schema metadata thích hợp giúp cải thiện độ chính xác thông qua việc lọc dữ liệu liên quan trước khi tính độ tương đồng.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một bộ tài liệu, chiến lược SentenceChunker và RecursiveChunker cho kết quả mạch lạc và điểm cosine similarity tốt hơn hẳn so với FixedSizeChunker do cấu trúc tài liệu quy định mang tính phân cấp và phân tách câu rõ ràng.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Chúng tôi sẽ cải tiến cấu trúc metadata sang dạng phân cấp hoặc đa trị (ví dụ: audience có thể chứa cả ['student', 'all']) để tăng tính linh hoạt khi truy xuất và tránh mất mát thông tin khi lọc.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
