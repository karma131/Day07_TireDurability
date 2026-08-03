# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** TireDurability
**Thành viên:** Nguyễn Ngọc Ánh, Trương Quốc Trường, Nguyễn Hoàng Vĩnh Phong, Đào Văn Đà, Nguyễn Quốc Anh
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Dịch vụ thư viện VinUniversity dành cho sinh viên, tập trung vào quyền mượn tài liệu, truy cập tài nguyên, đặt phòng, không gian và hỗ trợ học tập.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy định tiếp cận và sử dụng thư viện VinUniversity | [VinUni Policy](https://policy.vinuni.edu.vn/all-policies/library-policies-for-users/) | 2026-08-03 / V4.0 | 2.370 | `audience=all`, `category=access-policy` |
| 2 | Dịch vụ mượn tài liệu cho sinh viên đại học | [VinUni Library](https://library.vinuni.edu.vn/services/borrow-and-request/undergraduate-and-staff/) | 2026-08-03 / not-stated | 1.401 | `audience=student`, `category=borrowing` |
| 3 | Dịch vụ mượn tài liệu cho học viên cao học và giảng viên | [VinUni Library](https://library.vinuni.edu.vn/services/borrow-and-request/graduate-faculty-and-instructors/) | 2026-08-03 / not-stated | 1.090 | `audience=faculty`, `category=borrowing` |
| 4 | Quy định đặt phòng học nhóm tại thư viện | [VinUni Library](https://library.vinuni.edu.vn/room-booking/) | 2026-08-03 / not-stated | 948 | `audience=all`, `category=room-booking` |
| 5 | Các dịch vụ hỗ trợ học tập của thư viện | [VinUni Library](https://library.vinuni.edu.vn/services/learning-services/) | 2026-08-03 / not-stated | 1.013 | `audience=all`, `category=learning-support` |
| 6 | Các loại không gian trong thư viện | [VinUni Library](https://library.vinuni.edu.vn/resources/library-spaces/) | 2026-08-03 / not-stated | 831 | `audience=all`, `category=library-spaces` |
| 7 | Hướng dẫn thao tác thường gặp tại thư viện | [VinUni Library](https://library.vinuni.edu.vn/faq/) | 2026-08-03 / not-stated | 1.307 | `audience=student`, `category=self-service-help` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | Chuỗi | `vinuni-undergraduate-borrowing` | Định danh duy nhất, truy vết và xóa toàn bộ chunk của một tài liệu. |
| `title` | Chuỗi | `Dịch vụ mượn tài liệu cho sinh viên đại học` | Hiển thị nguồn dễ hiểu và hỗ trợ nhận diện nội dung chunk. |
| `source_url` | URL dạng chuỗi | `https://library.vinuni.edu.vn/...` | Kiểm chứng câu trả lời tại nguồn công khai ban đầu. |
| `retrieved_at` | Ngày ISO | `2026-08-03` | Cho biết thời điểm nhóm lấy và kiểm tra dữ liệu. |
| `document_version` | Chuỗi | `V4.0`, `not-stated` | Ưu tiên chính sách mới và phát hiện thông tin có nguy cơ lỗi thời. |
| `audience` | Enum dạng chuỗi | `student`, `faculty`, `all` | Lọc đúng nhóm người dùng; tránh nhầm quyền mượn sinh viên đại học với cao học/giảng viên. |
| `department` | Chuỗi | `library` | Giới hạn retrieval vào đúng đơn vị cung cấp dịch vụ. |
| `category` | Enum dạng chuỗi | `borrowing`, `room-booking` | Thu hẹp tìm kiếm theo loại dịch vụ và giảm chunk nhiễu. |
| `language` | Chuỗi | `vi` | Chọn corpus phù hợp ngôn ngữ câu hỏi và mô hình embedding. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Quy định tiếp cận và sử dụng thư viện | FixedSizeChunker (`fixed_size`) | 5 | 473,8 | Trung bình; một số câu/điều kiện bị cắt tại mốc 500 ký tự. |
| Quy định tiếp cận và sử dụng thư viện | SentenceChunker (`by_sentences`) | 9 | 261,4 | Tốt; giữ trọn câu nhưng tạo nhiều chunk hơn. |
| Quy định tiếp cận và sử dụng thư viện | RecursiveChunker (`recursive`) | 7 | 336,7 | Tốt; ưu tiên ranh giới đoạn, dòng và câu. |
| Dịch vụ mượn cho sinh viên đại học | FixedSizeChunker (`fixed_size`) | 3 | 466,7 | Trung bình; có ranh giới cắt giữa hai mục. |
| Dịch vụ mượn cho sinh viên đại học | SentenceChunker (`by_sentences`) | 5 | 278,4 | Tốt; các điều kiện mượn và gia hạn nằm trọn câu. |
| Dịch vụ mượn cho sinh viên đại học | RecursiveChunker (`recursive`) | 3 | 465,3 | Tốt; gần kích thước mục và vẫn dưới giới hạn. |
| Quy định đặt phòng học nhóm | FixedSizeChunker (`fixed_size`) | 2 | 473,5 | Trung bình; điều kiện đến muộn nằm qua ranh giới chunk. |
| Quy định đặt phòng học nhóm | SentenceChunker (`by_sentences`) | 4 | 235,2 | Tốt; giữ nguyên từng quy tắc đặt phòng. |
| Quy định đặt phòng học nhóm | RecursiveChunker (`recursive`) | 2 | 472,5 | Tốt; tách theo đoạn/mục tự nhiên. |

Số liệu trên được chạy với `ChunkingStrategyComparator().compare(text, chunk_size=500)` trên ba tài liệu đại diện. Comparator dùng fixed-size không overlap để so sánh cấu trúc; benchmark cá nhân bên dưới dùng đúng cấu hình được phân công là overlap 50.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Nguyễn Ngọc Ánh**
- **Nhiệm vụ chính:** Tổng hợp dữ liệu và chạy baseline.
- **Loại chiến lược:** FixedSize — `FixedSizeChunker(chunk_size=500, overlap=50)`.
- **Mô tả & lý do chọn cho chủ đề này:** Đây là đường cơ sở đơn giản và dễ tái lập để đo tác động của các chiến lược khác. Kích thước 500 ký tự giữ được lượng thông tin vừa đủ cho một đoạn quy định, còn overlap 50 giúp giảm nguy cơ mất điều kiện nằm sát ranh giới chunk.
- **Thiết lập đánh giá:** Local embedding `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, corpus 7 tài liệu được chia thành 22 chunks, cùng 5 query chuẩn của nhóm.
- **Kết quả cá nhân:** Cả 5/5 query có chunk liên quan trong top-3 và top-1 đều thuộc đúng tài liệu mục tiêu. Điểm theo rubric là **9/10**: bốn câu đầy đủ đạt 2 điểm/câu; câu đặt phòng đạt 1 điểm vì chunk top-1 bị cắt trước điều kiện đến muộn 10 phút.
- **Failure case:** Với query đặt phòng, top-1 đạt 0,6881 và chứa giới hạn 2 giờ/phiên, 2 phiên/ngày, 4 phiên/tuần, nhưng thiếu hậu quả khi đến muộn. Điều này cho thấy overlap 50 chưa bảo đảm mọi điều kiện sát ranh giới đều cùng xuất hiện trong top-3.

**Trương Quốc Trường**
- **Nhiệm vụ chính:** Kiểm tra dữ liệu và metadata.
- **Loại chiến lược:** `FixedSizeChunker(chunk_size=350, overlap=80)`.
- **Mô tả & lý do chọn:** Kích thước 350 ký tự phù hợp với các đoạn quy định dịch vụ tương đối ngắn, giúp chunk tập trung và hạn chế nhiễu. Overlap 80 ký tự được dùng để giữ lại ngữ cảnh quanh ranh giới, giảm nguy cơ cắt rời từ khóa hoặc điều kiện quan trọng giữa hai chunk liên tiếp.
- **Kết quả cung cấp:** **8/10 theo file kết quả của thành viên**.
- **Điểm mạnh:** Cấu hình đơn giản, xử lý nhanh; overlap tương đối lớn giúp bù đắp nhược điểm cắt theo số ký tự.
- **Điểm yếu:** Nội dung ở vùng overlap bị lặp lại và chiến lược vẫn có thể cắt ngang một ý hoặc một câu dài.
- **Lưu ý tính so sánh:** File kết quả của thành viên sử dụng thêm câu hỏi về đăng ký học phần và một số câu khác với bộ 5 câu hỏi đánh giá chung do nhóm thống nhất. Báo cáo giữ nguyên điểm thành viên cung cấp nhưng không dùng riêng điểm này để kết luận chiến lược nào tốt hơn; một thực nghiệm kiểm soát cần sử dụng cùng bộ dữ liệu, câu hỏi và mô hình embedding.
- **Cấu hình:**

```python
fixed_chunker = FixedSizeChunker(chunk_size=350, overlap=80)
```

**Nguyễn Hoàng Vĩnh Phong**
- **Nhiệm vụ chính:** Thiết kế benchmark và gold answer.
- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=3)`.
- **Mô tả & lý do chọn:** Chiến lược tách văn bản theo ranh giới câu rồi gom ba câu liên tiếp thành một chunk. Cách này giữ nguyên cấu trúc ngữ pháp và ý nghĩa của từng câu quy định, tránh lỗi cắt đôi câu như fixed-size baseline.
- **Kết quả cung cấp:** **8,5/10**; các chunk liên quan đều xuất hiện trong top-3, nhưng một số nằm ở top-2 thay vì top-1.
- **Điểm mạnh:** Nội dung dễ đọc, không ngắt giữa câu và phù hợp với các đoạn giải thích chính sách dài nhiều câu.
- **Điểm yếu:** Không bám trực tiếp theo heading `##`; một mục dài có thể bị chia sang nhiều chunk và làm evidence tụt xuống top-2.
- **Lưu ý tính so sánh:** Bộ câu hỏi trong file kết quả của thành viên có cách diễn đạt và nội dung khác bộ 5 câu hỏi đánh giá chung do nhóm thống nhất ở nhiều câu. Báo cáo giữ nguyên điểm 8,5/10 do thành viên cung cấp, đồng thời không xem chênh lệch điểm này là bằng chứng độc lập rằng một chiến lược chia đoạn tốt hơn chiến lược khác.

**Đào Văn Đà (2A202601089)**
- **Nhiệm vụ chính:** Chạy đánh giá và tổng hợp score.
- **Loại chiến lược:** `RecursiveChunker(chunk_size=500)`.
- **Mô tả & lý do chọn:** RecursiveChunker ưu tiên ranh giới đoạn, dòng và câu trước khi cắt theo từ hoặc ký tự. Với corpus chính sách/FAQ có cấu trúc rõ, cấu hình này cân bằng độ mạch lạc của chunk với giới hạn 500 ký tự.
- **Thiết lập đánh giá:** 7 tài liệu, 23 chunks, độ dài trung bình 387,87 ký tự, chunk dài nhất 493 ký tự; embedding `text-embedding-3-small`, agent dùng `gpt-4o-mini` và sinh câu trả lời một lượt.
- **Kết quả cá nhân:** **10/10**; cả 5 query có evidence đúng ở top-1 và agent trả lời đủ gold answer. Evidence rank lần lượt là `[1, 2]`, `[1]`, `[1, 2, 3]`, `[1]`, `[1, 2]`.
- **Metadata filter:** Ở câu 1, khi có `audience=student`, top-3 gồm hai chunk `vinuni-undergraduate-borrowing` và một chunk FAQ. Khi bỏ filter, top-1 chuyển thành `vinuni-library-access-policy`, còn tài liệu đúng cho sinh viên đại học xuống top-2 và tài liệu cao học/giảng viên xuất hiện ở top-3.
- **Failure case:** Vector similarity nhận diện tốt chủ đề “mượn tài liệu” nhưng không tự phân biệt chắc chắn đối tượng áp dụng. Tiền lọc `audience` là cần thiết để ưu tiên đúng chính sách sinh viên.

**Nguyễn Quốc Anh**
- **Nhiệm vụ chính:** Báo cáo, slide và phân tích lỗi.
- **Loại chiến lược:** Custom `HeadingSectionChunker(chunk_size=800)` kết hợp metadata filter.
- **Mô tả & lý do chọn cho chủ đề này:** Tài liệu thư viện có cấu trúc Markdown rõ ràng, trong đó mỗi heading thường tương ứng một quy trình hoặc nhóm quy định. Chia theo heading/section giúp giữ nguyên ngữ cảnh của từng mục, giảm nguy cơ cắt rơi các điều kiện quan trọng như hạn mượn, thời gian giữ tài liệu hoặc các bước xử lý FAQ.
- **Kết quả cá nhân:** Đạt **9/10** theo báo cáo thực nghiệm của thành viên; top-3 ổn định và metadata filter hỗ trợ tốt cho query phân biệt theo `audience`.
- **Điểm mạnh:** Chunk mạch lạc, giữ đúng cấu trúc mục và phù hợp với corpus có heading chuẩn.
- **Điểm yếu:** Phụ thuộc vào chất lượng Markdown; tài liệu thiếu hoặc dùng heading không nhất quán sẽ làm giảm hiệu quả.
- **Code snippet:**

```python
import re


class HeadingSectionChunker:
    """Split Markdown text by headings and section boundaries."""

    HEADING_PATTERN = re.compile(r"^#{1,6}\s+.+$", re.MULTILINE)

    def __init__(self, chunk_size: int = 800) -> None:
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        sections: list[str] = []
        current: list[str] = []

        def flush() -> None:
            nonlocal current
            section = "\n".join(current).strip()
            if section:
                sections.append(section)
            current = []

        for line in text.splitlines():
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
                chunks.extend(
                    section[start : start + self.chunk_size].strip()
                    for start in range(0, len(section), self.chunk_size)
                    if section[start : start + self.chunk_size].strip()
                )
                continue

            buffer.append(section)
            buffer_length += section_length + 2

        if buffer:
            chunks.append("\n\n".join(buffer).strip())
        return chunks
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Ngọc Ánh | FixedSizeChunker (`chunk_size=500`, `overlap=50`) | 9/10 | Đơn giản, nhanh, tái lập tốt; 5/5 query có evidence trong top-3. | Có thể cắt rời điều kiện chính sách; câu đặt phòng thiếu quy tắc đến muộn 10 phút. |
| Nguyễn Quốc Anh | HeadingSectionChunker (`chunk_size=800`) + metadata filter | 9/10 | Giữ section tốt, top-3 ổn định; filter hữu ích cho query theo `audience`. | Cần corpus có heading rõ ràng và markup nhất quán. |
| Trương Quốc Trường | FixedSizeChunker (`chunk_size=350`, `overlap=80`) | 8/10 (theo file thành viên) | Xử lý nhanh; overlap giữ thêm ngữ cảnh tại ranh giới chunk. | Có nội dung lặp, vẫn có thể cắt ngang ý và bộ query báo cáo chưa đồng nhất hoàn toàn. |
| Nguyễn Hoàng Vĩnh Phong | SentenceChunker (`max_sentences_per_chunk=3`) | 8,5/10 (theo file thành viên) | Không cắt đôi câu; chunk dễ đọc và có evidence trong top-3. | Nhiều evidence ở top-2 và bộ query báo cáo chưa đồng nhất hoàn toàn. |
| Đào Văn Đà | RecursiveChunker (`chunk_size=500`) | 10/10 | 5/5 evidence ở top-1; agent trả lời đầy đủ; chunk giữ ranh giới đoạn tốt. | Dùng embedding/LLM khác Nguyễn Ngọc Ánh nên chưa thể quy toàn bộ chênh lệch điểm cho chunking. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Trong các kết quả hiện có, `RecursiveChunker(chunk_size=500)` của Đào Văn Đà đạt điểm cao nhất (10/10), nhờ giữ được ranh giới đoạn và đưa evidence đúng lên top-1 cho cả 5 câu. Tuy nhiên, Đào Văn Đà dùng `text-embedding-3-small` và `gpt-4o-mini`, trong khi baseline của Nguyễn Ngọc Ánh dùng local multilingual embedding; các file của Trương Quốc Trường và Nguyễn Hoàng Vĩnh Phong cũng chưa dùng hoàn toàn cùng bộ query. Vì vậy, kết quả cho thấy RecursiveChunker có triển vọng tốt nhất trên corpus này nhưng chưa cô lập hoàn toàn tác động riêng của chunking. Một so sánh nhân quả cần cố định corpus, năm query, embedding backend, `top_k` và LLM.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên đại học được mượn tối đa bao nhiêu tài liệu, trong bao lâu và được gia hạn trong điều kiện nào? | Tối đa 3 tài liệu trong 2 tuần; gia hạn một lần thêm 1 tuần nếu chưa quá hạn và không có người khác yêu cầu. | `vinuni-undergraduate-borrowing`, mục “Thẻ và định mức mượn” |
| 2 | Một nhóm được đặt phòng học thư viện tối đa bao lâu, bao nhiêu lần và điều gì xảy ra nếu đến muộn? | Tối đa 2 giờ/phiên, 2 phiên/ngày và 4 phiên/tuần; có thể đặt trước tối đa 1 tuần; vắng 10 phút thì phòng được giải phóng. | `vinuni-library-room-booking`, mục “Giới hạn sử dụng”; `vinuni-library-access-policy`, mục “Thiết bị và phòng chức năng” |
| 3 | Thiết bị thư viện được mượn trong bao lâu, phải trả lúc nào và khi nào bị xem là thất lạc? | Mượn 1 ngày làm việc, trả trực tiếp tại quầy tầng một trước giờ đóng cửa 15 phút; quá hạn trên 5 ngày được xem là thất lạc và phải trả chi phí thay thế. | `vinuni-library-access-policy`, mục “Thiết bị và phòng chức năng”; `vinuni-undergraduate-borrowing`, mục “Mượn thiết bị” |
| 4 | Sinh viên truy cập tài nguyên điện tử từ ngoài trường bằng cách nào và cần lưu ý gì khi dùng máy tính công cộng? | Đăng nhập bằng VinUni ID; chỉ dùng cho mục đích cá nhân, phi thương mại, tuân thủ bản quyền và đóng trình duyệt sau khi dùng máy công cộng. | `vinuni-undergraduate-borrowing`, mục “Truy cập từ xa” |
| 5 | Sinh viên đã trả sách nhưng tài khoản vẫn báo quá hạn thì cần kiểm tra và xử lý theo các bước nào? | Xác nhận đã trả qua máy self-check hoặc trạm trả 24/7, kiểm tra email xác nhận, rồi liên hệ Information Desk nếu tài khoản chưa cập nhật. | `vinuni-library-faq`, mục “Đã trả sách nhưng tài khoản vẫn báo quá hạn” |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Quyền mượn và gia hạn của sinh viên đại học | RecursiveChunker + filter `audience=student` | Có — top-1 và top-2 | Agent trả lời đúng; filter loại nhiễu từ chính sách chung và nhóm cao học/giảng viên. |
| 2 | Giới hạn đặt phòng và xử lý đến muộn | RecursiveChunker | Có — top-1 | Top-2 policy bổ sung điều kiện hủy khi đến muộn 10 phút; agent trả lời đầy đủ. |
| 3 | Thời hạn mượn và xử lý thiết bị thất lạc | RecursiveChunker | Có — top-1, top-2 và top-3 | Top-1 score 0,674056; context chứa đủ thời hạn, nơi trả và điều kiện quá hạn. |
| 4 | Truy cập tài nguyên điện tử từ ngoài trường | RecursiveChunker | Có — top-1 | Top-1 score 0,717796; agent nêu đủ VinUni ID, đóng trình duyệt và sử dụng phi thương mại. |
| 5 | Đã trả sách nhưng vẫn báo quá hạn | RecursiveChunker | Có — top-1 và top-2 | Top-1 score 0,670180; agent trả lời đúng đủ ba bước xử lý. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, rõ nhất ở câu 1. Khi dùng `metadata_filter={"audience": "student"}`, hai kết quả đầu đều thuộc `vinuni-undergraduate-borrowing`; khi bỏ filter, `vinuni-library-access-policy` lên top-1 và tài liệu cao học/giảng viên xuất hiện trong top-3. Điều này chứng minh metadata filter giảm nhiễu khi nhiều tài liệu cùng nói về mượn và gia hạn nhưng áp dụng cho đối tượng khác nhau.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

1. **Metadata filter có tác động đo được:** ở câu 1, nếu không lọc thì policy chung đứng top-1 với score 0,787714, tài liệu sinh viên đại học đứng top-2 với 0,689121 và tài liệu cao học/giảng viên đứng top-3 với 0,677253. Khi lọc `audience=student`, tài liệu sinh viên đại học chiếm top-1 và top-2.
2. **Tìm đúng tài liệu chưa chắc đủ điều kiện:** baseline fixed-size của Nguyễn Ngọc Ánh đưa tài liệu đặt phòng lên top-1 nhưng cắt rời quy tắc đến muộn 10 phút. Recursive của Đào Văn Đà lấy thêm policy bổ sung ở top-2 nên agent trả lời đủ.
3. **Cần kiểm soát biến khi so sánh:** strategy, embedding model và LLM đều có thể làm thay đổi score. Kết quả 10/10 của Recursive rất tốt nhưng cần chạy lại trên cùng embedding backend với các thành viên khác để so sánh chunking công bằng.

**Bài học rút ra khi so sánh trong nhóm:**
> Trên cùng corpus, fixed-size đơn giản và ổn định nhưng có nguy cơ cắt đôi một điều kiện, còn recursive bám ranh giới đoạn tốt hơn và tạo context đầy đủ hơn cho agent. Heading-based có tiềm năng giữ trọn section nhưng phụ thuộc mạnh vào chất lượng markup. Metadata filter không thay thế chunking tốt, song là lớp bảo vệ cần thiết khi các tài liệu có từ khóa giống nhau nhưng áp dụng cho các nhóm người dùng khác nhau.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ chuẩn hóa heading và bổ sung metadata cấp section như `policy_area`, `section_type` hoặc `user_group` ngay từ lúc làm sạch dữ liệu. Nhóm cũng sẽ cố định một embedding model, cùng `top_k` và cùng cơ chế sinh câu trả lời cho mọi thành viên; sau đó chỉ thay đổi chunker để đánh giá công bằng tác động của từng chiến lược.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 14 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **39 / 40** |
