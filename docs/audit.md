# Audit Tampilan NusaTani — docs/audit.md

Dokumen ini adalah hasil pemetaan read-only terhadap semua template, base template, include/partial, dan file static yang ada di proyek NusaTani. Tidak ada perubahan logika yang disarankan.

---

## 1. Struktur Template

### 1.1 Base Template

| File | Path | Keterangan |
|------|------|------------|
| Base template | `templates/base.html` | Template utama yang di-extends oleh semua halaman. Berisi navbar, toast, modal konfirmasi, footer, dan blok `content`. |
| Auth base | `templates/accounts/auth_base.html` | Base untuk halaman autentikasi (login, register). Meng-extends `base.html`, menyembunyikan `public-hero`, menyediakan panel auth dengan `auth-card`. |

### 1.2 Template per App

| App | Template | Path |
|-----|----------|------|
| accounts | login | `templates/registration/login.html` |
| accounts | guide | `templates/accounts/guide.html` |
| accounts | register | `templates/accounts/register.html` |
| accounts | dashboard | `templates/accounts/dashboard.html` |
| accounts | profile | `templates/accounts/profile.html` |
| products | catalog | `templates/products/catalog.html` |
| products | my_products | `templates/products/my_products.html` |
| products | product_form | `templates/products/product_form.html` |
| products | product_detail | `templates/products/product_detail.html` |
| products | inventory_form | `templates/products/inventory_form.html` |
| orders | my_orders | `templates/orders/my_orders.html` |
| orders | incoming_orders | `templates/orders/incoming_orders.html` |
| orders | order_form | `templates/orders/order_form.html` |
| orders | order_detail | `templates/orders/order_detail.html` |
| orders | payment_form | `templates/orders/payment_form.html` |
| orders | status_form | `templates/orders/status_form.html` |
| orders | _order_table (partial) | `templates/orders/_order_table.html` |
| quality_control | queue | `templates/quality_control/queue.html` |
| quality_control | inspection_form | `templates/quality_control/inspection_form.html` |
| deliveries | delivery_list | `templates/deliveries/delivery_list.html` |
| deliveries | delivery_detail | `templates/deliveries/delivery_detail.html` |
| deliveries | delivery_form | `templates/deliveries/delivery_form.html` |
| assets | asset_list | `templates/assets/asset_list.html` |
| assets | asset_form | `templates/assets/asset_form.html` |
| assets | asset_detail | `templates/assets/asset_detail.html` |
| mentorship | mentorship_list | `templates/mentorship/mentorship_list.html` |
| mentorship | mentorship_form | `templates/mentorship/mentorship_form.html` |
| mentorship | mentorship_detail | `templates/mentorship/mentorship_detail.html` |
| mentorship | activity_form | `templates/mentorship/activity_form.html` |
| bankku | dashboard | `templates/bankku/dashboard.html` |
| bankku | my_performance | `templates/bankku/my_performance.html` |

Tidak ada include/partial terpisah selain `_order_table.html` yang digunakan sebagai partial tabel pesanan.

---

## 2. File Static

### 2.1 CSS

| File | Path | Keterangan |
|------|------|------------|
| app.css | `static/css/app.css` | Custom CSS NusaTani. Variabel warna hijau/orang, glassmorphism, komponen card, badge, toast, modal, dashboard stats, onboarding wizard, auth panel. |

### 2.2 Gambar

| File | Path | Keterangan |
|------|------|------------|
| favicon.svg | `static/images/favicon.svg` | Favicon SVG |
| favicon-32.png | `static/images/favicon-32.png` | Favicon 32x32 PNG |
| favicon.ico | `static/images/favicon.ico` | Favicon ICO |
| apple-touch-icon.png | `static/images/apple-touch-icon.png` | Apple touch icon |
| highland-sawah.jpg | `static/images/highland-sawah.jpg` | Foto latar sawah terasering |
| highland.svg | `static/images/highland.svg` | Siluet gunung dataran tinggi |

Tidak ada file JavaScript custom di `static/`. JS hanya ada sebagai inline `<script>` di dalam template dan Bootstrap Bundle dari CDN.

---

## 3. Konfigurasi Static (config/settings.py)

| Pengaturan | Nilai | Keterangan |
|------------|-------|------------|
| `STATIC_URL` | `static/` | URL publik untuk file statis |
| `STATIC_ROOT` | `BASE_DIR / "staticfiles"` | Tujuan `collectstatic` di produksi |
| `STATICFILES_DIRS` | `[BASE_DIR / "static"]` | Direktori sumber statis saat development |
| WhiteNoise | `whitenoise.middleware.WhiteNoiseMiddleware` | Middleware untuk serve statis di produksi |
| STORAGES staticfiles | `CompressedManifestStaticFilesStorage` (non-DEBUG) / `StaticFilesStorage` (DEBUG) | Kompresi + hash nama file di produksi |

---

## 4. CSS Framework dan Font

| Komponen | Sumber | Versi |
|----------|--------|-------|
| CSS Framework | `https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css` | Bootstrap 5.3.3 |
| JS Framework | `https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js` | Bootstrap 5.3.3 Bundle |
| Font 1 | `https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700` | Inter (body text) |
| Font 2 | `https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800` | Plus Jakarta Sans (heading) |

Tidak ada framework CSS lain yang dicampur. Tidak ada file JS custom eksternal.

---

## 5. Peta Halaman per Role

### 5.1 Route dan URL

| URL | Namespace:name | Template | Fungsi Halaman |
|-----|----------------|----------|----------------|
| `/` | `home` | (redirect) | Arahkan ke panduan atau login |
| `/health/` | `health` | (text) | Status layanan |
| `/admin/` | `admin:index` | Django admin | Panel administrasi Django |
| `/accounts/panduan/` | `accounts:guide` | `accounts/guide.html` | Panduan pendaftaran per peran |
| `/accounts/daftar/` | `accounts:register` | `accounts/register.html` | Formulir pendaftaran akun baru |
| `/accounts/login/` | `accounts:login` | `registration/login.html` | Halaman masuk + tombol demo |
| `/accounts/demo/` | `accounts:demo_login` | (redirect) | Masuk cepat sebagai demo |
| `/accounts/logout/` | `accounts:logout` | (redirect) | Keluar dari akun |
| `/accounts/profil/` | `accounts:profile` | `accounts/profile.html` | Ubah profil pengguna |
| `/accounts/dashboard/` | `accounts:dashboard` | `accounts/dashboard.html` | Dashboard sesuai peran |
| `/products/` | `products:catalog` | `products/catalog.html` | Katalog produk |
| `/products/surplus/` | `products:surplus` | `products/catalog.html` | Katalog surplus (sama template) |
| `/products/saya/` | `products:my_products` | `products/my_products.html` | Kelola produk milik petani |
| `/products/tambah/` | `products:create` | `products/product_form.html` | Tambah produk baru |
| `/products/<int:pk>/` | `products:detail` | `products/product_detail.html` | Detail produk |
| `/products/<int:pk>/ubah/` | `products:update` | `products/product_form.html` | Ubah produk |
| `/products/<int:pk>/stok/` | `products:inventory_update` | `products/inventory_form.html` | Perbarui stok |
| `/orders/saya/` | `orders:my_orders` | `orders/my_orders.html` | Pesanan saya (pembeli) |
| `/orders/masuk/` | `orders:incoming` | `orders/incoming_orders.html` | Pesanan masuk (petani) |
| `/orders/preorder/` | `orders:preorder_create` | `orders/order_form.html` | Buat pre-order (HOREKA) |
| `/orders/surplus/` | `orders:surplus_create` | `orders/order_form.html` | Buat pesanan surplus |
| `/orders/<int:pk>/` | `orders:detail` | `orders/order_detail.html` | Detail pesanan |
| `/orders/<int:pk>/status/` | `orders:update_status` | `orders/status_form.html` | Ubah status pesanan |
| `/orders/<int:pk>/pembayaran/` | `orders:update_payment` | `orders/payment_form.html` | Ubah status pembayaran |
| `/qc/` | `quality_control:queue` | `quality_control/queue.html` | Antrean pemeriksaan QC |
| `/qc/<int:pk>/periksa/` | `quality_control:inspect` | `quality_control/inspection_form.html` | Formulir pemeriksaan QC |
| `/qc/pesanan/<int:pk>/ajukan/` | `quality_control:submit_to_qc` | (redirect) | Ajukan pesanan ke QC |
| `/deliveries/` | `deliveries:list` | `deliveries/delivery_list.html` | Daftar pengiriman |
| `/deliveries/<int:pk>/` | `deliveries:detail` | `deliveries/delivery_detail.html` | Detail pengiriman |
| `/deliveries/siapkan/<int:pk>/` | `deliveries:prepare` | (redirect) | Siapkan pengiriman |
| `/deliveries/<int:pk>/status/` | `deliveries:update_status` | `deliveries/delivery_form.html` | Ubah status pengiriman |
| `/assets/` | `assets:list` | `assets/asset_list.html` | Daftar aset usaha |
| `/assets/baru/` | `assets:create` | `assets/asset_form.html` | Tambah aset baru |
| `/assets/<int:pk>/` | `assets:detail` | `assets/asset_detail.html` | Detail aset |
| `/assets/<int:pk>/ubah/` | `assets:update` | `assets/asset_form.html` | Ubah aset |
| `/assets/<int:pk>/hapus/` | `assets:delete` | (redirect) | Hapus aset |
| `/mentorship/` | `mentorship:list` | `mentorship/mentorship_list.html` | Daftar pendampingan |
| `/mentorship/baru/` | `mentorship:create` | `mentorship/mentorship_form.html` | Tambah pendampingan |
| `/mentorship/<int:pk>/` | `mentorship:detail` | `mentorship/mentorship_detail.html` | Detail pendampingan |
| `/mentorship/<int:pk>/ubah/` | `mentorship:update` | `mentorship/mentorship_form.html` | Ubah pendampingan |
| `/mentorship/<int:pk>/kegiatan/` | `mentorship:activity_create` | `mentorship/activity_form.html` | Tambah kegiatan pendampingan |
| `/bankku/` | `bankku:dashboard` | `bankku/dashboard.html` | Dashboard BANKKU |
| `/bankku/performaku/` | `bankku:my_performance` | `bankku/my_performance.html` | Performaku (petani) |

### 5.2 Akses per Role (berdasar decorator `@role_required` di views)

| Role | Halaman yang Terbuka | Catatan |
|------|---------------------|---------|
| **Petani (farmer)** | Dashboard, Katalog, Sisaku, Produk Saya, Pesanan Masuk, Pengiriman, Asetku, Mentorku, Performaku | Tambah produk, ubah stok, ajukan QC |
| **HOREKA (horeca)** | Dashboard, Katalog, Sisaku, Pesanan Saya, Pengiriman | Buat pre-order |
| **Konsumen (consumer)** | Dashboard, Katalog, Sisaku, Pesanan Saya, Pengiriman | Belanja surplus |
| **QC (qc)** | Dashboard, Antrean QC | Periksa produk |
| **Mentor (mentor)** | Dashboard, Mentorku | Jadwalkan pendampingan |
| **Bank (bank)** | Dashboard, BANKKU | Pantau performa petani |
| **Admin (admin)** | Dashboard Administrator, semua halaman via superuser | Akses ke `/admin/` |
| **Superuser** | Semua halaman | Bypass semua pembatasan role |

---

## 6. Ketidakkonsistenan Penamaan Menu dan Judul

### 6.1 Nama Menu di Navigasi (base.html)

| Label di Menu | URL | App | Catatan |
|---------------|-----|-----|---------|
| Dashboard Saya | `accounts:dashboard` | accounts | — |
| Katalog | `products:catalog` | products | — |
| Sisaku | `products:surplus` | products | Nama menu "Sisaku" tapi URL name `surplus` |
| Pesanan Masuk | `orders:incoming` | orders | Dropdown farmer |
| Pengiriman | `deliveries:list` | deliveries | Digunakan farmer dan pembeli |
| Asetku | `assets:list` | assets | — |
| Mentorku | `mentorship:list` | mentorship | — |
| Performaku | `bankku:my_performance` | bankku | — |
| Pesanan Saya | `orders:my_orders` | orders | Dropdown pembeli |
| Antrean QC | `quality_control:queue` | quality_control | — |
| BANKKU | `bankku:dashboard` | bankku | Huruf besar semua |

### 6.2 Ketidakkonsistenan yang Ditemukan

1. **"Sisaku" vs "Surplus"**: Menu navigasi menulis "Sisaku" tetapi URL name dan pola URL adalah `surplus`. Template catalog menggunakan satu template untuk keduanya dengan parameter `surplus_only`.
2. **"Pesanan Masuk" vs "Pesanan Saya"**: Kedua halaman orders menggunakan pola nama yang berbeda untuk farmer (masuk) dan pembeli (saya). Ini sengaja untuk membedakan arah pesanan.
3. **Format Harga**: Digunakan helper `_rupiah()` di `accounts/views.py` (format "Rp" dengan titik sebagai pemisah ribuan). Beberapa template mungkin menampilkan harga langsung tanpa diformatkan (perlu verifikasi lebih lanjut di template order/product).
4. **Format Tanggal**: Menggunakan filter Django `{% now "j F Y" %}` di dashboard, dan format `{{ order.created_at:%d %b %Y }}` di helper `_order_activity`. Konsisten menggunakan bahasa Indonesia.

---

## 7. Penggunaan Emoji sebagai Ikon

| Emoji | Tempat Digunakan | Keterangan |
|-------|------------------|------------|
| 🌱 | base.html (brand-mark, footer), auth_base.html (brand-mark), product_detail.html, catalog.html, dashboard.html (hero-mark), guide.html (flow-icon) | Ikon brand NusaTani |
| 📦 | dashboard.html (cycle icon) | Ikon produk/stok |
| ✅ | dashboard.html (cycle icon), guide.html (check-list), base.html (toast success) | Selesai/lolos |
| 🌿 | dashboard.html (empty-state) | Ikon kosong |
| 🔍 | roles.py (QC icon) | Ikon QC |
| 📥 | accounts/views.py (action icon) | Ikon pesanan masuk |
| 🧰 | accounts/views.py (action icon) | Ikon aset |
| 📈 | accounts/views.py (action icon) | Ikon performa |
| 🗓️ | accounts/views.py (action/icon) | Ikon pre-order/jadwal |
| ♻️ | accounts/views.py (action/icon) | Ikon surplus |
| 💳 | accounts/views.py (action/icon) | Ikon pembayaran |
| 🗂️ | accounts/views.py (action icon) | Ikon daftar |
| 👁 | login.html (password toggle) | Tombol tampilkan/sembunyikan kata sandi |
| → | login.html, guide.html, register.html, mentorship_list.html, delivery_detail.html, dashboard.html | Panah navigasi |
| ← | guide.html | Panah kembali |
| ○ | login.html (demo role check) | Checkbox kosong demo |
| ✓ | login.html, guide.html (role-check) | Tanda centang pilihan |
| ⚡ | login.html (demo button) | Ikon cepat/demo |
| 🧭 | login.html, register.html, guide.html | Ikon panduan |
| 🙈 | login.html (JS password toggle) | Ikon sembunyikan kata sandi |
| 🛒 | accounts/views.py (action icon) | Ikon katalog |
| 🚚 | accounts/views.py (action icon) | Ikon pengiriman |
| ✅/⛔/⚠️/🐞/ℹ️ | base.html (toast icon) | Ikon tipe pesan toast |

---

## 8. File yang Diperlukan untuk Perbaikan Tampilan (Read-Only)

Jika ada perubahan tampilan yang dibutuhkan, file-file berikut adalah target edit yang valid (hanya template dan static):

- `templates/base.html` — navbar, footer, toast, modal
- `templates/accounts/auth_base.html` — panel auth
- `templates/registration/login.html` — halaman masuk
- `templates/accounts/guide.html` — panduan pendaftaran
- `templates/accounts/dashboard.html` — dashboard per role
- `templates/accounts/register.html` — pendaftaran
- `templates/accounts/profile.html` — profil
- Semua template di `templates/products/`, `templates/orders/`, `templates/quality_control/`, `templates/deliveries/`, `templates/assets/`, `templates/mentorship/`, `templates/bankku/`
- `static/css/app.css` — styling custom
- `static/images/*` — aset gambar

File yang **TIDAK boleh diubah** (read-only constraint): `config/settings.py`, `config/urls.py`, semua `urls.py` di app, semua `views.py`, semua `models.py`, semua `forms.py`, semua migrasi.

---
