# Đóng góp Báo cáo Nhóm — Thành viên 4

**Thành viên:** Đào Văn Đa (2A202601089)

**Chiến lược:** `RecursiveChunker(chunk_size=500)`

RecursiveChunker ưu tiên ranh giới đoạn, dòng và câu trước khi cắt theo từ hoặc ký tự. Với corpus chính sách/FAQ có cấu trúc rõ, lựa chọn này cân bằng độ mạch lạc và giới hạn kích thước 500 ký tự.

## Thống kê

- Số tài liệu: 7
- Số chunk: 23
- Độ dài trung bình: 387.87 ký tự
- Chunk dài nhất: 493 ký tự

## Kết quả benchmark

| Câu | Evidence rank | Điểm | Top-1 |
|---:|---|---:|---|
| 1 | `[1, 2]` | 2 / 2 | `vinuni-undergraduate-borrowing` |
| 2 | `[1]` | 2 / 2 | `vinuni-library-room-booking` |
| 3 | `[1, 2, 3]` | 2 / 2 | `vinuni-library-access-policy` |
| 4 | `[1]` | 2 / 2 | `vinuni-undergraduate-borrowing` |
| 5 | `[1, 2]` | 2 / 2 | `vinuni-library-faq` |

**Tổng:** **10 / 10**

## Metadata filter và failure case

Câu 1 có tài liệu gây nhiễu dành cho cao học/giảng viên. Top-3 có filter: `['vinuni-undergraduate-borrowing', 'vinuni-undergraduate-borrowing', 'vinuni-library-faq']`; không filter: `['vinuni-library-access-policy', 'vinuni-undergraduate-borrowing', 'vinuni-graduate-faculty-borrowing']`.
