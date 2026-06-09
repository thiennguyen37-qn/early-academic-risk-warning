# Open University Learning Analytics Dataset (OULAD)

## Nguồn dữ liệu

**Tổ chức sở hữu**

The Open University
Walton Hall, Milton Keynes, MK7 6AA, United Kingdom
Liên hệ: Zdenek Zdrahal — [zdenek.zdrahal@open.ac.uk](mailto:zdenek.zdrahal@open.ac.uk)

**Nhà cung cấp dữ liệu**

| Tên            | Đơn vị                                                                | Email                                                         |
| -------------- | --------------------------------------------------------------------- | ------------------------------------------------------------- |
| Jakub Kuzilek  | Knowledge Media Institute, The Open University & CIIRC, CTU in Prague | [jakub.kuzilek@gmail.com](mailto:jakub.kuzilek@gmail.com)     |
| Martin Hlosta  | Knowledge Media Institute, The Open University                        | [martin.hlosta@open.ac.uk](mailto:martin.hlosta@open.ac.uk)   |
| Zdenek Zdrahal | Knowledge Media Institute, The Open University & CIIRC, CTU in Prague | [zdenek.zdrahal@open.ac.uk](mailto:zdenek.zdrahal@open.ac.uk) |

**Ngày công bố:** Tháng 12 năm 2015

---

## Tổng quan

OULAD chứa dữ liệu về các khóa học, sinh viên và các tương tác của họ với Môi trường học tập trực tuyến (Virtual Learning Environment - VLE) trên bảy học phần (module) được lựa chọn. Các đợt mở khóa học bắt đầu vào **tháng 2** (`B`) và **tháng 10** (`J`). Tất cả các bảng dữ liệu được liên kết thông qua các định danh duy nhất và được lưu dưới dạng tệp CSV.

Thông tin thêm: https://analyse.kmi.open.ac.uk/open_dataset

---

## Thống kê bộ dữ liệu

| Thực thể                    |   Số lượng |
| --------------------------- | ---------: |
| Sinh viên tham gia khóa học |     32,953 |
| Đợt mở học phần             |         22 |
| Trang/tài nguyên VLE        |      6,364 |
| Nhật ký tương tác VLE       | 10,655,280 |
| Bản ghi đăng ký học         |     32,953 |
| Bài đánh giá                |        206 |
| Bản ghi kết quả đánh giá    |    173,912 |
| **Tổng số thuộc tính**      |     **43** |

---

## Thông tin thuộc tính

### `courses.csv`

| Cột                 | Kiểu dữ liệu | Đơn vị | Mô tả                                           |
| ------------------- | ------------ | ------ | ----------------------------------------------- |
| `code_module`       | nominal      | —      | Mã định danh của học phần                       |
| `code_presentation` | nominal      | —      | Mã năm + học kỳ (`B` = tháng 2, `J` = tháng 10) |
| `length`            | integer      | ngày   | Thời lượng của đợt mở học phần                  |

---

### `assessments.csv`

| Cột                 | Kiểu dữ liệu | Đơn vị | Mô tả                                                                           |
| ------------------- | ------------ | ------ | ------------------------------------------------------------------------------- |
| `code_module`       | nominal      | —      | Học phần chứa bài đánh giá                                                      |
| `code_presentation` | nominal      | —      | Đợt mở học phần chứa bài đánh giá                                               |
| `id_assessment`     | integer      | —      | Mã định danh duy nhất của bài đánh giá                                          |
| `assessment_type`   | nominal      | —      | Loại bài đánh giá                                                               |
| `date`              | integer      | ngày   | Hạn nộp cuối cùng, tính từ ngày bắt đầu khóa học (ngày 0)                       |
| `weight`            | integer      | %      | Trọng số của bài đánh giá; bài thi cuối kỳ = 100%, các bài khác cộng lại = 100% |

---

### `vle.csv`

| Cột                 | Kiểu dữ liệu | Đơn vị | Mô tả                                    |
| ------------------- | ------------ | ------ | ---------------------------------------- |
| `id_site`           | integer      | —      | Mã định danh duy nhất của tài nguyên VLE |
| `code_module`       | nominal      | —      | Học phần chứa tài nguyên                 |
| `code_presentation` | nominal      | —      | Đợt mở học phần chứa tài nguyên          |
| `activity_type`     | nominal      | —      | Vai trò/loại của tài nguyên              |
| `week_from`         | integer      | tuần   | Tuần dự kiến bắt đầu sử dụng tài nguyên  |
| `week_to`           | integer      | tuần   | Tuần dự kiến kết thúc sử dụng tài nguyên |

---

### `studentInfo.csv`

| Cột                    | Kiểu dữ liệu | Đơn vị | Mô tả                                                                          |
| ---------------------- | ------------ | ------ | ------------------------------------------------------------------------------ |
| `code_module`          | nominal      | —      | Học phần mà sinh viên đăng ký                                                  |
| `code_presentation`    | nominal      | —      | Đợt mở học phần mà sinh viên đăng ký                                           |
| `id_student`           | integer      | —      | Mã định danh duy nhất của sinh viên                                            |
| `gender`               | nominal      | —      | Giới tính của sinh viên                                                        |
| `region`               | nominal      | —      | Khu vực địa lý nơi sinh viên sinh sống trong thời gian học                     |
| `highest_education`    | nominal      | —      | Trình độ học vấn cao nhất khi nhập học                                         |
| `imd_band`             | nominal      | —      | Mức chỉ số thiếu thốn xã hội (Index of Multiple Deprivation) tại nơi sinh sống |
| `age_band`             | nominal      | —      | Nhóm tuổi của sinh viên                                                        |
| `num_of_prev_attempts` | integer      | —      | Số lần sinh viên đã từng học lại học phần này                                  |
| `studied_credits`      | integer      | —      | Tổng số tín chỉ của các học phần sinh viên đang học                            |
| `disability`           | nominal      | —      | Sinh viên có khai báo khuyết tật hay không                                     |
| `final_result`         | nominal      | —      | Kết quả cuối cùng của sinh viên trong học phần                                 |

---

### `studentRegistration.csv`

| Cột                   | Kiểu dữ liệu | Đơn vị | Mô tả                                                                                                       |
| --------------------- | ------------ | ------ | ----------------------------------------------------------------------------------------------------------- |
| `code_module`         | nominal      | —      | Mã học phần                                                                                                 |
| `code_presentation`   | nominal      | —      | Mã đợt mở học phần                                                                                          |
| `id_student`          | integer      | —      | Mã định danh duy nhất của sinh viên                                                                         |
| `date_registration`   | integer      | ngày   | Ngày đăng ký, tính tương đối so với ngày bắt đầu khóa học (giá trị âm = đăng ký trước khi khóa học bắt đầu) |
| `date_unregistration` | integer      | ngày   | Ngày hủy đăng ký, tính tương đối so với ngày bắt đầu khóa học; để trống nếu sinh viên hoàn thành khóa học   |

---

### `studentAssessment.csv`

| Cột              | Kiểu dữ liệu | Đơn vị | Mô tả                                              |
| ---------------- | ------------ | ------ | -------------------------------------------------- |
| `id_assessment`  | integer      | —      | Mã định danh bài đánh giá                          |
| `id_student`     | integer      | —      | Mã định danh duy nhất của sinh viên                |
| `date_submitted` | integer      | ngày   | Ngày nộp bài, tính từ thời điểm bắt đầu khóa học   |
| `is_banked`      | integer      | —      | Đánh dấu kết quả được chuyển từ đợt học trước      |
| `score`          | integer      | 0–100  | Điểm của sinh viên; điểm dưới 40 được xem là Fail  |

---

### `studentVle.csv`

| Cột                 | Kiểu dữ liệu | Đơn vị | Mô tả                                                   |
| ------------------- | ------------ | ------ | ------------------------------------------------------- |
| `code_module`       | nominal      | —      | Mã học phần                                             |
| `code_presentation` | nominal      | —      | Mã đợt mở học phần                                      |
| `id_student`        | integer      | —      | Mã định danh duy nhất của sinh viên                     |
| `id_site`           | integer      | —      | Mã định danh tài nguyên VLE                             |
| `date`              | integer      | ngày   | Ngày tương tác, tính từ thời điểm bắt đầu khóa học      |
| `sum_click`         | integer      | —      | Số lần sinh viên tương tác với tài nguyên trong ngày đó |

---

## Giá trị thiếu

Có — một số thuộc tính chứa giá trị bị thiếu.

---

## Phân bố nhãn (`final_result`)

| Lớp                    |   Số lượng |        % |
| ---------------------- | ---------: | -------: |
| Distinction (Xuất sắc) |      3,024 |     9.3% |
| Fail (Trượt)           |      7,052 |    21.6% |
| Pass (Đạt)             |     12,361 |    37.9% |
| Withdrawn (Bỏ học)    |     10,156 |    31.2% |
| **Tổng cộng**          | **32,593** | **100%** |
