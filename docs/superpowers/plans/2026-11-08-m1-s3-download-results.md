# Kế hoạch bổ sung benchmark tải S3 vào book M1

**Mục tiêu:** Báo cáo lần tải 144 bundle trong mục Performance, với provenance và phạm vi đo rõ ràng.

**Nguồn:** `final_evidence/s3-download-benchmark/bulk-plan-01/{plan.json,summary.json,events.jsonl,bundles.csv}` tại workspace. M1 Performance hiện ở `m1/03-performance.ipynb`. Đây là lần tải ngày 08/11/2026 sau các phiên crawl M1, không phải measurement của lượt chuẩn bị bulk trước các phiên đó.

## 1. Kiểm chứng và chuẩn hóa evidence

- [ ] Đối chiếu summary, events, CSV và plan: 144 key duy nhất, trạng thái `downloaded`, phạm vi 20.000 ID, tổng bytes, số bundle và manifest/snapshot hashes. Phát hiện mâu thuẫn phải báo lỗi, không tự suy diễn.
- [ ] Trích xuất bản CSV gọn theo bundle và summary CSV/JSON vào `data/m1/` theo mẫu hiện có. Lưu SHA-256 của bốn file đầu vào, revision `d4a92cd0192950e7bb3a8abc60ceba9da335d255`, phạm vi, timestamp và tên run; không đưa secrets hoặc đường dẫn cá nhân không cần thiết vào book.
- [ ] Giữ số nguyên bytes và thời gian gốc trong dữ liệu; chỉ làm tròn số giây khi hiển thị. Kiểm tra `resource_errors`, giá trị thiếu, 144 chênh lệch size và sự nhất quán trạng thái; không ghi khẳng định kiểm MD5 sau copy lên Drive.

## 2. Trình bày trong Performance

- [ ] Thêm một tiểu mục đánh số phù hợp trong `m1/03-performance.ipynb`, cập nhật đánh số tiếp theo nếu cần. Bảng tóm tắt có chú thích dưới chân, mở rộng phù hợp và cuộn ngang khi cần: ID, số bundle tải mới/dùng lại/lỗi, bytes thực tế và manifest, session wall, thời gian chọn, download, MD5, copy, throughput, peak RSS và stage disk.
- [ ] Trình bày session wall 1.913 giây (~31 phút 53 giây); download 1.136 giây, MD5 230 giây, copy 507 giây và phần còn lại xấp xỉ 40 giây. Selection ~4 giây đo riêng trước session. Throughput tải có trọng số = tổng bytes tải mới / tổng download seconds (~67,5 MB/s); throughput toàn phiên (~40,1 MB/s) dùng session wall. Không tính lại thời gian copy hoặc cộng các thành phần hai lần.
- [ ] Thêm biểu đồ thanh chồng cho các khoảng thời gian được đo và phần còn lại, với nhãn giây nguyên, nêu rõ selection không nằm trong session wall. Thêm phân phối thời gian mỗi bundle nếu biểu đồ thực sự giúp nhận ra biến thiên; không dùng tổng throughput từng bundle để tính tốc độ chung.
- [ ] Nêu sampler RSS là process tree, disk là thư mục local staging, 2 giây/lần và có thể bỏ sót đỉnh; không phải dung lượng Drive. Dùng caption dưới chân mỗi bảng và giới hạn wrap như các bảng hiện có.

## 3. Phạm vi và mối liên hệ với crawl

- [ ] Tính thêm một **ước lượng end-to-end** gồm thời gian benchmark tải S3 và khoảng thời gian nhóm crawl trên timeline chung. Dùng `session_wall_s` chưa làm tròn của lượt tải cộng với khoảng thời gian từ sampler crawl sớm nhất tới sampler crawl muộn nhất; không cộng tổng duration của các session crawl chồng lấn và không cộng lại retry, checkpoint hay copy vốn đã nằm trong thời gian được đo. Làm tròn giây khi hiển thị.
- [ ] Ghi rõ lần tải S3 này là lượt chạy lại có benchmark; lần tải raw trước khi crawl chưa có audit benchmark. Vì lượt đo mới diễn ra sau crawl, kết quả cộng là **ước lượng ghép từ hai lần đo**, không phải wall-clock quan sát liên tục của lượt M1 gốc. Không xác nhận tốc độ tải cũ bằng tốc độ lượt này.
- [ ] Giữ riêng các khoảng chưa đo: setup/mount, `selection_s` (báo riêng khoảng 4 giây), lấy manifest/snapshot, tải evidence và các bước khác ngoài sampler; không gọi ước lượng này là toàn bộ thời gian thực tế không thiếu bước. Nếu `selection_s` được tính thêm trong một chỉ số mở rộng, ghi công thức rõ ràng và không tính hai lần.
- [ ] Giải thích MD5 xác minh file local trước copy; kích thước khác manifest không tự chứng minh hỏng nếu MD5 khớp. Copy/rename qua Drive FUSE không chứng minh đồng bộ bền vững. Manifest boundaries là candidate, không xác nhận nội dung member hoặc version; chưa có member-index hoặc readback độc lập.
- [ ] Nếu cập nhật `m1/04-discussion.md`, chỉ thêm liên kết và giới hạn ngắn gọn; không lặp chi tiết benchmark trong Attempts & Effort. Giữ nguyên các thay đổi timing audit đang có ở local và các cập nhật M2 trên main.

## 4. Xác minh và bàn giao

- [ ] Chạy kiểm tra trích xuất trên evidence thật; đối chiếu output tổng với summary và events, kiểm tra đơn vị, mẫu số và hash. Xác nhận bảng, biểu đồ và chú thích có trong build; chạy các test hiện có và build/execution book khi môi trường hỗ trợ.
- [ ] Báo rõ kết quả kiểm tra và mọi giới hạn build, chưa commit/push nếu chưa được yêu cầu.
