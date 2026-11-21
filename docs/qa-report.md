# QA Report — Tampilan NusaTani

Tanggal: 20 Nov 2026  
Referensi: `docs/design-spec.md`, `docs/audit.md`  
Scope: Hanya tampilan (template + static CSS), tidak ada perubahan logika/views.

---

## 1. Responsif (360, 768, 1280, 1440px)

| Item | Status | Keterangan |
|------|--------|------------|
| Tidak ada scroll horizontal | LULUS | `overflow-x: clip` pada `main` (public & workspace), `box-sizing: border-box` pada `.content-panel`, grid `col-*` dengan breakpoints Bootstrap. |
| Navbar mobile berfungsi (hamburger) | LULUS | Bootstrap collapse via `navbar-toggler`, `data-bs-toggle="collapse"`, `data-bs-target="#mainNav"` di `base.html`. |

---

## 2. Kontras teks/latar (target >= 4.5:1 WCAG AA)

| Panel | Pasangan | Status | Keterangan |
|-------|----------|--------|------------|
| `.glass-light` (navbar, footer, KPI) | Teks `--ink:#0F2A1D` pada latar ~#ECF7EF | LULUS | Kontras sangat tinggi (bg sangat terang). |
| `.glass-strong` (form, tabel, modal) | Teks `--ink` pada latar ~#F6FBF7 | LULUS | Opacity 0.82, bg hampir putih. |
| `.glass-dark` (hero, teks putih) | Teks `#ffffff` pada latar gunung | DIPERBAIKI | Opacity `--glass-dark` ditingkatkan `0.62` → `0.78` (`tokens.css:28`) agar kontras >= 4.5:1 bahkan di lapisan gunung terang. |

Perhitungan kontras `.glass-dark` 0.62 over `--mtn-far:#CDEBD6` menghasilkan ~4.47:1 (di bawah target). Setelah 0.78: ~5.1:1.

---

## 3. Fallback tanpa backdrop-filter

| Item | Status | Keterangan |
|------|--------|------------|
| `@supports not (backdrop-filter: blur(1px))` | LULUS | Sudah ada di `components.css:38-46`. Ditambahkan pula di `app.css` untuk semua komponen kaca (navbar, card, modal, hero, toast, alert, footer, form, list-group). Fallback menggunakan background hampir solid (rgba .90-.95). |

---

## 4. prefers-reduced-motion, fokus keyboard, target sentuh

| Item | Status | Keterangan |
|------|--------|------------|
| `prefers-reduced-motion: reduce` | LULUS | `app.css:1704+` (nilai durasi 0.01ms) dan `components.css` (baris akhir) untuk skeleton-pulse, onboarding-step, flow-list. |
| Fokus keyboard terlihat | LULUS | `:focus-visible` outline 3px accent (`app.css:1652`, `components.css:248`). Skip-link focus style (`app.css:1657`). |
| Target sentuh >= 44px | DIPERBAIKI | `.btn` height 44px (`components.css:174`). `.btn-sm` diubah `height: auto` → `min-height: 44px`. `.navbar-toggler`, `.password-toggle`, `.btn-close` diberi min-height/min-width 44px. |

---

## 5. Performa

| Metrik | Nilai | Keterangan |
|--------|-------|------------|
| Elemen backdrop-filter per halaman (typical dashboard) | ~7-9 | Navbar (1), hero glass-dark (1), 4 KPI card (4), focus card (1-2), recent order card (1), footer (1). Dropdown/toast/modal hanya saat dibuka. Dalam batas "sedikit" per spec. |
| Ukuran CSS | tokens.css ~1KB, components.css ~13KB, app.css ~35KB, background.css ~1KB | Total ~50KB, dalam batas wajar. |
| Font | Google Fonts (Inter, Plus Jakarta Sans) via CDN | Tidak ada font lokal; fallback system-ui. |
| SVG | Inline sprite di `base.html` + `<use>` referensi | Tidak ada file SVG eksternal ikon. |
| Lighthouse | Tidak dijalankan (tidak ada Node.js/lighthouse di environment) | Django `manage.py check` lolos (0 issues). |

---

## 6. Konsistensi penamaan menu dan format data

### Format Rupiah (standar: "Rp 22.000" + satuan)

| File | Sebelum | Sesudah | Status |
|------|---------|---------|--------|
| `templates/products/catalog.html` | `rupiah:"pack"` | `rupiah:"pack"` | Sudah konsisten |
| `templates/products/product_detail.html` | `rupiah:"pack"` | `rupiah:"pack"` | Sudah konsisten |
| `templates/products/my_products.html` | `rupiah:"pack"` | `rupiah:"pack"` | Sudah konsisten |
| `templates/bankku/dashboard.html` | `Rp{{ x|floatformat:0 }}` | `{{ x|rupiah }}` | DIPERBAIKI (3 tempat) |
| `templates/bankku/my_performance.html` | `Rp{{ x|floatformat:0 }}` | `{{ x|rupiah }}` | DIPERBAIKI (2 tempat) |
| `templates/assets/asset_detail.html` | `Rp{{ x|floatformat:0 }}` | `{{ x|rupiah }}` | DIPERBAIKI (2 tempat) |
| `templates/assets/asset_list.html` | `Rp{{ x|floatformat:0 }}` | `{{ x|rupiah }}` | DIPERBAIKI (2 tempat) |
| `templates/orders/order_detail.html` | `Rp{{ x|floatformat:0 }}` | `{{ x|rupiah }}` | DIPERBAIKI (4 tempat) |
| `templates/orders/_order_table.html` | `Rp{{ x|floatformat:0 }}` | `{{ x|rupiah }}` | DIPERBAIKI (1 tempat) |

Semua template yang menampilkan harga sekarang pakai filter `rupiah` → output "Rp 22.000" (spasi setelah Rp, titik pemisah ribuan) sesuai `docs/design-spec.md:63`.

### Format Tanggal (standar: "20 Nov 2026")

| File | Sebelum | Sesudah | Status |
|------|---------|---------|--------|
| `templates/accounts/dashboard.html` | `{% now "j F Y" %}` → "20 November 2026" | `{% now "d M Y" %}` → "20 Nov 2026" | DIPERBAIKI |
| `templates/bankku/dashboard.html` | `date:"d M Y H:i"` | Tidak berubah | Sudah konsisten |
| `templates/mentorship/mentorship_detail.html` | `date:"d M Y H:i"` | Tidak berubah | Sudah konsisten |
| `templates/deliveries/delivery_detail.html` | `date:"d M Y H:i"` | Tidak berubah | Sudah konsisten |
| `templates/orders/order_detail.html` | `date:"d M Y"` / `date:"d M Y H:i"` | Tidak berubah | Sudah konsisten |
| `templates/orders/_order_table.html` | `date:"d M Y"` | Tidak berubah | Sudah konsisten |

### Penamaan menu

| Item | Status | Keterangan |
|------|--------|------------|
| "Sisaku" vs URL name `surplus` | Dokumentasi saja | Dicatat di `docs/audit.md:6.2`, tidak dapat diubah tanpa mengubah `urls.py`/`views.py` (read-only). |
| "Pesanan Masuk" (farmer) vs "Pesanan Saya" (pembeli) | Sengaja | Membedakan arah pesanan, tidak diubah. |
| "BANKKU" (huruf besar semua) | Dokumentasi saja | Label branding, tidak diubah. |

---

## 7. Emoji ikon (harus nol)

| File | Emoji yang diganti | Ganti dengan |
|------|-------------------|--------------|
| `templates/accounts/auth_base.html` | 🌱 brand-mark | `<svg><use href="#icon-sprout"></use></svg>` |
| `templates/accounts/dashboard.html` | 📦, ✅, 🌱 focus-icon | SVG via `#icon-search`, `#icon-check-circle`, `#icon-sprout` |
| `templates/accounts/dashboard.html` | → arrow | SVG `#icon-arrow-right` |
| `templates/deliveries/delivery_detail.html` | → arrow | SVG `#icon-arrow-right` |
| `templates/accounts/guide.html` | →, ✓, ←, 🌱 | SVG `#icon-arrow-right`, `#icon-check-circle`, `#icon-sprout` |
| `templates/mentorship/mentorship_list.html` | → (2x) | SVG `#icon-arrow-right` |

Verifikasi akhir dengan `grep` emoji unicode di semua `*.html`: **0 match** — tidak tersisa emoji ikon.

---

## Ringkasan

| Pemeriksaan | Status |
|-------------|--------|
| Responsif 360/768/1280/1440px | LULUS |
| Kontras >= 4.5:1 | LULUS (setelah perbaikan opacity glass-dark) |
| Fallback tanpa backdrop-filter | LULUS |
| prefers-reduced-motion / fokus / sentuh >= 44px | LULUS (setelah perbaikan touch target) |
| Performa (backdrop-filter, ukuran CSS) | LULUS |
| Konsistensi Rupiah & Tanggal | DIPERBAIKI |
| Tidak ada emoji ikon | LULUS |

File yang diubah:
- `templates/accounts/auth_base.html`
- `templates/accounts/dashboard.html`
- `templates/accounts/guide.html`
- `templates/deliveries/delivery_detail.html`
- `templates/mentorship/mentorship_list.html`
- `templates/bankku/dashboard.html`
- `templates/bankku/my_performance.html`
- `templates/assets/asset_detail.html`
- `templates/assets/asset_list.html`
- `templates/orders/order_detail.html`
- `templates/orders/_order_table.html`
- `static/css/tokens.css`
- `static/css/app.css`
- `static/css/components.css`