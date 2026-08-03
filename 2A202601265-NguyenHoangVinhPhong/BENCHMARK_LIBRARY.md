# Bộ Câu Hỏi Đánh Giá Truy Xuất — Dịch Vụ Thư Viện VinUniversity (K3 Library Services Benchmark Suite)

Tài liệu này chứa bộ **5 câu hỏi đánh giá chuẩn (Benchmark Queries)** kèm **câu trả lời chuẩn (Gold Answers)** và **yêu cầu lọc siêu dữ liệu (Metadata Filtering)** cho chủ đề **Dịch vụ Thư viện VinUniversity (`k3-library-services`)**.

---

## 1. Danh Sách Câu Hỏi Đánh Giá (Benchmark Queries)

| # | Câu hỏi đánh giá (Query) | Câu trả lời chuẩn (Gold Answer) | Tài liệu & Chunk chứa thông tin | Bộ lọc Metadata (Metadata Filter) |
|---|------------------------|-------------------------------|----------------------------------|------------------------------------|
| **1** | Sinh viên đại học được mượn tối đa bao nhiêu tài liệu và trong thời hạn bao lâu? | Sinh viên đại học được mượn tối đa 3 tài liệu, mỗi tài liệu trong thời hạn 2 tuần. Sách được gia hạn một lần thêm 1 tuần nếu chưa quá hạn và không có người khác yêu cầu. | `vinuni-undergraduate-borrowing` (`chunk_0`) | `{"audience": "student", "category": "borrowing"}` |
| **2** | Quy định và các bước đặt phòng học nhóm tại thư viện qua Microsoft Outlook như thế nào? | Đặt phòng qua Microsoft Outlook: mở Calendar > New Meeting > chọn phòng trong Rooms > chọn thời gian & nhập email thành viên > gửi. Nhóm phải từ 2 người trở lên, được đặt tối đa 2 giờ/phiên, 2 phiên/ngày và 4 phiên/tuần. Nếu muộn quá 10 phút, đặt chỗ sẽ bị hủy. | `vinuni-library-room-booking` (`chunk_0`, `chunk_1`, `chunk_2`) | `{"category": "room-booking"}` |
| **3** | Làm thế nào để xem hạn trả sách và gia hạn sách trực tuyến? | Đăng nhập website thư viện VinUni, mở My Library Account bằng tài khoản VinUni. Để gia hạn, chọn RENEW ALL cho tất cả sách hoặc vào mục LOAN chọn RENEW cho từng cuốn. | `vinuni-library-faq` (`chunk_1`) | `{"category": "self-service-help"}` |
| **4** | Học viên cao học và giảng viên được mượn tối đa bao nhiêu tài liệu? | Học viên cao học được mượn tối đa 5 tài liệu trong thời hạn 1 tháng (gia hạn 1 lần thêm 2 tuần). Giảng viên VinUni được mượn 5 tài liệu trong 6 tháng (gia hạn 1 lần). | `vinuni-graduate-faculty-borrowing` (`chunk_0`) | `{"audience": "faculty"}` *(Bắt buộc dùng filter để tránh lầm với đối tượng sinh viên)* |
| **5** | Thời hạn mượn thiết bị thư viện là bao lâu và quy định xử lý khi quá hạn trên 5 ngày? | Thiết bị được mượn trong 1 ngày làm việc, phải trả trực tiếp tại quầy lưu hành tầng một chậm nhất 15 phút trước giờ đóng cửa. Thiết bị quá hạn trên 5 ngày được tính là thất lạc và người mượn phải trả chi phí thay thế. | `vinuni-undergraduate-borrowing` (`chunk_2`) / `vinuni-library-access-policy` (`chunk_3`) | `None` / `{"department": "library"}` |

---

## 2. Tiêu Chí Đánh Giá & Phương Pháp Truy Xuất

### Chiến lược chunking đề xuất: `RecursiveChunker`
- **Tham số:** `chunk_size = 400`, `separators = ["\n\n", "\n", ". ", " ", ""]`
- **Lý do lựa chọn:** Tài liệu quy định thư viện được cấu trúc rõ ràng theo các mục (headers `##`), đoạn văn (`\n\n`) và câu (`. `). `RecursiveChunker` bảo toàn được ranh giới các quy định (định mức mượn, quy trình đặt phòng) mà không làm ngắt đôi ý nghĩa như `FixedSizeChunker`.

### Vai trò của Metadata Filtering
- **Bài kiểm tra phân tách đối tượng (Audience Isolation):** Ở **Câu hỏi 4**, nếu không dùng bộ lọc `metadata_filter={"audience": "faculty"}`, câu hỏi về định mức mượn của giảng viên/cao học dễ bị nhầm lẫn với sinh viên đại học do từ khóa "mượn tài liệu" xuất hiện ở nhiều tài liệu. Bộ lọc metadata giúp đảm bảo chỉ tìm kiếm trong phạm vi đối tượng mong muốn.
