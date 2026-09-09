# Khung ghế — chín ghế, bỏ bớt được

Đây là bộ ghế đã chạy thật. Dự án nhỏ **bỏ bớt**: tối thiểu là R0 + `tho-dung` + `kiem-luat`.

| Ghế | Vai | Việc | Gọi khi nào |
|---|---|---|---|
| *(phiên chính)* | R0 | quản đốc: cắt lô, đề bài, giữ cổng | luôn |
| `truong-ky-thuat` | R1 | đề bài kỹ thuật lô khó · dựng lô khó nhất · gỡ bế tắc · review kiến trúc cuối sóng | **chỉ bốn việc này** |
| `nghien-cuu` | **R1b** | do kha thi - khao sat 2-3 phuong an kem danh doi - kiem ke nguon du lieu that | **TRUOC khi R1 ve kien truc**, hoac khi co cau "lam duoc khong / cai nao hon" |
| `tho-dung` | R2 | gõ code đúng MỘT mục spec | mỗi lô dựng |
| `kiem-luat` | R2 | soi guardrail, hợp đồng dữ liệu, ngân sách đọc — **chỉ đọc** | sau mỗi lô dựng |
| `kiem-giao-dien` | R2 | soi hệ nền, bố cục, i18n, khả dụng — **chỉ đọc** | sau mỗi lô có UI |
| `nguoi-thu` | R2 | viết/chạy test, nghiệm thu theo checklist | cuối mỗi lô |
| `nghiep-vu` | R2 | trả lời "vì sao" từ tài liệu nguồn | khi đề bài chạm nghiệp vụ chưa rõ |
| `chia-lo` | R2 | chia lô, xếp thứ tự phụ thuộc | đầu mỗi đợt |
| `do-duong` | R3 | dò mã nguồn "đã có gì", chạy lệnh cơ khí | trước khi dựng, để R0 khỏi đọc file dài |

## Vì sao phải có ghế nghiên cứu riêng (đo 9/9)

Không có ghế này thì **quản đốc tự đi nghiên cứu ngay trong phiên chính** — và đó là chỗ đắt nhất hệ
thống: một lượt ở phiên chính tốn **1,088 điểm**, một lượt ở ghế thợ tốn **0,070** → **rẻ hơn 15,4 lần**
khi cùng việc đó chạy ở ghế riêng. Chưa kể phiên chính bị **nhiễm ngữ cảnh vĩnh viễn**: mọi file thô
đọc vào sẽ được đọc lại ở *mỗi* lượt sau đó.

Và lý do nghiệp vụ quan trọng hơn tiền: **thiếu nghiên cứu thì Tech Lead yếu** — kiến trúc vẽ bằng
trực giác thay vì bằng số. Ghế này dọn bàn cho ghế kia: đo xong mới thiết kế.

**Luồng chuẩn cho một lô khó:** `nghien-cuu` đo → `truong-ky-thuat` chọn phương án + viết đề bài kỹ
thuật → `tho-dung` dựng → hai ghế soi → `nguoi-thu` nghiệm thu.

## Ba luật giữ cho cơ cấu không mục

1. **Hai ghế soi CHỈ ĐỌC.** Cho chúng quyền ghi là mất lý do tồn tại — người soi mà sửa được thì
   không còn ai soi. Chúng báo "sai ở đâu, hậu quả gì", R0 quyết vá hay không.
2. **Chỉ R0 ghi vào `workspace/`.** Subagent trả kết quả, R0 chép lại. Đó là cách bộ nhớ không loạn.
3. **Không ghế nào nhớ giữa các lần gọi.** Mỗi lần gọi là một đầu óc mới đọc lại tài liệu — nên tài
   liệu và `workspace/` phải đúng, đó là bộ nhớ duy nhất.

## Luật nâng–hạ (R0 tự quyết, ghi một dòng vào TRANG-THAI)

- Ghế R2 **sai 2 lần trong cùng một lô** → gọi R1 **gỡ bế tắc** (tìm vì sao kẹt: đề bài mơ hồ / thiếu
  ngữ cảnh / bẫy thật), không phải "nâng bậc" mù.
- Lô **khó nhất của đợt** → R1 tự dựng, vẫn qua đủ hai ghế soi + ghế thử.
- Việc **cơ khí thuần** đang nằm ở ghế R2 → hạ R3 bằng tham số lúc gọi, không sửa file ghế.
- Đề bài phải viết lại quá 1 lần → lỗi ở tầng trên, không phải lỗi thợ.

## Giới hạn thật — nói trước để không kỳ vọng nhầm

- Soi không thay được **chạy thật**; có lỗi chỉ lộ trên môi trường thật.
- Đội đông không nhanh hơn nếu việc **dính nhau** — chỉ gọi song song khi không đụng cùng file.
- Không ai duyệt thay người ở cổng cuối: cơ cấu lo "chạy đúng spec", còn "spec có đúng ý không" là việc của người.
