# Bậc model theo GÓI — chỗ dễ mất tiền nhất

**Luật cứng:** chỉ ghim model mà gói của người dùng **thật sự có**. Ghim tên model ngoài gói có thể rơi
sang đường tính phí khác — đó là "trừ tiền không kiểm soát". Không đoán: **hỏi người dùng** model cao
nhất trong bảng chọn của họ (`/model`).

**Và gói thay đổi theo thời điểm** — model có thể bị tắt giữa chừng. Vì vậy skill này **không ghim
cứng tên model vào tài liệu**: nó cài một cái **toggle** đổi cả xưởng trong một lệnh.

## Toggle — `cong-cu/doi-bac.py` (copy từ `references/doi-bac.py`)

```
python cong-cu/doi-bac.py            # xem đang ở hồ sơ nào
python cong-cu/doi-bac.py fable      # gói CÓ Fable
python cong-cu/doi-bac.py opus       # gói KHÔNG Fable (Opus cao nhất)
python cong-cu/doi-bac.py sonnet     # gói eo hẹp Opus (ví dụ gói 20$)
```

Nó đổi **ba chỗ cùng lúc**: `.claude/settings.json` (ghế R0) · dòng `model:` trong **mọi** ghế ·
và ghi lại `.claude/BAC-DANG-DUNG.md`. **Mọi tài liệu trỏ vào file đó**, không viết tên model vào văn
bản — đổi hồ sơ là xong, không phải đi sửa 9 file rồi quên một file.

> Sau khi đổi: **đóng phiên rồi mở lại** thì bậc mới có hiệu lực. Phiên đang mở không tự đổi.

## Ba hồ sơ

| Vai | `fable` | `opus` | `sonnet` |
|---|---|---|---|
| **R0** Quản đốc | `claude-fable-5` | `claude-opus-5` | `claude-sonnet-5` |
| **R1** Tech Lead | `claude-opus-5` | `claude-sonnet-5` | `claude-sonnet-5` |
| **R1b** Nghiên cứu | `claude-sonnet-5` | `claude-sonnet-5` | `claude-sonnet-5` |
| **R2** Kỹ sư/QA/BA | `claude-sonnet-5` | `claude-sonnet-5` | `claude-sonnet-5` |
| **R3** Cơ khí | `claude-haiku-4-5-20251001` | `claude-haiku-4-5-20251001` | `claude-haiku-4-5-20251001` |

### Chọn hồ sơ nào

- **`fable`** — gói có Fable. Còn "đệm" Tech Lead ở bậc Opus: thợ kẹt thì R1 gỡ mà không phiền quản đốc.
  Nhược: chính cái đệm đó dễ bị lạm dụng — đo được R1 ăn **78,6%** chi phí phần thợ.
- **`opus`** — gói không Fable (Opus cao nhất). R0 xuống Opus, **Tech Lead về Sonnet**. Không ghim Opus
  cho R1: nếu R0 và R1 cùng bậc thì mất khoảng cách trọng tài, mà R1 lại đúng là chỗ rò lớn nhất.
- **`sonnet`** — gói **20$ (Pro)** hoặc lúc hạn mức Opus gần cạn. Cả xưởng chạy Sonnet; quản đốc **nâng
  theo LƯỢT GỌI** (truyền tham số model) cho đúng lô khó nhất, có chủ đích và ghi vết.

**Với hồ sơ `opus` và `sonnet`, gánh nặng dồn sang chất lượng ĐỀ BÀI** — không còn ai đỡ ở giữa.
Đề bài chặt (file sẽ đụng · GWT ba nhánh · checklist nghiệm thu · thứ không được đụng) là điều kiện
sống, không phải điều nên có.

## Chi phí — đo trên 34.626 lượt gọi thật của một dự án đang chạy sản xuất

| Bậc | Điểm quota mỗi lượt | So với Sonnet |
|---|---|---|
| Haiku | 0,010 | rẻ hơn 6,9× |
| Sonnet | 0,069 | mốc |
| Opus | 0,465 | đắt hơn 6,7× |
| Fable | 0,88 – 1,11 | *(xem ghi chú)* |

> **Ghi chú quan trọng:** thước đo xếp **Fable và Opus CÙNG bậc giá**. Con số Fable cao hơn ở trên là do
> **độ dài ngữ cảnh** (Fable ngồi phiên chính, Opus ngồi ghế thợ), **không phải chênh giá model**.
> Hệ quả: **đổi R0 từ Fable sang Opus gần như không đổi điểm quota** — cái đổi là năng lực, không phải chi phí.

**Mô hình 1.000 lượt gọi, theo tỉ lệ đo được:**

| Kịch bản | Điểm / 1.000 lượt | So mốc |
|---|---|---|
| `fable`, R1 bị gọi 30% lượt (thực trạng cũ) | 315,8 | mốc |
| `fable`, R1 chỉ 10% lượt (có kỷ luật) | 238,8 | −24% |
| **`opus`** (R1 = Sonnet, nâng 5%) | **219,6** | **−30%** |

Gói không có Fable **không thiệt về chi phí** — thậm chí rẻ hơn, vì nó bị ép bỏ luôn cái đệm dễ lạm dụng.

## Mức tư duy (effort) — đo được, ngược trực giác

| Bậc | high | xhigh | Kéo lên xhigh |
|---|---|---|---|
| Sonnet | 0,0706 | 0,0669 | **rẻ hơn 5,2%** |
| Opus | 0,4548 | 0,4740 | đắt hơn 4,2% |
| Fable | 1,1132 | 0,8805 | **rẻ hơn 20,9%** |

**Kéo mức tư duy lên KHÔNG làm đắt hơn**, trong khi tỉ lệ token nghĩ tăng rõ (Opus 27% → 46%) — nghĩ
thay cho làm lại. Nếu phiên chạy không người trực: **chốt mức TRƯỚC khi phát goal**, giữa chừng không
ai chỉnh được. *(Tương quan, không phải thí nghiệm đối chứng — nhưng đủ để bác bỏ nỗi lo "nghĩ nhiều tốn tiền".)*

## Thứ đắt nhất không phải model — mà là ngữ cảnh

| Vùng | Điểm/lượt | |
|---|---|---|
| Phiên chính (quản đốc) | **1,088** | 12,8% số lượt nhưng **43,8% chi phí** |
| Ghế thợ (subagent) | 0,205 | 87,2% số lượt, 56,2% chi phí |

**Gấp 5,3 lần** — vì phiên chính mang cả lịch sử, đọc lại ở *mỗi* lượt. Đây là bằng chứng cứng cho hai
luật: **mỗi sóng lớn mở phiên mới**, và **quản đốc không tự đọc file dài / không tự nghiên cứu**
(giao `nghien-cuu` — rẻ hơn 15,4 lần).

## Khi model mới ra đời
Chỉ sửa **bảng ba hồ sơ ở trên** và `HO_SO` trong `doi-bac.py`. Mọi ghế đọc theo VAI, không theo tên model.
