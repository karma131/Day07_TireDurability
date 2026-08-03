# Kết quả Giai đoạn 2 — Thành viên 4

- **Sinh viên:** Đào Văn Đa (2A202601089)
- **Chiến lược:** `RecursiveChunker(chunk_size=500)`
- **Embedding:** `text-embedding-3-small`
- **LLM:** `gpt-4o-mini`
- **Sinh câu trả lời:** 1 lượt
- **Corpus:** `data/vinuni_library_services`
- **Số chunk:** 23
- **Độ dài chunk trung bình:** 387.87 ký tự
- **Điểm benchmark:** **10 / 10**

## Kết quả 5 câu hỏi

### Câu 1

**Query:** Sinh viên đại học được mượn tối đa bao nhiêu tài liệu, trong bao lâu và được gia hạn trong điều kiện nào?

**Metadata filter:** `{'audience': 'student'}`

**Điểm tự động theo rubric:** **2 / 2**

**Evidence rank:** `[1, 2]`

**Top-3:**

1. `vinuni-undergraduate-borrowing` — score `0.689121` — # Dịch vụ mượn tài liệu cho sinh viên đại học ## Thẻ và định mức mượn VinUniversity ID đồng thời là thẻ thư viện để mượn tài liệu hoặc thiết bị. Sinh viên đại học được mượn tối đa 3 tài liệu, mỗi tài liệu trong 2 tuần. Sách được gia hạn một
2. `vinuni-undergraduate-borrowing` — score `0.503894` — Sinh viên có thể yêu cầu sách qua danh mục trực tuyến. Việc xử lý thường mất 1–2 ngày làm việc và thư viện gửi email khi sách sẵn sàng. Sách được giữ trong 2 ngày để người yêu cầu đến nhận tại quầy lưu hành. ## Mượn thiết bị Thiết bị được m
3. `vinuni-library-faq` — score `0.497523` — # Hướng dẫn thao tác thường gặp tại thư viện ## Mượn và trả sách bằng máy Máy self-check ở tầng một hoặc tầng hai được dùng để mượn hoặc trả sách in. Máy trả sách 24/7 tại lối vào chính chỉ dùng để trả sách. ## Xem hạn trả và gia hạn Để xem

**Câu trả lời của agent:**

Sinh viên đại học được mượn tối đa 3 tài liệu, mỗi tài liệu trong 2 tuần. Sách được gia hạn một lần thêm 1 tuần nếu chưa quá hạn và không có người dùng khác yêu cầu. Việc gia hạn có thể thực hiện trực tuyến hoặc bằng máy self-check tại tầng một hoặc tầng hai. [Nguồn 1]

Thông tin đối chiếu trực tiếp từ chính sách: VinUniversity ID đồng thời là thẻ thư viện để mượn tài liệu hoặc thiết bị. Sinh viên đại học được mượn tối đa 3 tài liệu, mỗi tài liệu trong 2 tuần. Sách được gia hạn một lần thêm 1 tuần nếu chưa quá hạn và không có người dùng khác yêu cầu. Có thể gia hạn trực tuyến hoặc bằng máy self-check tại tầng một hoặc tầng hai. [Nguồn 1]

**Gold answer:** Tối đa 3 tài liệu, mỗi tài liệu trong 2 tuần. Sách được gia hạn một lần thêm 1 tuần nếu chưa quá hạn và không có người khác yêu cầu.

### Câu 2

**Query:** Một nhóm được đặt phòng học thư viện tối đa bao lâu, bao nhiêu lần và điều gì xảy ra nếu đến muộn?

**Metadata filter:** `None`

**Điểm tự động theo rubric:** **2 / 2**

**Evidence rank:** `[1]`

**Top-3:**

1. `vinuni-library-room-booking` — score `0.560913` — # Quy định đặt phòng học nhóm tại thư viện ## Đối tượng và nguyên tắc đặt phòng Phòng học nhóm có thể được đặt bởi sinh viên, giảng viên và nhân viên VinUniversity. Một nhóm phải có ít nhất 2 người. Việc đặt phòng được xử lý theo thứ tự đăn
2. `vinuni-library-access-policy` — score `0.533647` — Thiết bị thư viện được mượn trong 1 ngày làm việc và phải trả trực tiếp tại quầy lưu hành tầng một, muộn nhất 15 phút trước giờ đóng cửa. Thiết bị quá hạn trên 5 ngày được xem là thất lạc và người mượn phải trả chi phí thay thế. Phòng chức 
3. `vinuni-library-spaces` — score `0.481213` — # Các loại không gian trong thư viện ## Không gian cộng tác Thư viện có phòng thảo luận, booth thảo luận mở và khu ghế ngồi ở cả hai tầng. Người dùng còn có thể tiếp cận maker space, studio, phòng teleconference và phòng máy tính. Khu học t

**Câu trả lời của agent:**

Một nhóm được đặt phòng học thư viện tối đa 2 giờ trong một phiên, 2 phiên trong một ngày và 4 phiên trong một tuần, tính chung cho tất cả phòng. Nếu người dùng đến muộn quá 10 phút, đặt chỗ sẽ bị hủy. [Nguồn 1]

Thông tin đối chiếu trực tiếp từ chính sách: Mỗi nhóm được đặt tối đa 2 giờ trong một phiên, 2 phiên trong một ngày và 4 phiên trong một tuần, tính chung cho tất cả phòng. Có thể đặt trong ngày sử dụng hoặc sớm nhất 1 tuần trước đó. [Nguồn 1]

**Gold answer:** Tối đa 2 giờ mỗi phiên, 2 phiên mỗi ngày và 4 phiên mỗi tuần trên tổng số phòng. Có thể đặt trước tối đa 1 tuần; nếu vắng trong 10 phút đầu, phòng được giải phóng cho người khác.

### Câu 3

**Query:** Thiết bị thư viện được mượn trong bao lâu, phải trả lúc nào và khi nào bị xem là thất lạc?

**Metadata filter:** `None`

**Điểm tự động theo rubric:** **2 / 2**

**Evidence rank:** `[1, 2, 3]`

**Top-3:**

1. `vinuni-library-access-policy` — score `0.674056` — Thiết bị thư viện được mượn trong 1 ngày làm việc và phải trả trực tiếp tại quầy lưu hành tầng một, muộn nhất 15 phút trước giờ đóng cửa. Thiết bị quá hạn trên 5 ngày được xem là thất lạc và người mượn phải trả chi phí thay thế. Phòng chức 
2. `vinuni-undergraduate-borrowing` — score `0.544345` — Sinh viên có thể yêu cầu sách qua danh mục trực tuyến. Việc xử lý thường mất 1–2 ngày làm việc và thư viện gửi email khi sách sẵn sàng. Sách được giữ trong 2 ngày để người yêu cầu đến nhận tại quầy lưu hành. ## Mượn thiết bị Thiết bị được m
3. `vinuni-library-access-policy` — score `0.542096` — Người dùng có thể yêu cầu tài liệu đang được mượn qua hệ thống thư viện. Khi tài liệu sẵn sàng, thư viện giữ tài liệu trong 2 ngày; quá thời gian này yêu cầu sẽ bị hủy. Course Reserve, tài liệu thất lạc, tài liệu không được lưu hành, hoặc y

**Câu trả lời của agent:**

Thiết bị thư viện được mượn trong 1 ngày làm việc. Người mượn phải trả thiết bị chậm nhất 15 phút trước giờ đóng cửa. Nếu thiết bị quá hạn trên 5 ngày, nó sẽ được xem là thất lạc và người mượn phải trả chi phí thay thế. [Nguồn 1]

Thông tin đối chiếu trực tiếp từ chính sách: Thiết bị thư viện được mượn trong 1 ngày làm việc và phải trả trực tiếp tại quầy lưu hành tầng một, muộn nhất 15 phút trước giờ đóng cửa. Thiết bị quá hạn trên 5 ngày được xem là thất lạc và người mượn phải trả chi phí thay thế. [Nguồn 1]

**Gold answer:** Thiết bị được mượn trong 1 ngày làm việc, phải trả trực tiếp tại quầy tầng một chậm nhất 15 phút trước giờ đóng cửa. Quá hạn trên 5 ngày thì bị xem là thất lạc và người mượn phải trả chi phí thay thế.

### Câu 4

**Query:** Sinh viên truy cập tài nguyên điện tử từ ngoài trường bằng cách nào và cần lưu ý gì khi dùng máy tính công cộng?

**Metadata filter:** `None`

**Điểm tự động theo rubric:** **2 / 2**

**Evidence rank:** `[1]`

**Top-3:**

1. `vinuni-undergraduate-borrowing` — score `0.717796` — Danh mục thiết bị gồm laptop, iPad, bộ sạc, chuột, tai nghe, adapter, bút trình chiếu, bút viết và tẩy bảng, cùng tủ khóa. ## Truy cập từ xa Sinh viên hiện tại có thể truy cập tài nguyên trực tuyến từ ngoài trường bằng VinUni ID. Khi dùng m
2. `vinuni-graduate-faculty-borrowing` — score `0.598260` — Người dùng hiện tại có thể truy cập tài nguyên điện tử từ xa bằng tài khoản VinUni. Tài nguyên chỉ được dùng cho mục đích cá nhân, phi thương mại và phải tuân thủ luật bản quyền cũng như điều khoản của nhà cung cấp.
3. `vinuni-library-access-policy` — score `0.533523` — ## Tài nguyên điện tử và sao chụp Tài nguyên điện tử chỉ dành cho người dùng được VinUni cho phép. Người dùng đăng nhập bằng VinUni ID và chỉ sử dụng tài liệu cho mục đích cá nhân, phi thương mại. Dịch vụ in, sao chụp và quét chỉ phục vụ họ

**Câu trả lời của agent:**

Sinh viên hiện tại có thể truy cập tài nguyên điện tử từ ngoài trường bằng cách sử dụng VinUni ID. Khi sử dụng máy tính công cộng, người dùng cần lưu ý đóng trình duyệt sau khi hoàn tất để tránh người khác sử dụng sai tài khoản hoặc tài nguyên. Tài nguyên điện tử phải được sử dụng cho mục đích cá nhân, phi thương mại và tuân thủ bản quyền cùng điều khoản cấp phép. [Nguồn 1]

Thông tin đối chiếu trực tiếp từ chính sách: Sinh viên hiện tại có thể truy cập tài nguyên trực tuyến từ ngoài trường bằng VinUni ID. Khi dùng máy tính công cộng, người dùng phải đóng trình duyệt sau khi hoàn tất để tránh người khác sử dụng sai tài khoản hoặc tài nguyên. Tài nguyên điện tử phải được dùng cho mục đích cá nhân, phi thương mại và tuân thủ bản quyền cùng điều khoản cấp phép. [Nguồn 1]

**Gold answer:** Đăng nhập bằng VinUni ID. Tài nguyên chỉ dùng cho mục đích cá nhân, phi thương mại và phải tuân thủ bản quyền; khi dùng máy công cộng phải đóng trình duyệt sau khi hoàn tất.

### Câu 5

**Query:** Sinh viên đã trả sách nhưng tài khoản vẫn báo quá hạn thì cần kiểm tra và xử lý theo các bước nào?

**Metadata filter:** `None`

**Điểm tự động theo rubric:** **2 / 2**

**Evidence rank:** `[1, 2]`

**Top-3:**

1. `vinuni-library-faq` — score `0.670180` — ## Đã trả sách nhưng tài khoản vẫn báo quá hạn Trước tiên, người dùng cần xác nhận sách đã được trả qua máy self-check hoặc trạm trả sách 24/7 trước khi đưa lên giá. Tiếp theo, kiểm tra email xác nhận trả sách của thư viện. Nếu tài khoản vẫ
2. `vinuni-library-faq` — score `0.591103` — # Hướng dẫn thao tác thường gặp tại thư viện ## Mượn và trả sách bằng máy Máy self-check ở tầng một hoặc tầng hai được dùng để mượn hoặc trả sách in. Máy trả sách 24/7 tại lối vào chính chỉ dùng để trả sách. ## Xem hạn trả và gia hạn Để xem
3. `vinuni-undergraduate-borrowing` — score `0.549060` — # Dịch vụ mượn tài liệu cho sinh viên đại học ## Thẻ và định mức mượn VinUniversity ID đồng thời là thẻ thư viện để mượn tài liệu hoặc thiết bị. Sinh viên đại học được mượn tối đa 3 tài liệu, mỗi tài liệu trong 2 tuần. Sách được gia hạn một

**Câu trả lời của agent:**

Sinh viên cần thực hiện các bước sau để kiểm tra và xử lý khi tài khoản vẫn báo quá hạn mặc dù đã trả sách:

1. **Xác nhận việc trả sách**: Đảm bảo rằng sách đã được trả qua máy self-check hoặc trạm trả sách 24/7 trước khi đưa lên giá. [Nguồn 1]

2. **Kiểm tra email xác nhận**: Xem lại email xác nhận trả sách từ thư viện để đảm bảo rằng việc trả sách đã được ghi nhận. [Nguồn 1]

3. **Liên hệ với nhân viên**: Nếu tài khoản vẫn chưa được cập nhật sau khi đã thực hiện hai bước trên, sinh viên cần liên hệ với nhân viên tại Information Desk để được hỗ trợ. [Nguồn 1]

Thông tin đối chiếu trực tiếp từ chính sách: Trước tiên, người dùng cần xác nhận sách đã được trả qua máy self-check hoặc trạm trả sách 24/7 trước khi đưa lên giá. Tiếp theo, kiểm tra email xác nhận trả sách của thư viện. Nếu tài khoản vẫn chưa cập nhật, liên hệ nhân viên tại Information Desk. [Nguồn 1]

**Gold answer:** Xác nhận sách đã được trả qua máy self-check hoặc trạm trả 24/7, kiểm tra email xác nhận trả sách, rồi liên hệ Information Desk nếu tài khoản vẫn chưa cập nhật.

## Phân tích metadata filter ở câu 1

- Có filter: `['vinuni-undergraduate-borrowing', 'vinuni-undergraduate-borrowing', 'vinuni-library-faq']`
- Không filter: `['vinuni-library-access-policy', 'vinuni-undergraduate-borrowing', 'vinuni-graduate-faculty-borrowing']`

## Dự đoán độ tương tự

| # | Dự đoán | Score thực tế | Nhãn thực tế | Đúng? |
|---:|---|---:|---|---|
| 1 | cao | 0.725871 | cao | Có |
| 2 | cao | 0.591021 | cao | Có |
| 3 | thấp | 0.288613 | thấp | Có |
| 4 | cao | 0.634631 | cao | Có |
| 5 | thấp | 0.207318 | thấp | Có |
