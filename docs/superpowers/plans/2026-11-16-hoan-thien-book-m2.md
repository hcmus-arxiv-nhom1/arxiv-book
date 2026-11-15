# Kế hoạch hoàn thiện Book M2

**Mục tiêu:** Cập nhật Book theo kết quả M2 chính thức và QA đối chiếu source mới, giữ rõ phạm vi và giới hạn của từng phép đo.

**Nguồn yêu cầu:** https://hcmus-cs-ta.github.io/lab-book/intro-ds/statement/parsing/

**Bằng chứng:** M2 `m2-full-01`; QA toàn bảng `qa-full-01`; QA đối chiếu source `qa-thien-01` tại https://drive.google.com/drive/folders/1f6AsmOwSaq70vcgoRWUsbKZbfrfhI2Ye. Kết quả mới: 1.114 paper có source, 2.407 parsed version được so sánh; 22.625 parsed version ngoài phạm vi bị bỏ qua. Agreement counts headings 2357, formulas 2147, floats 2352, items 2342. Đây là kiểm tra số lượng theo version, không phải điểm chính xác ngữ nghĩa; một run multi-version không đại diện toàn corpus. Manual review pending.

## Công việc

- [ ] Kiểm tra `identity.json`, `qa_status.json`, `structure_summary.json` và CSV chi tiết cùng thuộc `qa-thien-01`, đối chiếu tổng số/rates và output `m2-full-01`. Lưu bằng chứng cần thiết trong `data/m2/` theo quy ước Book, kèm provenance và link Drive; không thay thế bằng chứng QA toàn bảng.
- [ ] Sửa `m2/index.md`, `m2/02-data-stats.ipynb`, `m2/04-quality.ipynb` để trình bày riêng: QA toàn bảng 20.000 paper; so sánh source subset multi-Thiện 1.114 paper/2.407 version; mẫu lịch sử 100 paper/121 version; human score sheet chưa hoàn tất. Không ghi là QA source toàn corpus hoặc diễn giải agreement là accuracy.
- [ ] Tạo bảng và biểu đồ từ CSV/JSON lúc build: tỷ lệ agreement theo bốn loại và số lượng version trong phạm vi; làm rõ mẫu chọn theo run, regex và các nguyên nhân đếm lệch, không khẳng định nguyên nhân nếu chưa xác minh. Bảo đảm phân biệt các mẫu ở mọi chú thích và tiêu đề.
- [ ] Rà `m2/01-methodology.md` đối chiếu code và output thực, đặc biệt phát biểu version không TeX xuất hiện như root trong hierarchy; sửa nếu không đúng. Rà số liệu coverage, trước/sau dedup, recovery BBL, thời gian và RAM trong các trang còn lại với bằng chứng gốc và yêu cầu TA.
- [ ] Quyết định trình bày kết quả đọc 30 paper lịch sử như quan sát chưa chấm; không tính điểm hoặc mô tả là đánh giá con người hoàn tất. Nếu nhóm muốn có điểm, người đọc phải điền score sheet trước khi công bố.
- [ ] Build toàn bộ Jupyter Book theo README và kiểm tra notebook thực thi, link, dữ liệu và provenance; đối chiếu tổng 20.000 paper, 26.491 version và 200 shard. Kiểm tra biểu đồ Plotly trực tiếp trong browser (hover/zoom và bố cục), đồng thời nêu rõ nếu môi trường không cho phép.
- [ ] Review diff, chạy các kiểm tra của repo và tạo PR để thành viên phụ trách Book duyệt. Không chạy lại parser, benchmark hay restore toàn corpus.
