# Fix Background — Diagnosis & Perbaikan

## Langkah 1 — Diagnosis

### Cara gunung/latar dipasang (sebelum perbaikan)

- **Template:** `templates/base.html` memuat dekorasi latar sebagai `<div class="mountain-bg" aria-hidden="true">` (baris ~67–81) yang berisi satu `<svg>` inline 4 lapis gunung. Elemen ini berada di luar alur konten utama (langsung di dalam `<body>`), sebelum navbar.
- **CSS latar:** `static/css/background.css`
  - `.mountain-bg`: `position: fixed; inset: 0; z-index: -1; overflow: hidden; pointer-events: none` (di belakang semua konten).
  - `::before`: langit gradient `--sky-top → --sky-bottom`. `::after`: glow radial `--lime-300` kanan atas.
  - `.mountain-bg svg`: `position: absolute; bottom: 0; width: 100vw; height: 55vh; left:50%; transform: translateX(-50%)` dengan `preserveAspectRatio="xMidYMid slice"`.
  - 4 path (`.mtn-far/mid/near/front`) memakai variabel `--mtn-*`. Kabut: `<rect class="fog-band">` + gradient. Responsif: `<600px` sembunyikan `.mtn-mid, .mtn-near`.
  - `.content-panel`: panel putih semi-solid `rgba(255,255,255,.55)` + `backdrop-filter: blur(8px)` membungkus `{% block content %}` di `<main>` (agar teks terbaca sementara).
- **Dekorasi latar lain (tersebar, di luar `mountain-bg`):**
  - `templates/base.html` (publik, non-login): `<div class="public-hero" role="img">` di dalam alur halaman (antara navbar dan `<main>`), berlatar foto `static/images/highland-sawah.jpg` (CSS `static/css/app.css`, `.public-hero`). Ini dekorasi latar yang berada di dalam alur layout.
  - `static/css/app.css`: `.hero-soft::before` memakai `background-image: url("../images/highland.svg")`; `body.is-workspace main::before` memakai siluet `highland.svg` sebagai pseudo-elemen dekoratif di belakang area main.
  - `static/images/mountains.svg` (duplikat SVG gunung) dan `static/images/highland.svg` ada sebagai aset statis.

### Penyebab tabrakan gunung dengan form/teks (jendela setengah layar)

1. **Gunung terlalu tinggi dan memuncak ke tengah viewport.** SVG diberi tinggi tetap `55vh` pada container fixed. Pada jendela pendek (mis. tinggi 500px → 275px; setengah layar) atau lebar sempit dengan `preserveAspectRatio="xMidYMid slice"` (menjaga rasio lalu memotong), bentuk puncak (path naik hingga mendekati bagian atas viewBox 520) diskalakan besar sehingga puncak gunung menembus area konten/form.
2. **Anchoring/preserveAspectRatio tidak mengunci dasar.** `xMidYMid slice` menjaga tengah-tengah; kombinasi lebar `100vw` + tinggi `55vh` + slice dapat mendorong puncak lebih tinggi dari yang diinginkan. Seharusnya dasar gunung menempel bawah (`xMidYMax`) dan tinggi dibatasi proporsional (clamp berbasis vh dengan batas px).
3. **Tidak ada pemudaran ke atas.** Tidak ada `mask-image`/fade, sehingga tepi atas siluet gunung menjadi garis tegas di belakang konten/panel transparan.
4. **Lapisan blur per gunung tidak diterapkan.** Spesifikasi visual membutuhkan blur berbeda per kedalaman (jauh 2px, tengah 1.5px, dekat 1px) agar latar tidak “bersaing” dengan teks; sebelumnya tidak ada filter blur pada lapisan.
5. **Dekorasi latar di alur halaman.** `.public-hero` (foto sawah) berada di alur layout dan menambah elemen latar besar sebelum konten, memperumit tinggi efektif dan berpotensi bergeser/tumpang tindih pada viewport pendek. Dekorasi latar juga tersebar (`main::before`, `hero-soft::before`) alih-alih terpusat.
6. **Panel konten tembus pandang.** `.content-panel` memakai latar `rgba(255,255,255,.55)`; saat gunung naik tinggi di belakangnya, siluet tetap terlihat kuat menabrak teks/form di dalam panel.

### Screenshot browser (Playwright) — status

Lingkungan eksekusi **tidak memiliki** browser/Playwright yang siap pakai (`playwright` tidak terpasang, `npx` tersedia tetapi tanpa paket browser terinstal, tidak ada `chromium`/`google-chrome`/`chrome` di PATH). Karena itu screenshot otomatis pada 360/640/960/1280px (tinggi 500 & 900) **tidak dapat diambil dari sini**.

**Yang diminta untuk verifikasi manual (screenshot):** buka halaman form (mis. `/accounts/login/`, form produk/pesanan) dan dashboard (`/accounts/dashboard/`) pada ukuran jendela **360×500, 360×900, 640×500, 640×900, 960×500, 960×900, 1280×500, 1280×900**. Pastikan puncak gunung memudar dan tidak menabrak teks/form, tidak ada scroll horizontal, dan tidak ada layout shift.

## Langkah 2 — Perbaikan yang diterapkan

1. **`#bg-scene` terpusat (base template):** `templates/base.html` memakai `<div id="bg-scene" aria-hidden="true">` dengan `position:fixed; inset:0; z-index:-1; overflow:hidden; pointer-events:none`. Semua dekorasi latar halaman dipindahkan ke dalamnya (langit, glow, 4 lapis gunung, dan layer sawah publik).
2. **Dekorasi latar dihapus dari alur halaman:** `.public-hero` in-flow dihapus dari template (foto sawah dipindah ke layer di dalam `#bg-scene`, ditampilkan hanya pada `body.is-public` via CSS). Pseudo-dekorasi latar halaman `body.is-workspace main::before` dan latar foto `.public-hero` dinonaktifkan di CSS.
3. **Gunung 4 lapis di dasar scene:** SVG 4 path dengan `preserveAspectRatio="xMidYMax slice"`, tinggi `clamp(180px, 34vh, 380px)`; override `@media (max-height: 599px)` → `26vh`; `<600px` lebar → hanya 2 lapis (far, front) dan tinggi `22vh`.
4. **Blur & fade:** `filter: blur(2px)` (far), `blur(1.5px)` (mid), `blur(1px)` (near), front tanpa blur; `mask-image: linear-gradient(to top, #000 0%, #000 35%, transparent 100%)` pada pembungkus gunung agar memudar ke atas (tanpa garis tegas).
5. **Panel konten:** `main, .page, .navbar, footer` diberi `position:relative; z-index:1`. `.content-panel` diperkuat sebagai panel kaca kuat (`.glass-strong`/latar solid semi-opaque) agar teks/form/tabel tidak pernah langsung di atas latar.
6. **Stabilitas layout:** `overflow-x` dicegah pada body/scene, elemen latar `pointer-events:none`, dimensi/posisi fixed untuk menghindari layout shift.

Catatan: perubahan hanya pada lapisan tampilan (template/CSS/SVG). Tidak ada perubahan models/views/urls/forms/permission/migrasi/nama field/URL.
