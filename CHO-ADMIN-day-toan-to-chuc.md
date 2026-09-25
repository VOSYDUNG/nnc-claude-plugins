# Cách 2 — Admin đẩy cho TOÀN tổ chức (không ai phải gõ lệnh)

Cách 1 (mỗi người gõ 2 lệnh) nằm ở `README.md`. Cách này dành cho quản trị viên Claude của
NNC Lao Group: thêm hai khoá vào **managed settings** của tổ chức, mọi thành viên tự có.

```json
{
  "extraKnownMarketplaces": {
    "nnc-claude-plugins": {
      "source": {
        "source": "git",
        "url": "https://github.com/VOSYDUNG/nnc-claude-plugins.git"
      },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "nnc@nnc-claude-plugins": true
  }
}
```

- `extraKnownMarketplaces` — tự đăng ký marketplace, không ai phải chạy `/plugin marketplace add`.
- `enabledPlugins` — tự bật plugin `nnc` cho mọi người.
- Muốn chặt hơn: `strictKnownMarketplaces` (CHỈ dùng được ở managed settings) giới hạn nhân viên
  chỉ được cài từ marketplace của công ty.

**Cập nhật về sau:** sửa repo → **tăng `version`** trong `plugins/nnc/.claude-plugin/plugin.json`
(PATCH sửa lỗi · MINOR thêm tính năng tương thích · MAJOR đổi bố cục dự án, kèm `oser migrate`) → mọi người nhận bản mới. Chỉ số version ở **plugin.json** mới kích hoạt cập
nhật; version ở `marketplace.json` chỉ để ghi nhãn.

**Repo riêng tư:** Claude Code dùng thẳng `git` của máy — SSH key hoặc credential helper sẵn có là đủ,
không cần token riêng.

**Sau khi mọi người nhận bản mới:** mỗi dự án chạy `oser update` (hoặc `oser migrate` khi nâng MAJOR);
`oser doctor` báo `OSR-002` khi dự án được sinh bởi version khác version đang chạy.
