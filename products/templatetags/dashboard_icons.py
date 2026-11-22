"""Filter chip status untuk seluruh halaman NusaTani.

Chip memakai sprite SVG yang didefinisikan di ``templates/base.html`` supaya
seluruh aplikasi memakai satu sistem ikon. Teks status selalu di-escape karena
nilainya berasal dari model dan dapat berubah.
"""

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

# Label status -> varian warna. Kunci memakai label tampilan persis seperti
# yang dikirim model (``get_status_display`` dan sejenisnya).
_CHIP_VARIAN = {
    # Pesanan
    "Menunggu Konfirmasi": "menunggu",
    "Dikonfirmasi": "produksi",
    "Dalam Produksi": "produksi",
    "Menunggu QC": "qc",
    "QC Lolos": "siap",
    "QC Ditolak": "dibatalkan",
    "Siap Dikirim": "siap",
    "Dalam Pengiriman": "dikirim",
    "Selesai": "selesai",
    "Dibatalkan": "dibatalkan",
    # Quality Control
    "Menunggu pemeriksaan": "qc",
    "Sedang diperiksa": "qc",
    "Lolos QC": "selesai",
    "Tidak lolos QC": "dibatalkan",
    "Menunggu": "qc",
    "Diperiksa": "qc",
    "Lolos": "selesai",
    "Ditolak": "dibatalkan",
    # Pengiriman
    "Disiapkan": "siap",
    "Dikirim": "dikirim",
    "Diterima": "selesai",
    # Pembayaran (simulasi)
    "Belum dibayar": "menunggu",
    "Menunggu konfirmasi": "menunggu",
    "DP tercatat": "menunggu",
    "Lunas": "selesai",
    "Pengembalian dana disimulasikan": "netral",
    # Kondisi aset
    "Baik": "selesai",
    "Cukup": "menunggu",
    "Perlu perbaikan": "dibatalkan",
    # Pendampingan
    "Dijadwalkan": "menunggu",
    # Indikator pembiayaan (simulasi)
    "Potensial (simulasi)": "selesai",
    "Perlu pendampingan": "menunggu",
    "Belum memenuhi ambang simulasi": "dibatalkan",
    # Ketersediaan produk
    "Tersedia": "selesai",
    "Akan tersedia": "qc",
    "Stok habis": "dibatalkan",
    "Nonaktif": "netral",
    # Produk surplus
    "Sisaku": "netral",
    # Skema pembiayaan aset
    "Tunai": "netral",
    "Ijarah": "info",
    "Kredit": "menunggu",
    # Status umum (timestamp/label)
    "Belum": "netral",
}

# Varian warna -> nama simbol pada sprite di base.html.
_CHIP_ICON = {
    "menunggu": "alert-circle",
    "qc": "clipboard-check",
    "produksi": "package",
    "siap": "check-circle",
    "dikirim": "truck",
    "selesai": "check-circle",
    "dibatalkan": "x",
    "netral": "info-circle",
}

_VARIAN_LOWER = {label.lower(): variant for label, variant in _CHIP_VARIAN.items()}


@register.filter
def nt_chip(badge):
    """Render chip status berisi varian warna, ikon sprite, dan teks aman."""
    text = str(badge or "").strip()
    variant = _CHIP_VARIAN.get(text) or _VARIAN_LOWER.get(text.lower(), "netral")
    icon = _CHIP_ICON.get(variant, _CHIP_ICON["netral"])
    return mark_safe(
        '<span class="chip chip--%s">'
        '<svg class="nt-icon" width="12" height="12" aria-hidden="true">'
        '<use href="#icon-%s"></use></svg>'
        '<span class="chip-text">%s</span></span>'
        % (variant, icon, escape(text))
    )
