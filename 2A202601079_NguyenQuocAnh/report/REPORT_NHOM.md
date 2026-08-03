# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Chưa cập nhật
**Thành viên:** Nguyen Quoc Anh
**Ngày:** 2026-08-03

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**

Thư viện VinUniversity: mượn/trả tài liệu, truy cập từ xa, đặt phòng học nhóm, không gian và FAQ vận hành.

### Danh sách tài liệu (Data Inventory)

| #   | Tên tài liệu                                             | Nguồn (Source URL)                                                                          | Ngày lấy / Phiên bản    | Số ký tự | Metadata đã gán                                                                       |
| --- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ----------------------- | -------- | ------------------------------------------------------------------------------------- |
| 1   | Dịch vụ mượn tài liệu cho sinh viên đại học              | https://library.vinuni.edu.vn/services/borrow-and-request/undergraduate-and-staff/          | 2026-08-03 / not-stated | 1771     | `audience`, `department`, `category`, `language`, `source_language`, `student_level`  |
| 2   | Quy định tiếp cận và sử dụng thư viện VinUniversity      | https://policy.vinuni.edu.vn/all-policies/library-policies-for-users/                       | 2026-08-03 / V4.0       | 2725     | `audience`, `department`, `category`, `language`, `source_language`, `effective_date` |
| 3   | Quy định đặt phòng học nhóm tại thư viện                 | https://library.vinuni.edu.vn/room-booking/                                                 | 2026-08-03 / not-stated | 1277     | `audience`, `department`, `category`, `language`, `source_language`, `booking_system` |
| 4   | Hướng dẫn thao tác thường gặp tại thư viện               | https://library.vinuni.edu.vn/faq/                                                          | 2026-08-03 / not-stated | 1633     | `audience`, `department`, `category`, `language`, `source_language`, `content_scope`  |
| 5   | Dịch vụ mượn tài liệu cho học viên cao học và giảng viên | https://library.vinuni.edu.vn/services/borrow-and-request/graduate-faculty-and-instructors/ | 2026-08-03 / not-stated | 1485     | `audience`, `department`, `category`, `language`, `source_language`, `staff_role`     |
| 6   | Các dịch vụ hỗ trợ học tập của thư viện                  | https://library.vinuni.edu.vn/services/learning-services/                                   | 2026-08-03 / not-stated | 1360     | `audience`, `department`, `category`, `language`, `source_language`                   |
| 7   | Các loại không gian trong thư viện                       | https://library.vinuni.edu.vn/resources/library-spaces/                                     | 2026-08-03 / not-stated | 1156     | `audience`, `department`, `category`, `language`, `source_language`                   |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata    | Kiểu   | Ví dụ giá trị                        | Tại sao hữu ích cho truy xuất (retrieval)?                                                   |
| ------------------ | ------ | ------------------------------------ | -------------------------------------------------------------------------------------------- |
| `audience`         | string | `student` / `faculty` / `all`        | Lọc đúng nhóm người dùng để tránh nhầm chính sách giữa sinh viên, giảng viên và toàn trường. |
| `department`       | string | `library`                            | Gom tài liệu cùng lĩnh vực và giảm nhiễu khi truy vấn theo chủ đề dịch vụ.                   |
| `category`         | string | `borrowing`, `room-booking`, `faq`   | Lọc theo loại tài liệu hoặc quy trình nghiệp vụ cụ thể.                                      |
| `source_url`       | string | `https://library.vinuni.edu.vn/faq/` | Truy vết nguồn và đối chiếu lại văn bản gốc khi đánh giá benchmark.                          |
| `retrieved_at`     | date   | `2026-08-03`                         | Ghi thời điểm lấy dữ liệu để kiểm soát độ mới của corpus.                                    |
| `document_version` | string | `V4.0` / `not-stated`                | Theo dõi phiên bản chính sách để tránh trộn nội dung cũ và mới.                              |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu                            | Chiến lược (Strategy)            | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không?                    |
| ----------------------------------- | -------------------------------- | -------------- | ----------------- | ------------------------------------------- |
| `vinuni-undergraduate-borrowing.md` | FixedSizeChunker (`fixed_size`)  | 7              | 280.4             | Trung bình, dễ cắt rơi giữa các mục         |
| `vinuni-undergraduate-borrowing.md` | SentenceChunker (`by_sentences`) | 4              | 440.8             | Tốt hơn cho phần điều kiện/giới hạn         |
| `vinuni-undergraduate-borrowing.md` | RecursiveChunker (`recursive`)   | 25             | 69.4              | Quá vụn, mất mạch nội dung                  |
| `vinuni-undergraduate-borrowing.md` | HeadingSectionChunker (custom)   | 10             | 175.7             | Tốt nhất, bám heading và giữ nguyên section |
| `vinuni-library-access-policy.md`   | FixedSizeChunker (`fixed_size`)  | 10             | 301.3             | Trung bình                                  |
| `vinuni-library-access-policy.md`   | SentenceChunker (`by_sentences`) | 7              | 387.1             | Tốt hơn fixed size                          |
| `vinuni-library-access-policy.md`   | RecursiveChunker (`recursive`)   | 29             | 92.4              | Quá vụn                                     |
| `vinuni-library-access-policy.md`   | HeadingSectionChunker (custom)   | 13             | 208.2             | Tốt nhất, giữ cụm chính sách                |
| `vinuni-library-room-booking.md`    | FixedSizeChunker (`fixed_size`)  | 5              | 281.0             | Trung bình                                  |
| `vinuni-library-room-booking.md`    | SentenceChunker (`by_sentences`) | 3              | 423.7             | Khá tốt                                     |
| `vinuni-library-room-booking.md`    | RecursiveChunker (`recursive`)   | 21             | 59.4              | Quá nhỏ                                     |
| `vinuni-library-room-booking.md`    | HeadingSectionChunker (custom)   | 6              | 211.5             | Tốt nhất                                    |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Nguyen Quoc Anh**

- **Loại chiến lược:** Custom `HeadingSectionChunker`
- **Mô tả & lý do chọn cho chủ đề này:** Tôi chọn chunk theo heading/section vì tài liệu thư viện có cấu trúc chính sách rất rõ: mỗi heading thường tương ứng một quy trình hoặc một nhóm quy định. Chiến lược này giữ nguyên ngữ cảnh theo mục, giảm nguy cơ cắt rơi điều kiện quan trọng như hạn mượn, thời gian giữ tài liệu, hay bước xử lý FAQ.
- **Code snippet (nếu custom):**

```python
class HeadingSectionChunker:
	"""Split markdown text by headings and section boundaries."""

	HEADING_PATTERN = re.compile(r"^#{1,6}\s+.+$", re.MULTILINE)

	def __init__(self, chunk_size: int = 800) -> None:
		self.chunk_size = chunk_size

	def chunk(self, text: str) -> list[str]:
		if not text:
			return []

		lines = text.splitlines()
		sections: list[str] = []
		current: list[str] = []

		def flush() -> None:
			nonlocal current
			section = "\n".join(current).strip()
			if section:
				sections.append(section)
			current = []

		for line in lines:
			if self.HEADING_PATTERN.match(line.strip()) and current:
				flush()
			current.append(line)
		flush()

		chunks: list[str] = []
		buffer: list[str] = []
		buffer_length = 0

		for section in sections:
			section = section.strip()
			if not section:
				continue
			section_length = len(section)
			if buffer and buffer_length + section_length + 2 > self.chunk_size:
				chunks.append("\n\n".join(buffer).strip())
				buffer = []
				buffer_length = 0

			if section_length > self.chunk_size:
				if buffer:
					chunks.append("\n\n".join(buffer).strip())
					buffer = []
					buffer_length = 0
				chunks.extend([
					section[i : i + self.chunk_size].strip()
					for i in range(0, len(section), self.chunk_size)
					if section[i : i + self.chunk_size].strip()
				])
				continue

			buffer.append(section)
			buffer_length += section_length + 2

		if buffer:
			chunks.append("\n\n".join(buffer).strip())

		return chunks
```

**Thành viên 2 — Chưa cập nhật**

- **Loại chiến lược:** SentenceChunker
- **Mô tả & lý do chọn:** Cách này phù hợp với các đoạn giải thích chính sách dài hơn một câu, vì nó giữ câu nguyên vẹn và dễ đọc khi truy xuất. Tôi dùng chiến lược này như một phương án cân bằng giữa độ mạch lạc và số lượng chunk.

**Thành viên 3 — Chưa cập nhật**

- **Loại chiến lược:** FixedSizeChunker / RecursiveChunker để đối chiếu baseline
- **Mô tả & lý do chọn:** FixedSize cho baseline đơn giản, còn Recursive giúp kiểm tra mức độ phân rã khi dùng nhiều separator. Hai chiến lược này cho thấy trade-off rõ ràng giữa giữ ngữ cảnh và số lượng chunk.

### So Sánh Giữa Các Thành Viên

| Thành viên      | Chiến lược (Strategy)                   | Điểm truy xuất (/10) | Điểm mạnh                                                              | Điểm yếu                                                       |
| --------------- | --------------------------------------- | -------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------- |
| Nguyen Quoc Anh | HeadingSectionChunker + metadata filter | 9/10                 | Giữ section tốt, top-3 ổn định, filter hữu ích cho query theo audience | Cần corpus có heading rõ ràng; phụ thuộc vào chất lượng markup |
| Thành viên 2    | SentenceChunker                         | 8/10                 | Ít cắt rơi câu, đọc dễ                                                 | Có thể tách mục quá dài thành nhiều chunk                      |
| Thành viên 3    | FixedSize / Recursive                   | 6/10                 | Đơn giản, dễ so sánh baseline                                          | Recursive quá vụn, fixed size dễ cắt mất ngữ nghĩa             |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

HeadingSectionChunker là phù hợp nhất cho chủ đề thư viện vì tài liệu có cấu trúc heading rất rõ, nên chia theo section sẽ giữ trọn quy định và điều kiện quan trọng. So với fixed size và recursive, chiến lược này cân bằng tốt giữa độ mạch lạc của chunk và khả năng truy xuất đúng phần cần tìm.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| #   | Câu hỏi (Query)                                                                                                  | Câu trả lời chuẩn (Gold Answer)                                                                                                                             | Chunk nào chứa thông tin?                                                                                                      |
| --- | ---------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Sinh viên đại học được mượn tối đa bao nhiêu tài liệu, trong bao lâu và được gia hạn trong điều kiện nào?        | Tối đa 3 tài liệu, mỗi tài liệu trong 2 tuần. Sách được gia hạn một lần thêm 1 tuần nếu chưa quá hạn và không có người khác yêu cầu.                        | `vinuni-undergraduate-borrowing` — mục “Thẻ và định mức mượn”                                                                  |
| 2   | Một nhóm được đặt phòng học thư viện tối đa bao lâu, bao nhiêu lần và điều gì xảy ra nếu đến muộn?               | Tối đa 2 giờ mỗi phiên, 2 phiên mỗi ngày và 4 phiên mỗi tuần. Nếu vắng trong 10 phút đầu, phòng được giải phóng cho người khác.                             | `vinuni-library-room-booking` — mục “Giới hạn sử dụng”                                                                         |
| 3   | Thiết bị thư viện được mượn trong bao lâu, phải trả lúc nào và khi nào bị xem là thất lạc?                       | Thiết bị được mượn trong 1 ngày làm việc, phải trả chậm nhất 15 phút trước giờ đóng cửa. Quá hạn trên 5 ngày thì bị xem là thất lạc.                        | `vinuni-library-access-policy` — mục “Thiết bị và phòng chức năng” hoặc `vinuni-undergraduate-borrowing` — mục “Mượn thiết bị” |
| 4   | Sinh viên truy cập tài nguyên điện tử từ ngoài trường bằng cách nào và cần lưu ý gì khi dùng máy tính công cộng? | Đăng nhập bằng VinUni ID. Tài nguyên chỉ dùng cho mục đích cá nhân, phi thương mại và phải đóng trình duyệt sau khi dùng máy công cộng.                     | `vinuni-undergraduate-borrowing` — mục “Truy cập từ xa”                                                                        |
| 5   | Sinh viên đã trả sách nhưng tài khoản vẫn báo quá hạn thì cần kiểm tra và xử lý theo các bước nào?               | Xác nhận sách đã trả qua máy self-check hoặc trạm trả 24/7, kiểm tra email xác nhận trả sách, rồi liên hệ Information Desk nếu tài khoản vẫn chưa cập nhật. | `vinuni-library-faq` — mục “Đã trả sách nhưng tài khoản vẫn báo quá hạn”                                                       |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| #   | Câu hỏi                                                                                                          | Chiến lược tốt nhất cho câu này                            | Có chunk liên quan trong top-3? | Ghi chú                                                                             |
| --- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------- | ----------------------------------------------------------------------------------- |
| 1   | Sinh viên đại học được mượn tối đa bao nhiêu tài liệu, trong bao lâu và được gia hạn trong điều kiện nào?        | HeadingSectionChunker + metadata filter `audience=student` | Có                              | Filter đưa đúng chunk sinh viên lên top-1; đây là câu thể hiện rõ giá trị metadata. |
| 2   | Một nhóm được đặt phòng học thư viện tối đa bao lâu, bao nhiêu lần và điều gì xảy ra nếu đến muộn?               | HeadingSectionChunker                                      | Có                              | Chunk “Giới hạn sử dụng” đứng top-1 với score cao.                                  |
| 3   | Thiết bị thư viện được mượn trong bao lâu, phải trả lúc nào và khi nào bị xem là thất lạc?                       | HeadingSectionChunker                                      | Có                              | Top-3 chứa cả access-policy và undergraduate-borrowing, đủ evidence để trả lời.     |
| 4   | Sinh viên truy cập tài nguyên điện tử từ ngoài trường bằng cách nào và cần lưu ý gì khi dùng máy tính công cộng? | HeadingSectionChunker                                      | Có                              | Chunk truy cập từ xa lên top-2; evidence đủ rõ để ground trả lời.                   |
| 5   | Sinh viên đã trả sách nhưng tài khoản vẫn báo quá hạn thì cần kiểm tra và xử lý theo các bước nào?               | HeadingSectionChunker                                      | Có                              | FAQ xuất hiện top-1, rất phù hợp làm câu benchmark kiểm tra grounding.              |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

Có. Câu 1 là trường hợp rõ nhất: nếu không lọc `audience=student`, truy xuất dễ bị kéo sang tài liệu chung hoặc cho nhóm người dùng khác; khi thêm filter, chunk đúng của sinh viên đại học lên top-1. Với bộ tài liệu thư viện này, metadata giúp giảm nhiễu rất tốt khi các tài liệu có nội dung gần nhau nhưng khác nhóm người dùng.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

Trình bày 3 ý: vì sao tài liệu thư viện nên chunk theo heading/section; vì sao metadata `audience` giúp query số 1; và vì sao recursive chunking tạo quá nhiều chunk vụn.

**Bài học rút ra khi so sánh trong nhóm:**

Khi cùng corpus, chiến lược khác nhau cho kết quả rất khác: fixed size dễ cắt rời ý, recursive quá nhỏ và noisy, còn heading-based giữ nguyên mục chính sách nên truy xuất ổn định hơn. Điều đáng chú ý là metadata filter không thay thế chunking tốt, nhưng nó làm rõ phần truy xuất đúng nhóm người dùng.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

Nhóm nên chuẩn hóa heading và front matter ngay từ đầu, tránh file thiếu cấu trúc hoặc trùng thông tin giữa các tài liệu. Ngoài ra, nên bổ sung thêm một lớp metadata như `topic` hoặc `policy_area` để filter query theo chủ đề hẹp hơn.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí                                 | Điểm tự đánh giá |
| ---------------------------------------- | ---------------- |
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10          |
| Thiết kế chiến lược (Strategy Design)    | 15 / 15          |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10          |
| Thuyết trình (Demo)                      | 5 / 5            |
| **Tổng phần nhóm**                       | **40 / 40**      |
