# Fix Login — Diagnosis & Perbaikan

## Langkah 1 — Diagnosis (sebelum mengubah)

### Struktur DOM Saat Ini

**base.html (ringkas):**
```
<body class="d-flex flex-column min-vh-100 is-public is-auth-page">
  #bg-scene (fixed, z-index:-1)
  nav.navbar (sticky-top)
  main#main-content.container.flex-grow-1.py-4
    .toast-container.position-fixed.bottom-0.end-0.p-3  ← DANGER: di dalam main
    .content-panel.glass-strong
      {% block content %}
  footer.footer-public.mt-auto
```

**accounts/auth_base.html:**
```
{% block content %}
<div class="auth-page">                           ← .auth-page (flex row center)
  <section class="auth-panel">                    ← .auth-panel (flex row center, align-items:center)
    <div class="auth-mobile-brand">NusaTani</div> ← sibling kartu (kiri)
    <div class="auth-card">                       ← kartu login (tengah)
      {% block auth_body %}{% endblock %}
    </div>
    <p class="auth-legal">MVP · Pembayaran...</p>  ← sibling kartu (kanan)
  </section>
</div>
{% endblock %}
```

**registration/login.html (auth_body):**
1. `section-kicker` + `h1` "Selamat datang kembali" + deskripsi
2. Form login (username, password, tombol "Masuk ke dashboard")
3. Divider "atau masuk sebagai demo"
4. **Demo picker** — link cards per peran (`.demo-role-card` sebagai `<a href="...">`)
5. **Demo card** — ringkasan peran terpilih + form demo (hidden input `role` + tombol "Masuk sebagai {Peran}")
6. Divider "atau"
7. Tombol "Belum tahu peran saya? Buka panduan"
8. Link "Daftar sekarang"

### Container Flex Baris yang Masalah
- **`.auth-page`** (app.css:1049): `display: flex; justify-content: center; min-height: calc(100vh - 72px)`
- **`.auth-panel`** (app.css:1202): `display: flex; align-items: center; justify-content: center; padding: 2.5rem 1rem; background: var(--nt-bg)`

`.auth-panel` memiliki **tiga anak flex** dalam satu baris horizontal: `.auth-mobile-brand` (kiri), `.auth-card` (tengah), `.auth-legal` (kanan). Karena `align-items: center`, ketiga elemen ini sejajar vertikal di tengah kartu. Inilah akar gejala #1 dan #2.

### Struktur DOM yang Benar (Target)
```
<body class="d-flex flex-column min-h-[100dvh]">
  #bg-scene (fixed, z-index:-1)
  nav.navbar
  main.auth-page (flex:1; display:grid; place-items:center; padding:24px 16px)
    .auth-card.glass-strong (width:min(100%,460px); margin:auto)
      A. Judul + kalimat singkat
      B. Pemilih peran (segmented control radio)
      C. Form login (username label dinamis, password, tombol utama)
      D. Divider + ringkasan peran + tombol demo sekunder + catatan
  footer (di luar main, mt-auto)
```
- Toast container dipindah ke **akhir `<body>`** (sibling footer), bukan di dalam `main`.

### Screenshot Browser
Playwright tersedia via `npx`. Screenshot akan diambil setelah perbaikan untuk verifikasi.

---

## Gejala & Akar Penyebab

| # | Gejala | Akar Penyebab |
|---|--------|---------------|
| 1 | Kartu tidak tengah, geser ~47px kiri | `.auth-panel` flex-row dengan 3 anak; `.auth-mobile-brand` lebar tidak sama dengan `.auth-legal` → pusat kartu bergeser |
| 2 | Logo & teks legal di kiri/kanan kartu | Sama di atas: `.auth-mobile-brand` dan `.auth-legal` jadi sibling flex kartu |
| 3 | Urutan konten salah | Template login urutannya: judul → form login → demo picker (link) → demo card (form) → divider → panduan. Harus: judul → pemilih peran (segmented) → form login → divider → ringkasan + tombol demo |
| 4 | Teks duplikat "Kelola produk..." | Ada di JS `cfgMap.farmer.hint` dan juga di `selected_role_config.hint` yang ditampilkan di demo card |
| 5 | Dua tombol besar hijau/oranye, emoji | Demo card pakai `.demo-btn` (warna `--nt-accent` oranye), login pakai `btn-primary-green`; role cards pakai emoji sprout (SVG tapi sama untuk semua peran) |
| 6 | Label username tidak berubah | JS hanya update label saat klik role card (link → reload). Perlu radio segmented control yang update label instan tanpa reload |
| 7 | Toast terpotong di dashboard | `.toast-container` ada di dalam `main > .content-panel` yang `overflow: hidden` / `clip`; z-index toast (1095) tapi parent clipping |

---

## Rencana Perbaikan (Langkah 2 & 3)

### A. Template & Struktur
1. **`templates/accounts/auth_base.html`** — hapus `.auth-page`, `.auth-panel`, `.auth-mobile-brand`, `.auth-legal`; ganti dengan `<main class="auth-page">` yang hanya membungkus `.auth-card`.
2. **`templates/registration/login.html`** — susun ulang `auth_body` sesuai URUTAN: judul → segmented control role (radio + label SVG) → form login → divider → ringkasan peran terpilih + tombol demo sekunder (glass) + catatan. Hapus demo picker link cards & demo card lama. Pertahankan dua `<form>` terpisah (login & demo) dengan `name`/`action`/`method` sama.
3. **`templates/base.html`** — pindahkan `.toast-container` ke akhir `<body>` (sebelum `</body>`), sibling footer.

### B. CSS (`static/css/app.css` + `static/css/components.css`)
1. **`.auth-page`** baru: `flex:1; display:grid; place-items:center; padding:24px 16px; min-height:0` (agar respect flex parent).
2. **`.auth-card`** baru: `width:min(100%,460px); margin:auto; background:rgba(255,255,255,.66); backdrop-filter:blur(16px) saturate(160%); -webkit-backdrop-filter:...; border:1px solid rgba(255,255,255,.55); border-radius:24px; box-shadow:0 8px 32px rgba(11,61,42,.14); padding:24px`.
3. **Fallback** `@supports not (backdrop-filter: blur(1px))` → `background:rgba(255,255,255,.92)`.
4. **Segmented control role**: radio tersembunyi, label sebagai tombol dengan SVG ikon per peran, grid 2 kolom di ≤480px, min-height 44px.
5. **Tombol demo sekunder**: gaya kaca (`.glass` / `.btn-outline-green` style), tidak oranye.
6. **Toast container**: `position:fixed; bottom:env(safe-area-inset-bottom,16px); right:env(safe-area-inset-right,16px); left:auto; z-index:2000; max-width:min(360px,calc(100vw-32px));` — di luar main.

### C. JS (≤25 baris, inline di login.html)
- Sinkronkan radio role → update label username, placeholder, hint, ringkasan, tombol demo.
- Progressive enhancement: tanpa JS, tampilkan `<select name="role">` tersembunyi yang di-submit oleh form demo; dengan JS, sembunyikan select dan gunakan radio.

### D. Token & Variabel
Gunakan token dari `docs/design-spec.md` (`--glass-light`, `--glass-strong`, `--blur-max`, `--radius-xl`, `--accent`, `--mtn-*`, dll). Jangan tambah warna baru.

---

## File yang Akan Diubah
1. `templates/base.html` — pindah toast container
2. `templates/accounts/auth_base.html` — struktur baru auth-page
3. `templates/registration/login.html` — konten baru + JS
4. `static/css/app.css` — hapus style lama auth-page/auth-panel/auth-card/demo-*, tambah style baru auth-page/auth-card/segmented/toast
5. `static/css/components.css` — perbaiki toast container position/z-index