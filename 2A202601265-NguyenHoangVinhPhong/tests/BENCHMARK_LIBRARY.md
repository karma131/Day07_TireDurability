# Benchmark — Dịch vụ thư viện VinUniversity

Phạm vi: dịch vụ thư viện dành cho sinh viên. Cả nhóm dùng đúng 5 câu hỏi dưới đây trên cùng corpus. Gold answer chỉ dựa trên nội dung đã lưu trong thư mục này.

## 1. Quyền mượn của sinh viên đại học

**Query:** Sinh viên đại học được mượn tối đa bao nhiêu tài liệu, trong bao lâu và được gia hạn trong điều kiện nào?

**Metadata filter bắt buộc:** `{"audience": "student"}`

**Gold answer:** Tối đa 3 tài liệu, mỗi tài liệu trong 2 tuần. Sách được gia hạn một lần thêm 1 tuần nếu chưa quá hạn và không có người khác yêu cầu.

**Evidence:** `vinuni-undergraduate-borrowing` — mục “Thẻ và định mức mượn”.

## 2. Giới hạn đặt phòng học nhóm

**Query:** Một nhóm được đặt phòng học thư viện tối đa bao lâu, bao nhiêu lần và điều gì xảy ra nếu đến muộn?

**Gold answer:** Tối đa 2 giờ mỗi phiên, 2 phiên mỗi ngày và 4 phiên mỗi tuần trên tổng số phòng. Có thể đặt trước tối đa 1 tuần; nếu vắng trong 10 phút đầu, phòng được giải phóng cho người khác.

**Evidence:** `vinuni-library-room-booking` — mục “Giới hạn sử dụng”.

## 3. Mượn và trả thiết bị

**Query:** Thiết bị thư viện được mượn trong bao lâu, phải trả lúc nào và khi nào bị xem là thất lạc?

**Gold answer:** Thiết bị được mượn trong 1 ngày làm việc, phải trả trực tiếp tại quầy tầng một chậm nhất 15 phút trước giờ đóng cửa. Quá hạn trên 5 ngày thì bị xem là thất lạc và người mượn phải trả chi phí thay thế.

**Evidence:** `vinuni-library-access-policy` — mục “Thiết bị và phòng chức năng”; đối chiếu `vinuni-undergraduate-borrowing` — mục “Mượn thiết bị”.

## 4. Truy cập tài nguyên từ ngoài trường

**Query:** Sinh viên truy cập tài nguyên điện tử từ ngoài trường bằng cách nào và cần lưu ý gì khi dùng máy tính công cộng?

**Gold answer:** Đăng nhập bằng VinUni ID. Tài nguyên chỉ dùng cho mục đích cá nhân, phi thương mại và phải tuân thủ bản quyền; khi dùng máy công cộng phải đóng trình duyệt sau khi hoàn tất.

**Evidence:** `vinuni-undergraduate-borrowing` — mục “Truy cập từ xa”.

## 5. Tài khoản vẫn báo quá hạn sau khi trả sách

**Query:** Sinh viên đã trả sách nhưng tài khoản vẫn báo quá hạn thì cần kiểm tra và xử lý theo các bước nào?

**Gold answer:** Xác nhận sách đã được trả qua máy self-check hoặc trạm trả 24/7, kiểm tra email xác nhận trả sách, rồi liên hệ Information Desk nếu tài khoản vẫn chưa cập nhật.

**Evidence:** `vinuni-library-faq` — mục “Đã trả sách nhưng tài khoản vẫn báo quá hạn”.

## Quy tắc chấm nhanh

- 2 điểm: top-3 có đúng evidence chunk và câu trả lời đủ điều kiện quan trọng.
- 1 điểm: top-3 có evidence nhưng câu trả lời thiếu điều kiện hoặc evidence không ở top-1.
- 0 điểm: top-3 không có evidence liên quan.

## Failure case nên theo dõi

Hai tài liệu về quyền mượn có con số khác nhau cho sinh viên đại học và học viên cao học. Nếu query số 1 không dùng filter `audience=student`, hệ thống có thể trả nhầm chunk “5 tài liệu trong 1 tháng” của nhóm cao học. Đây là trường hợp phù hợp để đo tác dụng của metadata filter.
