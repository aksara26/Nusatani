"""Definisi peran dan konten dashboard minimal untuk masing-masing peran.

Satu template dashboard dipakai untuk semua peran agar perubahan tampilan
cukup dilakukan di satu tempat. Konten per role diambil dari konfigurasi ini.
"""

from django.db import models


class Role(models.TextChoices):
    FARMER = "farmer", "Petani"
    HORECA = "horeca", "HOREKA"
    CONSUMER = "consumer", "Konsumen Rumah Tangga"
    QC = "qc", "Petugas Quality Control"
    MENTOR = "mentor", "Mentor"
    BANK = "bank", "Bank / Mitra Pembiayaan"
    ADMIN = "admin", "Administrator"


ROLE_DASHBOARDS = {
    Role.FARMER.value: {
        "label": "Dashboard Petani",
        "subtitle": "Pusat kendali usaha microgreens Anda.",
        "description": (
            "Pantau pesanan, kelola stok dan produk surplus, ajukan produk ke pemeriksaan "
            "kualitas, serta catat aset usaha dari satu tempat."
        ),
        "focus_areas": [
            {
                "title": "Pesanan & stok",
                "body": "Pesanan masuk dan ketersediaan produk menjadi dasar persiapan produksi.",
            },
            {
                "title": "Kualitas produk",
                "body": "Produk perlu lolos Quality Control sebelum masuk ke proses pengiriman.",
            },
            {
                "title": "Aset usaha",
                "body": "Rak, tray, lampu, dan peralatan panen tercatat untuk evaluasi usaha.",
            },
        ],
    },
    Role.HORECA.value: {
        "label": "Dashboard HOREKA",
        "subtitle": "Pemesanan terjadwal untuk hotel, restoran, dan kafe.",
        "description": (
            "Lihat katalog microgreens, kirim pre-order sesuai jadwal kebutuhan, dan pantau "
            "status pesanan hingga produk diterima."
        ),
        "focus_areas": [
            {
                "title": "Pre-order",
                "body": "Perkiraan waktu pemesanan adalah 7–14 hari sebelum produk dibutuhkan.",
            },
            {
                "title": "Status pesanan",
                "body": "Setiap tahap pesanan dapat dipantau hingga status Selesai.",
            },
            {
                "title": "Riwayat pembelian",
                "body": "Catatan pesanan sebelumnya membantu perencanaan kebutuhan berikutnya.",
            },
        ],
    },
    Role.CONSUMER.value: {
        "label": "Dashboard Konsumen",
        "subtitle": "Microgreens segar langsung dari petani.",
        "description": (
            "Jelajahi produk yang tersedia dan produk surplus petani, lakukan pemesanan, "
            "lalu pantau status sampai pesanan diterima."
        ),
        "focus_areas": [
            {
                "title": "Produk tersedia",
                "body": "Pilih produk sesuai stok yang tercatat di marketplace.",
            },
            {
                "title": "Produk surplus",
                "body": "Produk surplus petani ditawarkan dengan harga dan ketersediaan yang jelas.",
            },
            {
                "title": "Riwayat pesanan",
                "body": "Lihat kembali pesanan yang sudah Anda lakukan.",
            },
        ],
    },
    Role.QC.value: {
        "label": "Dashboard Quality Control",
        "subtitle": "Menjaga standar kualitas setiap produk yang dikirim.",
        "description": (
            "Periksa produk yang diajukan petani, isi hasil pemeriksaan, berikan catatan "
            "perbaikan, dan tentukan hasil lolos atau tidak lolos QC."
        ),
        "focus_areas": [
            {
                "title": "Antrean pemeriksaan",
                "body": "Produk berstatus menunggu pemeriksaan menjadi prioritas petugas QC.",
            },
            {
                "title": "Aspek yang dinilai",
                "body": "Kondisi visual, kebersihan, kesegaran, dan kesesuaian berat.",
            },
            {
                "title": "Aturan pengiriman",
                "body": "Produk yang tidak lolos QC tidak boleh masuk ke proses pengiriman.",
            },
        ],
    },
    Role.MENTOR.value: {
        "label": "Dashboard Mentor",
        "subtitle": "Pendampingan pertumbuhan petani.",
        "description": (
            "Pantau perkembangan petani, berikan materi edukasi, dan catat hasil "
            "pendampingan agar progres usaha dapat dievaluasi."
        ),
        "focus_areas": [
            {
                "title": "Perkembangan petani",
                "body": "Pantau aktivitas usaha dan capaian petani yang dibimbing.",
            },
            {
                "title": "Materi edukasi",
                "body": "Bagikan materi yang relevan dengan kebutuhan budidaya microgreens.",
            },
            {
                "title": "Catatan pendampingan",
                "body": "Simpan evaluasi dan riwayat kegiatan pendampingan.",
            },
        ],
    },
    Role.BANK.value: {
        "label": "Dashboard BANKKU",
        "subtitle": "Gambaran performa usaha untuk mitra pembiayaan.",
        "description": (
            "Lihat data pesanan, transaksi, aset, dan indikator performa petani sesuai "
            "hak akses yang diberikan."
        ),
        "focus_areas": [
            {
                "title": "Performa usaha",
                "body": "Jumlah pesanan, nilai pesanan, dan konsistensi pemenuhan pesanan.",
            },
            {
                "title": "Data pendukung",
                "body": "Riwayat transaksi, catatan kualitas, dan data aset petani.",
            },
            {
                "title": "Indikator pembiayaan",
                "body": "Nilai indikator pada MVP adalah simulasi, bukan keputusan kredit.",
            },
        ],
    },
    Role.ADMIN.value: {
        "label": "Dashboard Administrator",
        "subtitle": "Pengelolaan seluruh aktivitas platform.",
        "description": (
            "Kelola akun dan peran pengguna, katalog produk, data QC dan mentor, serta "
            "pantau laporan aktivitas NusaTani."
        ),
        "focus_areas": [
            {
                "title": "Akun & hak akses",
                "body": "Tetapkan peran pengguna sesuai tanggung jawab masing-masing.",
            },
            {
                "title": "Katalog & pesanan",
                "body": "Pastikan data produk, varietas, dan pesanan tetap konsisten.",
            },
            {
                "title": "Laporan aktivitas",
                "body": "Pantau ringkasan aktivitas platform dari satu dashboard.",
            },
        ],
    },
}


# Peran yang boleh mendaftar mandiri. Peran operasional/internal diberikan
# oleh administrator agar hak akses tetap terkendali.
SELF_REGISTER_ROLES = (
    Role.FARMER.value,
    Role.HORECA.value,
    Role.CONSUMER.value,
)


ROLE_GUIDES = {
    Role.FARMER.value: {
        "icon": "🌾",
        "label": Role.FARMER.label,
        "demo_username": "petani1",
        "is_amber": False,
        "summary": "Kelola produksi, stok, pesanan, kualitas, pengiriman, dan catatan usaha.",
        "steps": [
            "Buka <strong>Produk Saya</strong> untuk menambah produk dan memperbarui stok.",
            "Di <strong>Pesanan Masuk</strong>, konfirmasi pesanan lalu mulai produksi.",
            "Ajukan produk ke QC. Setelah <strong>Lolos QC</strong>, siapkan pengiriman lalu tandai selesai.",
            "Catat rak, tray, dan alat di <strong>Asetku</strong>; lihat jadwal di <strong>Mentorku</strong>.",
            "Pantau hasil usaha di <strong>Performaku</strong>.",
        ],
    },
    Role.HORECA.value: {
        "icon": "🍽️",
        "label": Role.HORECA.label,
        "demo_username": "horeca1",
        "is_amber": True,
        "summary": "Pesan microgreens terjadwal untuk hotel, restoran, dan kafe.",
        "steps": [
            "Buka <strong>Katalog</strong> lalu pilih produk yang dibutuhkan.",
            "Buat <strong>pre-order</strong> 7–14 hari sebelum tanggal kebutuhan.",
            "Pantau status pesanan sampai produk dikirim dan diterima.",
            "Lihat kembali pesanan melalui menu <strong>Pesanan Saya</strong>.",
        ],
    },
    Role.CONSUMER.value: {
        "icon": "🥗",
        "label": Role.CONSUMER.label,
        "demo_username": "konsumen1",
        "is_amber": True,
        "summary": "Beli microgreens segar, termasuk produk surplus petani.",
        "steps": [
            "Buka <strong>Katalog</strong> atau <strong>Sisaku</strong> untuk melihat produk.",
            "Pilih produk surplus yang masih tersedia lalu pesan.",
            "Pantau status pesanan dan pengiriman simulasi.",
            "Riwayat pembelian ada di menu <strong>Pesanan Saya</strong>.",
        ],
    },
    Role.QC.value: {
        "icon": "🔍",
        "label": Role.QC.label,
        "demo_username": "qc1",
        "is_amber": False,
        "summary": "Periksa kualitas produk sebelum pesanan boleh dikirim.",
        "steps": [
            "Buka <strong>Antrean QC</strong> untuk melihat produk yang diajukan petani.",
            "Periksa visual, kebersihan, kesegaran, dan kesesuaian berat.",
            "Tulis catatan perbaikan bila perlu, lalu pilih <strong>Lolos QC</strong> atau <strong>Tidak lolos QC</strong>.",
            "Produk yang ditolak tidak dapat masuk proses pengiriman.",
        ],
    },
    Role.MENTOR.value: {
        "icon": "🧑‍🏫",
        "label": Role.MENTOR.label,
        "demo_username": "mentor1",
        "is_amber": False,
        "summary": "Berikan materi, jadwal, dan evaluasi pendampingan petani.",
        "steps": [
            "Buka <strong>Mentorku</strong> lalu pilih <strong>Tambah pendampingan</strong>.",
            "Isi materi, detail, jadwal, dan petani yang dibimbing.",
            "Ubah status menjadi <strong>Selesai</strong> setelah pendampingan berlangsung.",
            "Catat kegiatan dan evaluasi agar riwayatnya tersimpan.",
        ],
    },
    Role.BANK.value: {
        "icon": "🏦",
        "label": Role.BANK.label,
        "demo_username": "bank1",
        "is_amber": False,
        "summary": "Pantau performa usaha dan indikator pembiayaan simulasi.",
        "steps": [
            "Buka <strong>BANKKU</strong> untuk melihat ringkasan seluruh petani.",
            "Pilih petani untuk melihat detail performa dan riwayat pesanan.",
            "Perhatikan komposisi skor: pemenuhan, kualitas, aset, pendampingan, dan pembayaran simulasi.",
            "Ingat: indikator ini bukan keputusan kredit resmi.",
        ],
    },
    Role.ADMIN.value: {
        "icon": "⚙️",
        "label": Role.ADMIN.label,
        "demo_username": "admin",
        "is_amber": False,
        "summary": "Kelola akun, katalog, pesanan, QC, mentor, dan laporan platform.",
        "steps": [
            "Gunakan akun ini untuk mengelola peran dan hak akses pengguna.",
            "Pastikan varietas dan produk di katalog tetap mutakhir.",
            "Pantau pesanan, antrean QC, pendampingan, dan BANKKU dari satu tempat.",
            "Akses admin juga tersedia di halaman <code>/admin/</code>.",
        ],
    },
}
