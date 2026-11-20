"""Template filter ikon SVG untuk dasbor (mengganti emoji) sesuai design-spec.

Semua ikon inline SVG, viewBox 0 0 24 24, stroke 1.75px, tanpa emoji.
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Ikon untuk statistik / aksi cepat / fokus (dikunci dari emoji yang dikirim views).
_ICON = {
    "\U0001F331": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/></svg>',              # 🌱 sprout
    "\U0001F4E6": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 8v13a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8z"/><polyline points="10 2 15 8 10 14"/><line x1="18" y1="6" x2="8" y2="6"/></svg>',  # 📦 package
    "\U0001F50D": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',  # 🔍 search
    "\U0001F9F0": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.17 12.63A6 6 0 0 0 21 10c0-2.16-1.29-4.11-3.17-5.19C17.3 3.17 14.46 2 12 2S6.7 3.17 5.17 4.81C3.29 5.89 2 7.84 2 10c0 2.16 1.29 4.11 3.17 5.19C6.7 16.83 9.54 18 12 18s5.3-1.17 6.83-2.81c1.88-1.08 3.17-3.03 3.17-5.19 0-1.16-.45-2.24-1.2-3.18Z"/><path d="M9 10h.01M15 10h.01M12 14v.01M12 6v.01"/></svg>',  # 🧰 tools
    "\U0001F4C6": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',  # 🗓️ calendar
    "\U00002672": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M1 12h5l4 4 4-4h5"/></svg>',                         # ♻️ recycle (simplified)
    "\U00002705": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>',                  # ✅ check
    "\U0001F4B3": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="6" width="20" height="12" rx="2" ry="2"/><line x1="12" y1="3" x2="12" y2="9"/><line x1="6" y1="21" x2="6" y2="15"/><line x1="18" y1="21" x2="18" y2="15"/></svg>',  # 💳 card
    "\u231B": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 3v6h4V3M14 21v-6h-4v6"/></svg>',                    # ⏳ hourglass
    "\U0001F6AB": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12a7 7 0 1 0 14 0 7 7 0 0 0-14 0Z"/><line x1="12" y1="8" x2="12" y2="16"/></svg>',     # ⛔ stop
    "\U0001F33E": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12h3l2 4 2-4 3 4 2-4h3"/></svg>',                # 🌾 grain
    "\U0001F4CA": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="12" y1="20" x2="12" y2="4"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="4"/></svg>',  # 📊 bar-chart
    "\U0001F4C8": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 12h-4l-3 3L7 18l1-3 3 2 2-4M2 22l6-6"/></svg>',   # 📈 line-chart
    "\U0001F465": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',     # 👥 users
    "\uff0b": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',              # ＋ fullwidth plus
    "\U0001F4E5": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 3h18"/><path d="M19 9v10c0 1.1-.9 2-2 2H7c-1.1 0-2-.9-2-2V9z"/><path d="M9 12H3l9-9"/></svg>',    # 📥 inbox
    "\U0001F6D2": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="8" cy="8" r="7"/><path d="M21 12a9 9 0 0 1-9 9 9 9 0 0 1-9-9"/></svg>',   # 🛒 cart
    "\U0001F69A": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 17V13c0-1.1-.9-2-2-2h-3c-.6 0-1.1-.3-1.4-.8L13 8.2V5c0-.6-.4-1-1-1H6c-.6 0-1 .4-1 1v3.2L3.4 11.2C3.1 11.7 3 12.2 3 12.8v4.2c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-4z"/><path d="M17 17h3M11 17h3"/></svg>',                            # 🚚 truck
    "\u2699": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1h-1.24A2 2 0 0 1 3 16.76V13c0-1.11.89-2 2-2h1.24a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33 1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09A1.65 1.65 0 0 0 15 4.6a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1h1.24A2 2 0 0 1 21 13.24V17a2 2 0 0 1-2 2h-1.59a1.65 1.65 0 0 0-1-1.51Z"/></svg>',              # ⚙️ gear
}

# Ikon untuk chip status (sesuai design-spec: teks + ikon).
_CHIP_ICON = {
    "menunggu": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    "qc": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="1"/><path d="M12 8v.01M12 16v.01M8 12h.01M16 12h.01M9.5 5h5M9.5 19h5"/></svg>',
    "produksi": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M13 2V6h6M13 8V6M13 12V6M13 16V6M13 20V6"/><rect x="2" y="6" width="10" height="14" rx="2" ry="2"/></svg>',
    "siap": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 7h.01M7 12h.01M7 17h.01M12 7h.01M12 12h.01M12 17h.01M17 7h.01M17 12h.01M17 17h.01"/></svg>',
    "dikirim": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="17 12 19 15 13 18"/><path d="M18.4 1.8a4 4 0 0 0-4.8 0l-4.2 4.2a4 4 0 0 0 0 4.8l3.6 3.6a4 4 0 0 0 4.8 0l4.2-4.2a4 4 0 0 0 0-4.8z"/></svg>',
    "selesai": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="22 12 14 20 10 14"/><circle cx="12" cy="12" r="10"/></svg>',
    "dibatalkan": '<svg class="nt-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/></svg>',
}

_CHIP_VARIAN = {
    "Menunggu Konfirmasi": "menunggu",
    "Menunggu QC": "qc",
    "Dalam Produksi": "produksi",
    "Siap Dikirim": "siap",
    "Dalam Pengiriman": "dikirim",
    "Selesai": "selesai",
    "Dibatalkan": "dibatalkan",
    "QC Lolos": "selesai",
    "QC Ditolak": "dibatalkan",
    "Menunggu": "menunggu",
    "Diperiksa": "qc",
    "Lolos": "selesai",
    "Ditolak": "dibatalkan",
    "Dijadwalkan": "menunggu",
    "Potensial": "selesai",
    "Pendampingan": "menunggu",
    "Belum": "dibatalkan",
}


@register.filter
def nt_icon(emoji):
    """Kembalikan inline SVG untuk emoji yang diberikan; kosong jika tidak diketahui."""
    return mark_safe(_ICON.get(emoji, ""))


@register.filter
def nt_chip(badge):
    """Kembalikan HTML lengkap chip status (variant + ikon + teks), aman di-render."""
    variant = _CHIP_VARIAN.get(badge, "menunggu")
    icon = _CHIP_ICON.get(variant, _CHIP_ICON["menunggu"])
    html = (
        '<span class="chip chip--%s">%s<span class="chip-text">%s</span></span>'
        % (variant, icon, badge)
    )
    return mark_safe(html)
