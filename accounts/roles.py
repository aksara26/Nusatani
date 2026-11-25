"""Definisi peran dan konten dashboard minimal untuk masing-masing peran.

Satu template dashboard dipakai untuk semua peran agar perubahan tampilan
cukup dilakukan di satu tempat. Konten per role diambil dari konfigurasi ini.
"""

from django.db import models
from django.urls import reverse_lazy
from django.utils.functional import lazy
from django.utils.html import format_html


def _guide_html(template, *args):
    return lazy(lambda: format_html(template, *args), str)()


def _guide_link(route_name, label):
    return _guide_html(
        '<strong><a href="{}">{}</a></strong>',
        reverse_lazy(route_name),
        label,
    )


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
                "url": reverse_lazy("products:my_products"),
                "icon": "package",
            },
            {
                "title": "Kualitas produk",
                "body": "Produk perlu lolos Quality Control sebelum masuk ke proses pengiriman.",
                "url": reverse_lazy("orders:incoming"),
                "icon": "clipboard-check",
            },
            {
                "title": "Aset usaha",
                "body": "Rak, tray, lampu, dan peralatan panen tercatat untuk evaluasi usaha.",
                "url": reverse_lazy("assets:list"),
                "icon": "archive",
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
                "url": reverse_lazy("orders:preorder_create"),
                "icon": "calendar",
            },
            {
                "title": "Status pesanan",
                "body": "Setiap tahap pesanan dapat dipantau hingga status Selesai.",
                "url": reverse_lazy("orders:my_orders"),
                "icon": "package",
            },
            {
                "title": "Riwayat pembelian",
                "body": "Catatan pesanan sebelumnya membantu perencanaan kebutuhan berikutnya.",
                "url": reverse_lazy("orders:my_orders"),
                "icon": "book",
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
                "url": reverse_lazy("products:catalog"),
                "icon": "layout-dashboard",
            },
            {
                "title": "Produk surplus",
                "body": "Produk surplus petani ditawarkan dengan harga dan ketersediaan yang jelas.",
                "url": reverse_lazy("products:surplus"),
                "icon": "sprout",
            },
            {
                "title": "Riwayat pesanan",
                "body": "Lihat kembali pesanan yang sudah Anda lakukan.",
                "url": reverse_lazy("orders:my_orders"),
                "icon": "book",
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
                "url": reverse_lazy("quality_control:queue"),
                "icon": "clipboard-check",
            },
            {
                "title": "Aspek yang dinilai",
                "body": "Kondisi visual, kebersihan, kesegaran, dan kesesuaian berat.",
                "url": reverse_lazy("quality_control:queue"),
                "icon": "search",
            },
            {
                "title": "Aturan pengiriman",
                "body": "Produk yang tidak lolos QC tidak boleh masuk ke proses pengiriman.",
                "url": reverse_lazy("deliveries:list"),
                "icon": "truck",
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
                "url": reverse_lazy("mentorship:list"),
                "icon": "users",
            },
            {
                "title": "Materi edukasi",
                "body": "Bagikan materi yang relevan dengan kebutuhan budidaya microgreens.",
                "url": reverse_lazy("mentorship:create"),
                "icon": "book",
            },
            {
                "title": "Catatan pendampingan",
                "body": "Simpan evaluasi dan riwayat kegiatan pendampingan.",
                "url": reverse_lazy("mentorship:list"),
                "icon": "file-text",
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
                "url": reverse_lazy("bankku:dashboard"),
                "icon": "bar-chart",
            },
            {
                "title": "Data pendukung",
                "body": "Riwayat transaksi, catatan kualitas, dan data aset petani.",
                "url": reverse_lazy("bankku:dashboard"),
                "icon": "book",
            },
            {
                "title": "Indikator pembiayaan",
                "body": "Nilai indikator pada MVP adalah simulasi, bukan keputusan kredit.",
                "url": reverse_lazy("bankku:dashboard"),
                "icon": "badge-check",
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
                "url": reverse_lazy("admin:index"),
                "icon": "settings",
            },
            {
                "title": "Katalog & pesanan",
                "body": "Pastikan data produk, varietas, dan pesanan tetap konsisten.",
                "url": reverse_lazy("products:catalog"),
                "icon": "layout-dashboard",
            },
            {
                "title": "Laporan aktivitas",
                "body": "Pantau ringkasan aktivitas platform dari satu dashboard.",
                "url": reverse_lazy("bankku:dashboard"),
                "icon": "bar-chart",
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


# Akun demo yang boleh dipakai untuk masuk cepat dari halaman login.
# Administrator sengaja tidak dimasukkan agar tidak tampil sebagai tombol demo.
DEMO_ROLE_ACCOUNTS = {
    Role.FARMER.value: {
        "role": Role.FARMER.value,
        "username": "petani1",
        "label": "Petani",
        "icon": "sprout",
        "input_label": "Username / ID Petani",
        "placeholder": "contoh: petani1",
        "hint": "Kelola produk, pesanan, kualitas, dan aset usaha.",
    },
    Role.HORECA.value: {
        "role": Role.HORECA.value,
        "username": "horeca1",
        "label": "HOREKA",
        "icon": "utensils",
        "input_label": "Username / Email usaha",
        "placeholder": "contoh: horeca1",
        "hint": "Pre-order terjadwal untuk hotel, restoran, dan kafe.",
    },
    Role.CONSUMER.value: {
        "role": Role.CONSUMER.value,
        "username": "konsumen1",
        "label": "Konsumen",
        "icon": "shopping-bag",
        "input_label": "Username / Email",
        "placeholder": "contoh: konsumen1",
        "hint": "Belanja microgreens segar untuk rumah tangga.",
    },
    Role.QC.value: {
        "role": Role.QC.value,
        "username": "qc1",
        "label": "QC",
        "icon": "clipboard-check",
        "input_label": "ID Petugas QC",
        "placeholder": "contoh: qc1",
        "hint": "Periksa dan putuskan kelayakan produk sebelum dikirim.",
    },
    Role.MENTOR.value: {
        "role": Role.MENTOR.value,
        "username": "mentor1",
        "label": "Mentor",
        "icon": "graduation-cap",
        "input_label": "Username Mentor",
        "placeholder": "contoh: mentor1",
        "hint": "Jadwalkan dan catat pendampingan petani.",
    },
    Role.BANK.value: {
        "role": Role.BANK.value,
        "username": "bank1",
        "label": "Bank",
        "icon": "landmark",
        "input_label": "Username / Email mitra",
        "placeholder": "contoh: bank1",
        "hint": "Pantau performa usaha dan indikator pembiayaan.",
    },
}


ROLE_GUIDES = {
    Role.FARMER.value: {
        "icon": "sprout",
        "label": Role.FARMER.label,
        "demo_username": "petani1",
        "is_amber": False,
        "summary": "Kelola produksi, stok, pesanan, kualitas, pengiriman, dan catatan usaha.",
        "steps": [
            _guide_html(
                "Buka {} untuk menambah produk dan memperbarui stok.",
                _guide_link("products:my_products", "Produk Saya"),
            ),
            _guide_html(
                "Di {}, konfirmasi pesanan lalu mulai produksi.",
                _guide_link("orders:incoming", "Pesanan Masuk"),
            ),
            "Ajukan produk ke QC. Setelah <strong>Lolos QC</strong>, siapkan pengiriman lalu tandai selesai.",
            _guide_html(
                "Catat rak, tray, dan alat di {}; lihat jadwal di {}.",
                _guide_link("assets:list", "Asetku"),
                _guide_link("mentorship:list", "Mentorku"),
            ),
            _guide_html(
                "Pantau hasil usaha di {}.",
                _guide_link("bankku:my_performance", "Performaku"),
            ),
        ],
    },
    Role.HORECA.value: {
        "icon": "utensils",
        "label": Role.HORECA.label,
        "demo_username": "horeca1",
        "is_amber": True,
        "summary": "Pesan microgreens terjadwal untuk hotel, restoran, dan kafe.",
        "steps": [
            _guide_html(
                "Buka {} lalu pilih produk yang dibutuhkan.",
                _guide_link("products:catalog", "Katalog"),
            ),
            _guide_html(
                "Buat {} 7–14 hari sebelum tanggal kebutuhan.",
                _guide_link("orders:preorder_create", "pre-order"),
            ),
            "Pantau status pesanan sampai produk dikirim dan diterima.",
            _guide_html(
                "Lihat kembali pesanan melalui menu {}.",
                _guide_link("orders:my_orders", "Pesanan Saya"),
            ),
        ],
    },
    Role.CONSUMER.value: {
        "icon": "shopping-bag",
        "label": Role.CONSUMER.label,
        "demo_username": "konsumen1",
        "is_amber": True,
        "summary": "Beli microgreens segar, termasuk produk surplus petani.",
        "steps": [
            _guide_html(
                "Buka {} atau {} untuk melihat produk.",
                _guide_link("products:catalog", "Katalog"),
                _guide_link("products:surplus", "Sisaku"),
            ),
            _guide_html(
                "Pilih {} yang masih tersedia lalu pesan.",
                _guide_link("products:surplus", "produk surplus"),
            ),
            "Pantau status pesanan dan pengiriman simulasi.",
            _guide_html(
                "Riwayat pembelian ada di menu {}.",
                _guide_link("orders:my_orders", "Pesanan Saya"),
            ),
        ],
    },
    Role.QC.value: {
        "icon": "clipboard-check",
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
        "icon": "graduation-cap",
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
        "icon": "landmark",
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
        "icon": "settings",
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
