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
