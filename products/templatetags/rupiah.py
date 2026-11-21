"""Template filter untuk format mata uang Rupiah sesuai format data design-spec."""

from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def rupiah(value, satuan=None):
    """Format angka menjadi 'Rp 22.000' atau 'Rp 22.000 / pack'.

    Args:
        value: harga (Decimal/int/float/str).
        satuan: opsional, mis. "pack" -> ditambahkan " / pack".

    Cocok untuk harga per pack yang umumnya bilangan bulat. Jika nilai
    mengandung centuan, desimal dua digit akan ditampilkan.
    """
    if value is None or value == "":
        base = "Rp 0"
    else:
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return "Rp 0"

        formatted = format(abs(amount), ",.2f").replace(",", "X").replace(".", ",").replace("X", ".")
        if amount < 0:
            formatted = f"-{formatted}"
        # Hilangkan ,00 kalau bilangan bulat agar output 'Rp 22.000' seperti spec.
        if formatted.endswith(",00"):
            formatted = formatted[:-3]
        base = f"Rp {formatted}"

    if satuan:
        return f"{base} / {satuan}"
    return base


@register.filter
def satuan_harga(verbose_name):
    """Ambil satuan harga dari verbose_name field, mis. 'Harga per pack' -> '/ pack'.

    Jika verbose_name tidak mengandung kata 'per ', kembalikan string kosong
    sehingga pemanggil bisa menampilkan TODO.
    """
    verbose = str(verbose_name or "")
    if "per " in verbose:
        return f"/ {verbose.split('per ', 1)[1]}"
    return ""
