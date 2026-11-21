# Fix Dashboard Glass — Diagnosis & Perbaikan

## Langkah 1 — Diagnosis (sebelum mengubah)

### Elemen pembungkus putih besar
**Selector:** `.content-panel.glass-strong` (base.html:184)
**Properti yang membuat putih:**
- `background: rgba(255, 255, 255, 0.88)` (background.css:135)
- `min-height: 100vh` (background.css:131) — memaksa panel tinggi penuh viewport
- `border-radius: var(--radius-lg)` (background.css:129)
- `padding: var(--space-6)` (background.css:130)
- `box-sizing: border-box` (background.css:132)

Elemen ini membungkus `{% block content %}` di dalam `<main>`, sehingga **seluruh isi halaman dashboard** (hero, KPI, fokus, pesanan terbaru) berada di dalam satu panel putih semi-solid yang menutupi latar gunung.

### Hero & KPI glass tidak tampak — penyebab

#### Hero (`.dashboard-hero.glass-dark`)
- Template: `<div class="glass-dark p-4 p-md-5 mb-4 dashboard-hero">`
- Masalah:
  1. Padding `p-4 p-md-5` = 1.5rem / 3rem → terlalu besar, tinggi ~335px
  2. Bootstrap `.lead` dan `<p>` margin-bottom menambah tinggi
  3. `.dashboard-hero-mark` (96×96px di app.css:473) terlalu besar, tidak dipakai (hidden di mobile, flex di lg)
  4. CSS `.dashboard-hero.glass-dark` (components.css:589) hanya set padding, tidak override background glass

#### KPI Cards (`.kpi-card`)
- Template: `<div class="kpi-card h-100">` di dalam `.col-6.col-lg-3`
- Masalah:
  1. Grid pakai Bootstrap flex (`.dashboard-stats` = `display:flex; flex-wrap:wrap`) + col classes → tidak pakai CSS Grid, kartu tidak rata 4 kolom di ≥1200px
  2. `.kpi-card` pakai `background: var(--glass-light)` tapi `.col-lg-3` lebar 25% dengan gap kecil → kartu 3+1 di layar lebar
  3. Ikon KPI: `.kpi-icon` background `rgba(255,255,255,0.5)` + `.nt-icon` 20×20px → terlalu kecil, hampir tidak terlihat
  4. Template render `{{ stat.icon|nt_icon|safe }}` tapi tidak dibungkus `<span class="kpi-ico">` per spec

#### Fokus peran & Pesanan terbaru
- Masih pakai `.card.h-100.glass-strong` dan `.card.glass-strong` — Bootstrap `.card` punya `background: var(--nt-surface)` (putih solid) yang menimpa `.glass-strong`

#### Toast
- Sudah dipindah ke akhir `<body>` tapi belum pakai `data-bs-autohide="true"` dengan delay 4 detik

---

## Langkah 2 — Rencana Perbaikan

1. **Hapus `.content-panel.glass-strong` wrapper** dari base.html untuk halaman workspace (dashboard). Isi halaman langsung di atas latar, tiap section pakai panel kaca sendiri.

2. **Hero**: 
   - Ganti ke `.glass-dark` dengan padding `24px 32px` (var(--space-6) var(--space-8))
   - Judul 32px (h1), deskripsi 14px maks 2 baris
   - Ikon ilustrasi: kotak 56×56px (bukan 96×96)
   - Tinggi total ≤ 220px

3. **KPI Grid**:
   - `.dashboard-stats` → `display:grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr)); gap: 24px`
   - Hapus Bootstrap col classes dari template
   - Kartu: `.glass .glass-sm .lift` (background var(--glass-light), blur-sm, lift hover)

4. **Ikon KPI**:
   - Struktur `<span class="kpi-ico"><svg ...></svg></span>`
   - CSS: `.kpi-ico svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.75}`
   - Setiap kartu wajib punya ikon relevan

5. **Fokus peran & Pesanan terbaru**:
   - Hapus `.card` class, pakai `.glass-strong` langsung
   - Daftar pesanan: baris `.glass-strong` + chip status

6. **Toast**:
   - Tambah `data-bs-delay="4000" data-bs-autohide="true"` di template
   - Sudah di akhir body

7. **Semua elemen putih solid** → terapkan kelas kaca yang sesuai