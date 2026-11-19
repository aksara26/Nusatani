# 🌱 NusaTani
### Platform Digital Marketplace Microgreens untuk Petani, HOREKA, dan Konsumen

NusaTani adalah platform digital yang menghubungkan petani microgreens dengan pembeli, khususnya sektor HOREKA (Hotel, Restoran, dan Kafe) serta konsumen rumah tangga.

Platform ini dirancang untuk membantu petani mengelola pesanan, stok, kualitas produk, aset usaha, dan pemasaran. Pembeli dapat melakukan pemesanan terjadwal maupun membeli produk surplus petani.

Dokumen ini disusun **dari yang paling penting hingga yang bersifat umum**: dimulai dari peta prioritas dan tahap implementasi, lalu detail modul inti, data, teknis setup/deployment, dan terakhir pengujian serta batasan MVP.

---

## 1. Peta Prioritas Pengembangan

Tujuh tahap berikut merupakan critical path NusaTani. Urutannya mengikuti ketergantungan teknis dan nilai bisnis: fondasi → produk → transaksi → kualitas → operasional pendukung → pembiayaan → pengujian akhir.

| Tahap | Fokus | Prioritas | Gate / Hasil Minimal |
|---|---|---|---|
| **1. Fondasi & Akses** | Proyek Django, environment, database, login, role, dashboard per role | **P0** | Skenario 1–3 lolos: petani, HOREKA, dan konsumen bisa login serta membuka dashboard masing-masing |
| **2. Deploy Tipis sejak Awal** | GitHub, Render, `build.sh`, gunicorn, WhiteNoise, environment variables | **P1** | URL publik dapat diakses; `migrate` dan `collectstatic` sukses di Render |
| **3. Katalog & Stok** | `Variety`, `Product`, `Inventory`, marketplace surplus | **P0** | Skenario 4 lolos: petani menambah produk dan produk muncul di katalog |
| **4. Inti Transaksi** | Pre-order HOREKA, pesanan konsumen, `Order`/`OrderItem`, status pesanan, pembayaran simulasi | **P0** | Skenario 5–6 lolos: pesanan tercatat dan statusnya berjalan |
| **5. Quality Gate & Pengiriman** | `QualityInspection`, status QC, aturan blocker pengiriman, `Delivery` simulasi | **P0** | Skenario 7–10 lolos; produk yang ditolak QC tidak bisa dikirim |
| **6. Operasional Petani & Mentoring** | `Asset` (Asetku), `Mentorship` (Mentorku) | **P1** | Aset dan catatan pendampingan bisa dicatat serta dilihat petani |
| **7. BANKKU & Pengujian Akhir** | `FarmerPerformance`, `FinancingAssessment`, hardening, 12 skenario uji | **P2** (uji & keamanan tetap wajib) | Skenario 11–12 lolos; data demo dibersihkan sebelum pemakaian nyata |

**Cara membaca prioritas:**

- **P0 — tidak boleh dilewati:** tahap 1, 3, 4, 5. Ini membentuk alur inti *petani → produk → pesanan → QC → pengiriman*.
- **P1 — sangat dianjurkan:** tahap 2 dan 6. Deploy sejak awal memberi umpan balik lebih cepat; aset dan mentoring melengkapi profil petani.
- **P2 — boleh ditunda:** indikator pembiayaan di tahap 7 karena sifatnya simulasi dan bergantung pada data dari tahap 3–6.

Dua penyesuaian terhadap rencana awal:

1. **Deployment naik dari tahap terakhir ke tahap 2** sebagai iris tipis, lalu diulang setiap tahap. Ini mencegah aplikasi hanya berjalan di komputer lokal.
2. **QC dan pengiriman dikerjakan sebelum Asetku/Mentorku/BANKKU**, karena produk tidak boleh masuk pengiriman sebelum dinyatakan lolos QC.

---

## 2. Tujuan Proyek

- Membantu petani microgreens menjangkau pasar yang lebih luas.
- Mempermudah pemesanan produk oleh HOREKA.
- Mengurangi potensi produk surplus yang tidak terjual.
- Menyediakan sistem pemeriksaan kualitas produk.
- Membantu petani mencatat aset dan perkembangan usaha.
- Menyediakan data usaha sebagai dasar evaluasi kelayakan pembiayaan.

---

## 3. Tahapan Implementasi Bertahap

Detail pengerjaan sesuai peta prioritas di Bab 1. Centang satu per satu setelah gate-nya terpenuhi.

### Tahap 1 — Fondasi & Akses (P0)

- [ ] Membuat proyek Django beserta folder `config`.
- [ ] Menyiapkan `settings.py` yang membaca konfigurasi dari environment variable.
- [ ] Menghubungkan Django ke PostgreSQL Supabase.
- [ ] Membuat model `User` dengan role: petani, HOREKA, konsumen, QC, mentor, bank, administrator.
- [ ] Membuat alur login/logout dan pengalihan ke dashboard sesuai role.
- [ ] Membuat dashboard minimal untuk setiap role.

**Gate:** skenario 1, 2, dan 3 di Bab 17 lolos.

**Lihat juga:** Bab 11 (setup lokal), Bab 12 (Supabase), Bab 8 (hak akses).

### Tahap 2 — Deploy Tipis sejak Awal (P1)

- [ ] Menyiapkan `.gitignore` dan `.env.example`, memastikan `.env` tidak ikut ter-commit.
- [ ] Mengunggah kode ke GitHub.
- [ ] Membuat Web Service Render dan menghubungkan repository `nusatani`.
- [ ] Mengisi environment variables: `SECRET_KEY`, `DEBUG`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`.
- [ ] Menyiapkan `build.sh` dan Start Command `gunicorn config.wsgi:application`.
- [ ] Mengaktifkan WhiteNoise untuk file static.
- [ ] Memverifikasi `migrate` dan `collectstatic` berjalan di Render.

**Gate:** alamat publik Render menampilkan aplikasi; deploy diulang setelah setiap tahap berikutnya.

**Lihat juga:** Bab 13, Bab 14, Bab 15.

### Tahap 3 — Katalog & Stok (P0)

- [ ] Membuat katalog varietas (`Variety`).
- [ ] Membuat data produk (`Product`) beserta foto dan harga.
- [ ] Membuat pengelolaan stok (`Inventory`).
- [ ] Membuat marketplace produk surplus petani.
- [ ] Membuat form petani untuk menambah dan mengubah produk.

**Gate:** skenario 4 di Bab 17 lolos.

**Lihat juga:** Bab 4.2, Bab 7.

### Tahap 4 — Inti Transaksi (P0)

- [ ] Membuat sistem pre-order HOREKA dengan perkiraan 7–14 hari sebelum kebutuhan.
- [ ] Membuat sistem pesanan konsumen untuk produk yang tersedia.
- [ ] Membuat `Order` dan `OrderItem` beserta sepuluh status pesanan.
- [ ] Membuat daftar pesanan yang diterima petani.
- [ ] Membuat catatan pembayaran simulasi (`PaymentRecord`).

**Gate:** skenario 5 dan 6 di Bab 17 lolos; status pesanan tidak boleh meloncat ke pengiriman.

**Lihat juga:** Bab 4.1, Bab 5, Bab 6.

### Tahap 5 — Quality Gate & Pengiriman (P0)

- [ ] Membuat modul Quality Control dan `QualityInspection`.
- [ ] Membuat status QC: menunggu pemeriksaan, sedang diperiksa, lolos QC, tidak lolos QC.
- [ ] Menerapkan aturan: produk belum lolos QC tidak boleh berstatus `Siap Dikirim`.
- [ ] Membuat dashboard petugas QC serta catatan perbaikan.
- [ ] Membuat simulasi kurir dan pelacakan status pengiriman (`Delivery`).

**Gate:** skenario 7–10 di Bab 17 lolos, termasuk produk yang ditolak QC tidak dapat dikirim.

**Lihat juga:** Bab 4.3, Bab 6.

### Tahap 6 — Operasional Petani & Mentoring (P1)

- [ ] Membuat modul Asetku (`Asset`) untuk rak, tray, lampu, peralatan panen, dan pengemasan.
- [ ] Menyiapkan pencatatan starter kit dan simulasi skema pembiayaan ijarah.
- [ ] Membuat modul Mentorku (`Mentorship`): materi, jadwal, catatan evaluasi, dan riwayat kegiatan.

**Gate:** petani dapat mencatat dan melihat aset serta catatan pendampingan.

**Lihat juga:** Bab 4.4, Bab 4.5.

### Tahap 7 — BANKKU & Pengujian Akhir (P2)

- [ ] Membuat `FarmerPerformance` dan dashboard BANKKU.
- [ ] Membuat `FinancingAssessment` dan indikator kelayakan sebagai simulasi.
- [ ] Memastikan secret key kuat, HTTPS, `CSRF_TRUSTED_ORIGINS`, dan cookie aman di produksi.
- [ ] Menjalankan seluruh 12 skenario pengujian di Bab 17.
- [ ] Membersihkan data pribadi/keuangan demo sebelum sistem dipakai sungguhan.

**Gate:** skenario 11 dan 12 lolos; batasan MVP di Bab 18 sudah dipahami oleh tim.

**Lihat juga:** Bab 4.6, Bab 17, Bab 18, Bab 19.

---

## 4. Modul Utama NusaTani

### 4.1 Pesananku

Fitur untuk mengelola pesanan yang diterima petani.

Informasi yang ditampilkan:
- Nomor pesanan.
- Nama pembeli.
- Produk.
- Jumlah pesanan.
- Tanggal pemesanan.
- Jadwal panen.
- Status pesanan.

### 4.2 Sisaku

Fitur untuk memasarkan produk surplus petani.

Informasi produk:
- Nama produk.
- Varietas.
- Jumlah stok.
- Harga.
- Foto produk.
- Tanggal tersedia.
- Status ketersediaan.

### 4.3 Qualityku

Fitur pemeriksaan kualitas produk.

Contoh data pemeriksaan:
- Nama produk.
- Kondisi visual.
- Kebersihan.
- Kesegaran.
- Kesesuaian berat.
- Catatan petugas QC.
- Hasil pemeriksaan.

Status QC:
- Menunggu pemeriksaan.
- Sedang diperiksa.
- Lolos QC.
- Tidak lolos QC.

### 4.4 Asetku

Fitur pencatatan aset usaha petani.

Contoh aset:
- Rak budidaya.
- Tray tanam.
- Lampu budidaya.
- Peralatan panen.
- Peralatan pengemasan.

Modul ini dapat dikembangkan untuk mencatat informasi starter kit dan skema pembiayaan ijarah sebagai simulasi.

### 4.5 Mentorku

Fitur pendampingan petani.

Informasi:
- Nama mentor.
- Materi pembelajaran.
- Jadwal pendampingan.
- Catatan evaluasi.
- Riwayat kegiatan.

### 4.6 BANKKU

Dashboard informasi performa usaha petani.

Data yang dapat ditampilkan:
- Jumlah pesanan.
- Total nilai pesanan.
- Riwayat transaksi.
- Konsistensi pemenuhan pesanan.
- Catatan kualitas.
- Data aset.
- Indikator kelayakan pembiayaan.

Indikator kelayakan pada MVP hanya berupa simulasi dan bukan keputusan kredit resmi.

---

## 5. Alur Pemesanan

### 5.1 Pemesanan HOREKA

1. HOREKA membuka katalog produk.
2. HOREKA memilih produk microgreens.
3. HOREKA menentukan jumlah pesanan.
4. HOREKA mengirim pesanan pre-order.
5. Sistem mencatat jadwal kebutuhan produk.
6. Petani menerima pesanan.
7. Petani mempersiapkan produksi.
8. Petani mengajukan produk untuk pemeriksaan QC.
9. Petugas QC melakukan pemeriksaan.
10. Produk yang lolos QC dapat masuk ke proses pengiriman.
11. Kurir menerima informasi pengiriman.
12. HOREKA menerima pesanan.
13. Sistem memperbarui status pesanan.

Perkiraan waktu pre-order yang direncanakan adalah 7–14 hari sebelum kebutuhan produk.

### 5.2 Pemesanan Konsumen

1. Konsumen membuka marketplace.
2. Konsumen memilih produk yang tersedia.
3. Konsumen melakukan pemesanan.
4. Sistem mencatat pesanan.
5. Petani mempersiapkan produk.
6. Produk melewati pemeriksaan QC.
7. Produk yang lolos QC diproses untuk pengiriman.
8. Konsumen menerima pesanan.

### 5.3 Simulasi Pembayaran

Untuk MVP, pembayaran menggunakan status simulasi.

Contoh:
- Belum dibayar.
- Menunggu konfirmasi.
- DP tercatat.
- Lunas.
- Dibatalkan.
- Pengembalian dana disimulasikan.

Rencana awal HOREKA menggunakan DP 50%, tetapi aturan pembatalan, pengembalian DP, dan waktu penyelesaian pembayaran harus ditetapkan sebelum digunakan pada transaksi sungguhan.

MVP tidak menyimpan atau menahan uang pengguna secara nyata.

---

## 6. Status Pesanan

| Status | Keterangan |
|---|---|
| Menunggu Konfirmasi | Pesanan baru masuk |
| Dikonfirmasi | Petani menerima pesanan |
| Dalam Produksi | Produk sedang disiapkan |
| Menunggu QC | Produk menunggu pemeriksaan |
| QC Lolos | Produk dinyatakan lolos |
| QC Ditolak | Produk belum memenuhi standar |
| Siap Dikirim | Produk siap diserahkan ke kurir |
| Dalam Pengiriman | Produk sedang dikirim |
| Selesai | Pesanan telah diterima |
| Dibatalkan | Pesanan dibatalkan |

Produk tidak boleh masuk ke status pengiriman sebelum dinyatakan lolos QC.

---

## 7. Struktur Database

| Model | Fungsi |
|---|---|
| User | Data akun dan role pengguna |
| FarmerProfile | Profil petani |
| HorecaProfile | Profil pembeli HOREKA |
| ConsumerProfile | Profil konsumen |
| Product | Data produk microgreens |
| Variety | Data varietas |
| Inventory | Stok produk |
| Order | Data pesanan |
| OrderItem | Rincian produk dalam pesanan |
| PaymentRecord | Catatan status pembayaran simulasi |
| QualityInspection | Data pemeriksaan QC |
| Delivery | Data pengiriman |
| Asset | Data aset petani |
| Mentorship | Data pendampingan |
| FarmerPerformance | Data performa petani |
| FinancingAssessment | Data simulasi penilaian pembiayaan |

### Relasi data secara umum

- Satu petani dapat memiliki banyak produk.
- Satu produk memiliki satu varietas.
- Satu petani dapat menerima banyak pesanan.
- Satu pesanan dapat memiliki banyak item.
- Satu produk dapat memiliki beberapa catatan pemeriksaan QC.
- Satu pesanan dapat memiliki data pengiriman.
- Satu petani dapat memiliki banyak data aset.

Gunakan relasi foreign key agar data saling terhubung dengan baik.

---

## 8. Jenis Pengguna dan Hak Akses

### A. Petani

Petani dapat:
- Mengelola profil usaha.
- Melihat katalog varietas microgreens.
- Mengelola stok produk.
- Menerima dan mengelola pesanan.
- Melihat pesanan masuk.
- Mengajukan produk untuk pemeriksaan kualitas.
- Mengelola data aset usaha.
- Melihat riwayat transaksi dan performa usaha.

### B. HOREKA

Pengguna HOREKA dapat:
- Melihat katalog produk.
- Memesan produk dengan sistem pre-order.
- Menentukan jumlah pesanan.
- Melihat status pesanan.
- Melihat riwayat pembelian.
- Melihat informasi pengiriman.

### C. Konsumen Rumah Tangga

Konsumen dapat:
- Melihat produk yang tersedia.
- Melihat produk surplus petani.
- Membeli produk sesuai stok.
- Melihat status pesanan.
- Melihat riwayat pembelian.

### D. Petugas Quality Control (QC)

Petugas QC dapat:
- Melihat daftar produk yang menunggu pemeriksaan.
- Memeriksa data kualitas.
- Mengisi hasil pemeriksaan.
- Menyetujui atau menolak produk.
- Memberikan catatan perbaikan.

### E. Mentor

Mentor dapat:
- Melihat perkembangan petani.
- Memberikan materi edukasi.
- Memberikan catatan pendampingan.
- Memantau perkembangan usaha.

### F. Bank atau Mitra Pembiayaan

Akun mitra pembiayaan dapat:
- Melihat data performa usaha petani sesuai hak akses.
- Melihat riwayat pesanan dan transaksi.
- Melihat data aset yang tercatat.
- Melihat indikator kelayakan pembiayaan.
- Memantau dashboard perkembangan petani.

### G. Administrator

Administrator dapat:
- Mengelola seluruh akun.
- Mengelola katalog produk.
- Mengelola kategori dan varietas.
- Memantau pesanan.
- Mengelola data QC.
- Mengelola data mentor.
- Melihat laporan aktivitas platform.

---

## 9. Teknologi yang Digunakan

| Teknologi | Fungsi |
|---|---|
| Python | Bahasa pemrograman utama |
| Django | Backend dan pengelolaan aplikasi |
| Django REST Framework | Pengembangan API |
| Bootstrap | Tampilan website responsif |
| PostgreSQL | Database utama |
| Supabase | Penyedia database PostgreSQL |
| GitHub | Penyimpanan kode dan version control |
| Render | Hosting aplikasi web |
| WhiteNoise | Penyajian file static Django |

### Layanan yang digunakan

- GitHub: https://github.com/
- Render: https://render.com/
- Supabase: https://supabase.com/
- Django: https://www.djangoproject.com/
- Bootstrap: https://getbootstrap.com/

**Catatan paket gratis:** Render Free dapat menidurkan aplikasi setelah tidak aktif selama periode tertentu. Supabase Free dapat menjeda proyek database yang tidak aktif selama sekitar satu minggu. Kuota dan ketentuan dapat berubah, jadi periksa halaman harga resmi sebelum deployment. Paket gratis cocok untuk demo, bukan layanan produksi yang membutuhkan ketersediaan tinggi.

- [Dokumentasi Render Free](https://render.com/docs/free)
- [Harga Supabase](https://supabase.com/pricing)

---

## 10. Struktur Folder Proyek

```text
nusatani/
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── deploy/
│   └── pythonanywhere_wsgi.py
│
├── accounts/
├── farmers/
├── products/
├── orders/
├── quality_control/
├── deliveries/
├── assets/
├── mentorship/
├── financing/
│
├── templates/
│   ├── base.html
│   ├── accounts/
│   ├── farmer/
│   ├── horeca/
│   ├── consumer/
│   ├── qc/
│   ├── mentor/
│   ├── bank/
│   └── admin/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/
│
├── requirements.txt
├── manage.py
├── build.sh
├── .env.example
├── .env.pythonanywhere.example
├── .gitignore
└── README.md
```

Folder aplikasi dapat disesuaikan ketika pengembangan dimulai.

---

## 11. Cara Menjalankan Proyek di Komputer

### Persyaratan

- Python versi yang didukung Django.
- Git.
- Visual Studio Code.
- Koneksi internet.

### Langkah 1 — Clone repository

```bash
git clone https://github.com/USERNAME/nusatani.git
cd nusatani
```

Ganti `USERNAME` dengan nama akun GitHub pemilik repository.

### Langkah 2 — Buat virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux atau macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Langkah 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Langkah 4 — Siapkan konfigurasi environment

Buat file `.env` berdasarkan `.env.example`.

Contoh isi `.env.example`:

```env
SECRET_KEY=isi_dengan_secret_key_lokal
DEBUG=True
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
ALLOWED_HOSTS=127.0.0.1,localhost
```

Jangan memasukkan password database atau secret key asli ke GitHub.

### Langkah 5 — Migrasi database

```bash
python manage.py makemigrations
python manage.py migrate
```

### Langkah 6 — Buat akun administrator

```bash
python manage.py createsuperuser
```

Ikuti instruksi untuk mengisi username, email, dan password.

### Langkah 7 — Jalankan aplikasi

```bash
python manage.py runserver
```

Buka:

```text
http://127.0.0.1:8000/
```

---

## 12. Persiapan Database Supabase

Supabase digunakan sebagai penyedia PostgreSQL.

1. Buka https://supabase.com/
2. Buat akun dan masuk ke dashboard.
3. Buat proyek baru dengan nama `nusatani`.
4. Buka pengaturan database dan cari informasi koneksi PostgreSQL.
5. Salin connection string yang sesuai.
6. Masukkan connection string ke environment variable:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
```

Sesuaikan dengan informasi koneksi asli dari Supabase.

Jika koneksi langsung tidak cocok dengan lingkungan hosting, periksa opsi connection pooling pada dokumentasi Supabase.

**Penting:** Jangan membagikan connection string, password, atau kredensial database kepada orang lain.

---

## 13. Persiapan GitHub

GitHub digunakan untuk menyimpan source code dan menghubungkannya dengan Render.

1. Buka https://github.com/
2. Buat akun jika belum memiliki akun.
3. Buat repository baru bernama `nusatani`.
4. Pastikan file `.gitignore` tersedia.

Contoh `.gitignore`:

```gitignore
venv/
__pycache__/
*.pyc
.env
db.sqlite3
staticfiles/
media/
.DS_Store
```

Kirim kode ke GitHub:

```bash
git init
git add .
git commit -m "Initial NusaTani project"
git branch -M main
git remote add origin https://github.com/USERNAME/nusatani.git
git push -u origin main
```

Ganti URL repository sesuai repository yang sudah dibuat.

Setiap perubahan berikutnya dapat dikirim dengan:

```bash
git add .
git commit -m "Update NusaTani"
git push
```

---

## 14. Deployment Website Menggunakan Render

Render digunakan untuk membuat aplikasi Django dapat diakses melalui internet.

Alamat: https://render.com/

### Langkah 1 — Buat akun Render

1. Buka website Render.
2. Pilih Sign Up.
3. Daftar atau masuk menggunakan GitHub.
4. Berikan izin akses repository yang akan digunakan.

### Langkah 2 — Buat Web Service

1. Buka Render Dashboard.
2. Klik **New**.
3. Pilih **Web Service**.
4. Hubungkan repository GitHub `nusatani`.
5. Pilih branch `main`.

### Langkah 3 — Isi konfigurasi

| Pengaturan | Nilai |
|---|---|
| Name | nusatani |
| Language | Python 3 |
| Branch | main |
| Root Directory | Kosong jika proyek berada di root repository |
| Build Command | `bash build.sh` |
| Start Command | `gunicorn config.wsgi:application` |
| Instance Type | Free |

Nama `config` pada Start Command harus sama dengan nama folder proyek Django yang berisi `wsgi.py`.

### Langkah 4 — Tambahkan Environment Variables

Pada bagian Environment di Render, masukkan:

| Key | Value |
|---|---|
| `SECRET_KEY` | Secret key Django yang aman |
| `DEBUG` | `False` |
| `DATABASE_URL` | Connection string PostgreSQL Supabase |
| `ALLOWED_HOSTS` | Host Render aplikasi |
| `CSRF_TRUSTED_ORIGINS` | URL HTTPS Render aplikasi |

Contoh format URL:

```text
https://nama-aplikasi.onrender.com
```

Jangan menggunakan contoh URL tersebut sebagai alamat final sebelum Render memberikan alamat aplikasi.

### Langkah 5 — Deploy

1. Periksa kembali konfigurasi.
2. Klik **Create Web Service**.
3. Tunggu proses instalasi dan deployment.
4. Periksa bagian Logs jika deployment gagal.
5. Jika berhasil, Render akan memberikan alamat website.

### Langkah 6 — Buat akun administrator

Setelah aplikasi berhasil berjalan, buat akun administrator menggunakan perintah:

```bash
python manage.py createsuperuser
```

Jalankan melalui fasilitas Shell jika tersedia pada layanan yang digunakan. Jika tidak tersedia, jalankan perintah dari komputer lokal yang sudah terhubung ke database Supabase.

### Alternatif tanpa kartu: PythonAnywhere

Jika Render tetap meminta kartu pada paket Free, **PythonAnywhere Beginner** dapat dipakai untuk MVP ini tanpa kartu. Perbedaannya, aplikasi dijalankan lewat WSGI (bukan gunicorn) dan memakai SQLite karena akun gratis baru tidak menyediakan PostgreSQL.

1. Buat akun Beginner di https://www.pythonanywhere.com/registration/register/beginner/
2. Di Bash console PythonAnywhere, jalankan:

   ```bash
   git clone https://github.com/aksara26/Nusatani.git
   cd Nusatani
   python3.12 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   ```

3. Salin `.env.pythonanywhere.example` menjadi `.env`, lalu ganti `<username>` dengan username PythonAnywhere Anda. `SECURE_SSL_REDIRECT` dibiarkan `False` karena HTTPS diurus PythonAnywhere.
4. Di tab **Web**, pilih **Add a new web app → Manual configuration → Python 3.12** (3.13 juga didukung).
5. Isi **Source code** dan **Working directory** dengan `/home/<username>/Nusatani`, serta **Virtualenv** dengan `/home/<username>/Nusatani/.venv`.
6. Salin isi `deploy/pythonanywhere_wsgi.py` ke `/var/www/<username>_pythonanywhere_com_wsgi.py`, lalu ganti `<username>` pada variabel `path`.
7. Tambahkan mapping **Static files**: URL `/static/` → `/home/<username>/Nusatani/staticfiles` dan URL `/media/` → `/home/<username>/Nusatani/media`.
8. Aktifkan **Force HTTPS**, lalu klik **Reload**.
9. Verifikasi `https://<username>.pythonanywhere.com/health/` menampilkan `{"status":"ok","database":"ok"}`, lalu uji login sesuai Skenario 1–3.

Catatan: `build.sh` tidak dipakai pada jalur PythonAnywhere. Web app gratis kedaluwarsa setelah sekitar satu bulan; perpanjang melalui tombol **Run until ...** di tab Web.

---

## 15. File Konfigurasi Deployment

### A. requirements.txt

Contoh dependencies awal:

```text
Django
djangorestframework
gunicorn
whitenoise
dj-database-url
psycopg[binary]
python-dotenv
```

Untuk hasil deployment yang konsisten, gunakan versi paket yang sudah diuji dan simpan versi tersebut di `requirements.txt`.

### B. build.sh

Buat file `build.sh` di folder utama proyek:

```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

File ini akan dijalankan saat proses build Render.

### C. Konfigurasi Django

Pada `settings.py`, sesuaikan konfigurasi produksi dengan environment variable.

Contoh dasar:

```python
import os
import dj_database_url

SECRET_KEY = os.environ.get("SECRET_KEY", "development-only-key")

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS", "localhost,127.0.0.1"
).split(",")

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL)
    }

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # Middleware Django lainnya
]

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
```

Pastikan middleware bawaan Django lainnya tetap ada dan urutannya sesuai dokumentasi Django.

Tambahkan konfigurasi CSRF terpercaya untuk domain HTTPS Render:

```python
CSRF_TRUSTED_ORIGINS = os.environ.get(
    "CSRF_TRUSTED_ORIGINS", ""
).split(",")
```

Untuk produksi, pastikan aplikasi menggunakan secret key yang kuat, HTTPS, dan pengaturan cookie yang aman.

---

## 16. Pengelolaan Foto dan File

Render Free menggunakan penyimpanan filesystem sementara untuk aplikasi web.

Karena itu:

- Jangan menyimpan foto produk permanen hanya di filesystem aplikasi Render.
- Untuk demo sederhana, gambar contoh dapat dimasukkan ke folder static dalam repository.
- Untuk upload foto pengguna, gunakan penyimpanan objek seperti Supabase Storage setelah kuota dan konfigurasi aksesnya diperiksa.
- Simpan alamat file atau URL gambar pada database, bukan file gambar besar langsung di database.

---

## 17. Skenario Pengujian

| No. | Skenario | Hasil yang Diharapkan |
|---|---|---|
| 1 | Petani login | Dashboard petani terbuka |
| 2 | HOREKA login | Dashboard HOREKA terbuka |
| 3 | Konsumen login | Dashboard konsumen terbuka |
| 4 | Petani menambah produk | Produk muncul di katalog |
| 5 | HOREKA membuat pesanan | Pesanan tercatat |
| 6 | Konsumen membeli produk surplus | Pesanan tercatat |
| 7 | Petani mengirim produk ke QC | Status berubah menjadi menunggu QC |
| 8 | QC menyetujui produk | Status menjadi QC lolos |
| 9 | QC menolak produk | Produk tidak dapat dikirim |
| 10 | Pesanan dikirim | Status pengiriman diperbarui |
| 11 | Pesanan selesai | Riwayat pesanan diperbarui |
| 12 | Admin membuka dashboard | Data platform dapat dipantau |

---

## 18. Batasan MVP

Versi MVP NusaTani difokuskan untuk demonstrasi alur bisnis dan pengujian pengguna.

Fitur yang masih berupa simulasi:

- Pembayaran dan pencatatan DP.
- Pengembalian dana.
- Pencairan dana kepada petani.
- Integrasi kurir dan pelacakan langsung.
- Penilaian kelayakan pembiayaan.
- Skema pembiayaan aset.

MVP tidak berfungsi sebagai penyedia layanan pembayaran, penyimpan dana, atau pemberi pinjaman.

Sebelum digunakan dalam operasional bisnis sungguhan, diperlukan peninjauan keamanan, aturan transaksi, ketentuan pembiayaan, perlindungan data, dan integrasi penyedia layanan yang sesuai.

---

## 19. Catatan Penting Deployment Gratis

1. Render Free dapat menidurkan aplikasi setelah tidak aktif. Pengunjung pertama setelah periode tidur mungkin perlu menunggu aplikasi aktif kembali.
2. Penyimpanan lokal Render tidak cocok untuk menyimpan file upload permanen.
3. Supabase Free memiliki batas kapasitas database dan dapat menjeda proyek yang tidak aktif.
4. Paket gratis tidak memberikan jaminan uptime seperti layanan produksi berbayar.
5. Jangan memasukkan data pribadi atau data keuangan sensitif pengguna sungguhan ke sistem demo.
6. Pantau kuota layanan agar tidak terkena biaya di luar perkiraan.

---

## 20. Referensi Dokumentasi

- Django: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Bootstrap: https://getbootstrap.com/docs/
- GitHub Docs: https://docs.github.com/
- Render Django Deployment: https://render.com/docs/deploy-django
- Render Free Services: https://render.com/docs/free
- Supabase Documentation: https://supabase.com/docs
- Supabase Pricing: https://supabase.com/pricing

---

## 21. Identitas Proyek

**Nama:** NusaTani  
**Kategori:** Agritech / Digital Marketplace  
**Fokus:** Microgreens dan pemberdayaan petani  
**Target pengguna:** Petani, HOREKA, konsumen rumah tangga, QC, mentor, dan mitra pembiayaan.  
**Jenis aplikasi:** Web Application  
**Tahap:** Minimum Viable Product (MVP)

---

## 🌱 NusaTani

*Menghubungkan petani, memperluas pasar, dan membangun ekosistem microgreens yang lebih terintegrasi.*
