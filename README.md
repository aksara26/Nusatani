# NusaTani: Panduan Restyle (Hijau Glassmorphism + Pegunungan)

Dokumen ini berisi temuan dari MVP yang sekarang, konsep desain, dan prompt step by step untuk AI coding agent (Claude Code, Cursor, dan sejenisnya).

---

## 1. Temuan dari web yang sekarang

1. **Gunung dan glass hampir tidak terlihat.** Latar tertutup lapisan putih tebal, sehingga kartu tampak seperti kotak putih biasa.
2. **Harga tertulis `Rp12000` tanpa pemisah ribuan.** Harusnya `Rp 12.000`.
3. **Harga tanpa satuan.** Proposal berasumsi harga per kg (Rp220.000/kg untuk HOREKA). Rp22.000 itu per apa?
4. **Penamaan tidak konsisten.** Menu "Sisaku" membuka halaman "Marketplace Surplus", dengan filter "Surplus". Pilih satu istilah.
5. **Ikon memakai emoji.** Tampilannya beda di tiap OS dan terkesan kurang serius. Ganti ke SVG.
6. **Foto produk berupa placeholder dengan area gambar sangat besar.** Ruang terbuang.
7. **Ada elemen dobel.** Badge "Petani" muncul di navbar dan di hero, dan tombol "Tambah produk" berulang.
8. **Desain di PDF tidak sama dengan web live.** Prototipe di halaman 5 proposal memakai sidebar hijau tua dengan kartu lime dan krem, sedangkan web live memakai navbar atas dan mint terang. Tentukan satu desain resmi.

## 2. Konsep

"Kabut dataran tinggi": pegunungan hijau berlapis, kabut, dan sedikit sawah terasering sebagai latar. Panel kaca buram menumpang di atasnya. Semua role memakai base hijau yang sama dan hanya `--accent` yang berganti per role.

Spesifikasi lengkap (warna, font, layout, komponen) ada di **Prompt 2**.

## 3. Referensi

- Nielsen Norman Group, *Glassmorphism*: pakai secukupnya dan pastikan kontras teks terpenuhi. https://www.nngroup.com/articles/glassmorphism/
- UXMagic, *What is Glassmorphism*: uji kontras WCAG AA 4,5:1 terhadap latar yang berubah, `-webkit-backdrop-filter` untuk Safari, dan fallback `@supports`. https://uxmagic.ai/blog/what-is-glassmorphism
- Axess Lab, *Glassmorphism Meets Accessibility*: hindari blur 20px ke atas dan hormati `prefers-reduced-motion`. https://axesslab.com/?p=5111
- *CSS Glassmorphism Best Practices* (2026): `backdrop-filter` membebani performa, jadi batasi ke lapisan paling atas, dan siapkan fallback. https://lifa-su.github.io/blog/ai-css-glassmorphism-accessible-design.html

## 4. Cara pakai

- Jalankan **satu prompt per sesi**, cek di browser, lalu commit.
- Di PythonAnywhere, kalau CSS tidak berubah, biasanya karena `collectstatic` belum dijalankan, mapping Static files di tab **Web** belum benar, atau belum klik **Reload**.
- Role admin tidak perlu kamu jelaskan: Prompt 1 menyuruh AI mengaudit sendiri semua template. Kalau "admin" yang dimaksud adalah Django admin bawaan (`/admin/`), biarkan dan jangan di-restyle.

---

## Prompt 0: Aturan tetap (simpan sebagai CLAUDE.md atau tempel di awal tiap sesi)

```
Kamu front-end engineer yang me-restyle web NusaTani: marketplace microgreens yang menghubungkan petani, HOREKA, dan konsumen, dengan fitur pre-order, QC, dan pembiayaan syariah. App berjalan di PythonAnywhere.

ATURAN TETAP:
1. Hanya ubah lapisan tampilan: templates dan static (CSS/JS/gambar/SVG). DILARANG mengubah models, views, urls, forms, permission, migrasi, atau nama field/URL name. Kalau sebuah perubahan tampilan butuh perubahan logika, berhenti dan tanya saya.
2. Semua teks UI berbahasa Indonesia. Pertahankan istilah menu: Pesananku, Sisaku, Qualityku, Asetku, Mentorku, BANKKU.
3. Ikuti docs/design-spec.md (dibuat di langkah 2). Jangan menambah warna atau font di luar spec.
4. Cek dulu CSS framework yang sudah dipakai (kemungkinan Bootstrap karena ada dropdown). Jangan mencampur sistem yang bertabrakan dan jangan menambah framework baru.
5. Jangan mengarang data. Kalau field/data tidak ada, tulis TODO di kode dan laporkan ke saya.
6. Setiap selesai: jalankan `python manage.py check`, jalankan `collectstatic` jika ada static baru, lalu ringkas file yang diubah dan apa yang harus saya cek di browser.
```

## Prompt 1: Audit (hanya baca, belum ubah apa pun)

```
Ikuti aturan di CLAUDE.md. Tugas kali ini READ-ONLY, jangan mengubah file.
1. Petakan semua template, base template, include/partial, dan file static (CSS/JS/gambar) yang ada.
2. Daftarkan setiap halaman per role (petani, konsumen, HOREKA, bank, admin, dan role lain yang kamu temukan di kode): URL, nama template, fungsi halaman.
3. Daftarkan CSS framework dan font yang sekarang dipakai, serta konfigurasi STATIC_URL/STATIC_ROOT/STATICFILES_DIRS.
4. Cari ketidakkonsistenan penamaan menu/judul (contoh: "Sisaku" vs "Marketplace Surplus" vs "Surplus") dan cara harga serta tanggal diformat.
5. Cari semua penggunaan emoji sebagai ikon.
Keluarkan hasilnya sebagai docs/audit.md dengan tabel ringkas. Jangan sarankan perubahan logika.
```

## Prompt 2: Design spec dan token

```
Ikuti CLAUDE.md. Buat file docs/design-spec.md berisi isi di bawah PERSIS apa adanya. Lalu buat static/css/tokens.css dari bagian "Warna (Token CSS)". Pasang font lewat base template (preconnect, display=swap, hanya bobot yang dipakai). Jangan restyle halaman dulu.

=== ISI design-spec.md ===
# NusaTani Design Spec
Konsep: "Kabut dataran tinggi". Latar pegunungan hijau berlapis + kabut, panel kaca buram di atasnya. Mood: segar, tenang, premium, tepercaya.

## Warna (Token CSS)
:root {
 --ink:#0F2A1D; --ink-muted:#3F5A4B;
 --green-900:#0B3D2A; --green-800:#166534; --green-700:#15803D; --green-600:#16A34A; --green-500:#22C55E;
 --mint-50:#F0FDF4; --mint-100:#DCFCE7; --lime-300:#BEF264;
 --cream:#FEF9E7; --amber-100:#FEF3C7; --amber-700:#B45309;
 --blue-100:#E0F2FE; --blue-700:#0369A1; --red-100:#FEE2E2; --red-700:#B91C1C;
 --sky-top:#E8F8EE; --sky-bottom:#FFFBEA;
 --mtn-far:#CDEBD6; --mtn-mid:#9ED2B2; --mtn-near:#5FAF84; --mtn-front:#2F8A5E;
 --glass-light:rgba(255,255,255,.62); --glass-strong:rgba(255,255,255,.82); --glass-dark:rgba(11,61,42,.62);
 --glass-border:rgba(255,255,255,.6); --glass-shadow:0 8px 32px rgba(11,61,42,.14);
 --blur-sm:8px; --blur-md:14px; --blur-max:16px;
 --radius-sm:10px; --radius-md:14px; --radius-lg:20px; --radius-xl:28px; --radius-pill:999px;
 --space-1:4px; --space-2:8px; --space-3:12px; --space-4:16px; --space-6:24px; --space-8:32px; --space-12:48px; --space-16:64px;
 --accent:#15803D;
}
Accent per role (set di <body data-role="...">):
 petani #15803D | konsumen #0F766E | horeca #B45309 | bank #1D4ED8 | admin #1F3A33.
Semua role memakai base hijau yang sama, hanya --accent yang berganti (tombol utama, tab aktif, ikon KPI).
Kontras teks minimal 4.5:1 (WCAG AA). Verifikasi pasangan warna dengan WebAIM Contrast Checker; kalau ada yang gagal, gelapkan warnanya.

## Tipografi
Heading: "Plus Jakarta Sans" 700/800. Body & UI: "Inter" 400/500/600. Angka/harga/KPI: Inter dengan font-variant-numeric: tabular-nums.
Skala (px): 12 (eyebrow/caption, uppercase, tracking .08em) / 14 (teks kecil) / 16 (body) / 18 / 20 (judul kartu) / 24 (judul seksi) / 32 (H1 halaman) / 44 (hero, hanya di dashboard & landing).
Line-height: body 1.6, heading 1.2, letter-spacing heading -0.02em. Fallback: system-ui, sans-serif.

## Latar (gunung)
Layer fixed di belakang semua konten (pakai elemen/pseudo-element position:fixed, BUKAN background-attachment:fixed, karena sering bermasalah di mobile).
- Langit: gradient 180deg --sky-top -> --sky-bottom.
- Glow matahari: radial-gradient lembut warna --lime-300 opacity ~.35 di kanan atas.
- 4 punggung gunung SVG berlapis di bagian bawah (tinggi ~55vh): far -> mid -> near -> front, warna --mtn-*, lapisan depan sedikit lebih gelap. Di antara lapisan beri kabut (gradient putih transparan ~.35). Lapisan depan boleh diberi tekstur terasering sawah sangat halus.
- SVG inline atau satu file ringan (<10KB). Di layar <600px tampilkan 2 lapisan saja.
- DILARANG menimpa latar dengan overlay putih di atas 25% opacity; gunung harus terlihat.

## Glass (aturan)
.glass: background var(--glass-light); backdrop-filter: blur(var(--blur-md)) saturate(140%); border:1px solid var(--glass-border); box-shadow var(--glass-shadow); radius lg.
.glass-strong: dipakai untuk konten padat teks (form, tabel, modal): background var(--glass-strong).
.glass-dark: hero/banner, teks putih: background var(--glass-dark).
Wajib: -webkit-backdrop-filter, dan fallback @supports not (backdrop-filter: blur(1px)) dengan background hampir solid (rgba(255,255,255,.95)).
Blur maksimum 16px. Kartu yang berulang dalam grid (produk, pesanan) memakai --blur-sm. backdrop-filter hanya di: navbar, hero, modal, panel utama.

## Layout
Container max 1200px, padding 20px (mobile) / 24px (desktop). Grid 12 kolom, jarak antar kartu 24px.
Navbar: melayang, sticky, top 12px, radius xl, tinggi 64px, .glass. Kiri: logo; tengah: menu; kanan: role badge, nama, tombol Keluar. Di mobile jadi hamburger.
Header halaman: eyebrow (12px uppercase) + H1 + subjudul di kiri, tombol aksi di kanan.
Dashboard: hero .glass-dark -> baris 4 KPI -> baris aksi cepat -> 2 kolom (Fokus peran | Pesanan terbaru).
Katalog: grid 4 kolom >=1200px, 3 kolom >=900px, 2 kolom >=600px, 1 kolom di bawahnya. Gambar produk rasio 4/3.
Jarak antar seksi 48px.

## Komponen
- Tombol: primer (isi --accent, teks putih), sekunder (outline accent, latar glass), ghost. Tinggi 44px, radius md, hover naik 2px, focus-visible ring 3px accent opacity .4.
- Kartu produk: gambar, chip (Surplus/Tersedia) di atas gambar, nama, nama petani, harga "Rp 22.000" + satuan, indikator stok (bar tipis), tombol "Detail".
- KPI card: ikon SVG di kotak 40px, label 12px uppercase, angka 32px tabular-nums, keterangan 14px.
- Chip status (selalu teks + ikon kecil, jangan hanya warna): Menunggu Konfirmasi (amber), Menunggu QC (amber gelap), Dalam Produksi (biru), Siap Dikirim (hijau), Dikirim (teal), Selesai (hijau tua), Dibatalkan (merah).
- Form: input .glass-strong, label di atas, tinggi 44px, error merah + ikon + teks.
- Tabel: baris .glass-strong, header sticky, zebra halus.
- Modal, toast, empty state (ilustrasi sprout SVG + teks + tombol aksi), skeleton loading, footer tipis.
- Ikon: satu set SVG (Lucide atau Tabler), stroke 1.75px. TANPA emoji sebagai ikon.

## Format data
Rupiah: "Rp 22.000". Tanggal: "20 Nov 2026". Selalu tampilkan satuan harga (mis. "/ pack") sesuai field yang ada. Jika tidak ada field satuan, tulis TODO dan laporkan.

## Gerak & aksesibilitas
Transisi 150-200ms ease-out. @media (prefers-reduced-motion: reduce) matikan animasi. Target sentuh >= 44px. Fokus keyboard selalu terlihat. Status tidak boleh hanya berbasis warna.
=== AKHIR ===
```

## Prompt 3: Latar gunung

```
Ikuti CLAUDE.md dan docs/design-spec.md bagian "Latar (gunung)".
Buat static/css/background.css dan sisipkan SVG gunung ringan (inline di base template atau satu file SVG di static/img).
Syarat:
- Layer position:fixed di belakang konten, z-index paling bawah, pointer-events:none.
- 4 lapisan gunung + kabut + glow matahari sesuai spec; warna memakai variabel --mtn-*.
- Hapus/kurangi overlay putih tebal yang sekarang menutupi latar, agar gunung terlihat.
- Responsif: di <600px hanya 2 lapisan.
- Halaman tetap terbaca di atas latar ini (belum ada panel kaca, itu langkah berikutnya, jadi sementara beri panel putih semi-solid agar teks aman).
Setelah selesai, jelaskan cara memverifikasi di browser dan di PythonAnywhere (collectstatic + Reload).
```

## Prompt 4: Base layout dan komponen kaca

```
Ikuti CLAUDE.md dan docs/design-spec.md.
Refactor base template dan buat static/css/components.css yang berisi: .glass, .glass-strong, .glass-dark, navbar melayang (dengan dropdown "Menu <role>" dan hamburger mobile), tombol, chip, form field, tabel, modal, toast, empty state, skeleton, footer.
- <body data-role="..."> diisi dari role user yang sedang login (pakai variabel yang sudah tersedia di template; JANGAN mengubah views. Jika belum tersedia, tulis TODO dan tanyakan).
- Tambahkan fallback @supports dan prefix -webkit-backdrop-filter.
- Ganti semua emoji ikon di navbar/komponen dengan SVG (Lucide atau Tabler, inline sprite).
- Hilangkan elemen dobel (mis. badge role yang muncul di navbar dan di hero).
Jangan menyentuh isi halaman selain header/footer.
```

## Prompt 5: Katalog, detail produk, dan halaman Sisaku

```
Ikuti CLAUDE.md dan docs/design-spec.md (komponen Kartu produk, grid katalog, format data).
Restyle halaman katalog, detail produk, dan halaman surplus.
1. Samakan istilah: pakai "Sisaku" untuk menu, judul halaman, dan filter (hapus "Marketplace Surplus"/"Surplus"), kecuali kamu menemukan alasan teknis. Kalau begitu, laporkan dulu.
2. Harga diformat "Rp 22.000" lewat template filter (kalau Django: pakai humanize intcomma dengan LANGUAGE_CODE "id", atau buat filter rupiah sendiri; jelaskan pilihanmu). Tampilkan satuan harga sesuai field; kalau tidak ada, TODO.
3. Kartu produk sesuai spec: gambar rasio 4/3, chip di atas gambar, indikator stok, tombol Detail.
4. Jika produk belum punya foto, tampilkan ilustrasi SVG sprout bergradien hijau-krem yang rapi sebagai placeholder, bukan area kosong besar.
5. Hapus tombol/filter yang berulang di halaman Sisaku; satu bar aksi saja.
6. Blur kartu memakai --blur-sm.
```

## Prompt 6: Dashboard semua role

```
Ikuti CLAUDE.md dan docs/design-spec.md (layout Dashboard, KPI card, chip status).
docs/audit.md sudah memuat semua role. Restyle dashboard SETIAP role yang ada di audit (termasuk role admin) dengan struktur yang sama:
hero .glass-dark -> 4 KPI card -> baris aksi cepat -> 2 kolom (Fokus peran | Pesanan terbaru).
- Konten, angka, tautan, dan permission tidak boleh berubah; hanya tampilan.
- Accent berbeda per role lewat data-role, sisanya identik.
- Daftar pesanan memakai chip status sesuai spec (teks + ikon).
- Role admin: gunakan komponen yang sama persis, tanpa menambah atau mengurangi fitur.
Kerjakan satu role per commit dan laporkan halaman apa yang perlu saya cek per role.
```

## Prompt 7: Form, auth, pesanan, QC, aset, tabel

```
Ikuti CLAUDE.md dan docs/design-spec.md.
Restyle halaman login/daftar, form tambah/ubah produk, daftar & detail pesanan (Pesananku), QC (Qualityku), aset (Asetku), pembiayaan (BANKKU), dan Mentorku jika ada.
- Form pakai .glass-strong, label di atas, error dengan ikon + teks, tombol sesuai spec.
- Tabel/daftar memakai .glass-strong dengan header sticky di desktop dan berubah menjadi kartu bertumpuk di mobile.
- Tambahkan empty state dan skeleton loading untuk daftar yang bisa kosong.
- Jangan mengubah validasi, field, atau alur submit.
```

## Prompt 8: QA akhir (responsif, aksesibilitas, performa)

```
Ikuti CLAUDE.md dan docs/design-spec.md. Lakukan pengecekan akhir dan perbaiki yang gagal (hanya tampilan):
1. Responsif di 360, 768, 1280, 1440px: tidak ada scroll horizontal, navbar mobile berfungsi.
2. Kontras: cek pasangan teks/latar di semua panel kaca terhadap latar gunung (hitung atau minta alat contrast checker); target >= 4.5:1. Naikkan opacity panel bila gagal.
3. Fallback tanpa backdrop-filter tetap terbaca.
4. prefers-reduced-motion mematikan animasi; fokus keyboard terlihat; target sentuh >= 44px.
5. Performa: hitung jumlah elemen ber-backdrop-filter per halaman (usahakan sedikit), ukuran CSS/SVG/font, dan jalankan Lighthouse jika bisa.
6. Konsistensi penamaan menu dan format Rupiah/tanggal di semua halaman.
7. Tidak ada emoji ikon tersisa.
Buat docs/qa-report.md berisi daftar lulus/gagal dan apa yang sudah diperbaiki.
```

---

## 5. Catatan di luar permintaan (proposal PDF)

Rapikan ini sebelum juri membandingkan web dengan dokumen:

- **Komisi tidak konsisten.** Business Model Canvas menulis komisi 3%, sedangkan Bab III memakai 15% (HOREKA) dan 18% (rumah tangga). Web harus mengikuti salah satunya.
- **Margin starter-kit tidak cocok.** Harga jual Rp8.000.000 dikurangi HPP Rp7.000.000 adalah Rp1.000.000, tetapi tabel menulis margin Rp1.200.000.
- **"Biaya bulanan platform Rp60.000.000"** di struktur biaya BMC terlihat sama dengan CAPEX Rp60 juta di Bab III, padahal biaya tetap bulanan di tabelnya jauh lebih kecil.
- **Ejaan inkonsisten:** "Platfrom", "Mikrogreen/Microgreen", dan judul sampul yang kacau.
