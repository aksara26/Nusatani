"""Form pengajuan pesanan, perubahan status, dan pembayaran simulasi."""

from django import forms
from django.utils import timezone

from products.models import Product

from .models import (
    ALLOWED_TRANSITIONS,
    FARMER_MANAGEABLE_STATUSES,
    OrderStatus,
    PaymentRecord,
)


def _apply_bootstrap_styles(form):
    for field in form.fields.values():
        css_class = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
        field.widget.attrs.setdefault("class", css_class)


class OrderForm(forms.Form):
    """Form pesanan baru; aturan waktu berbeda untuk pre-order dan surplus."""

    product = forms.ModelChoiceField(
        queryset=Product.objects.none(), label="Produk", empty_label="— Pilih produk —"
    )
    quantity = forms.IntegerField(min_value=1, label="Jumlah")
    needed_by = forms.DateField(
        required=False,
        label="Dibutuhkan pada",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    notes = forms.CharField(
        required=False,
        label="Catatan untuk petani",
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, order_type="preorder", **kwargs):
        super().__init__(*args, **kwargs)
        self.order_type = order_type
        products = Product.objects.select_related("variety", "farmer").filter(is_active=True)
        if order_type == "surplus":
            products = products.filter(is_surplus=True, inventory__quantity__gt=0)
        self.fields["product"].queryset = products
        self.fields["needed_by"].required = order_type == "preorder"
        if order_type == "preorder":
            self.fields["needed_by"].help_text = "Isi 7–14 hari sebelum produk dibutuhkan."
        _apply_bootstrap_styles(self)

    def clean_needed_by(self):
        needed = self.cleaned_data.get("needed_by")
        if needed is None:
            return None
        delta = (needed - timezone.localdate()).days
        if delta < 0:
            raise forms.ValidationError("Tanggal kebutuhan tidak boleh di masa lalu.")
        if self.order_type == "preorder" and not 7 <= delta <= 14:
            raise forms.ValidationError("Pre-order harus dibuat 7–14 hari sebelum kebutuhan.")
        return needed

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        product = self.cleaned_data.get("product")
        if self.order_type == "surplus" and product and quantity > product.stock:
            raise forms.ValidationError(f"Stok yang tersedia hanya {product.stock}.")
        return quantity


class OrderStatusForm(forms.Form):
    """Form perubahan status dengan pilihan yang hanya boleh dipilih petani.

    Form ini sengaja bukan ModelForm agar status lama tidak tertimpa nilai POST
    sebelum `Order.transition_to` memeriksa urutan transisi.
    """

    status = forms.ChoiceField(label="Status berikutnya", choices=())

    def __init__(self, *args, order=None, is_admin=False, **kwargs):
        super().__init__(*args, **kwargs)
        allowed = set(ALLOWED_TRANSITIONS.get(order.status, set())) if order else set()
        if not is_admin:
            allowed &= FARMER_MANAGEABLE_STATUSES
        self.fields["status"].choices = [
            (value, label) for value, label in OrderStatus.choices if value in allowed
        ]
        _apply_bootstrap_styles(self)


class PaymentForm(forms.ModelForm):
    class Meta:
        model = PaymentRecord
        fields = ("status", "paid_amount", "note")
        labels = {
            "status": "Status pembayaran",
            "paid_amount": "Jumlah yang dicatat",
            "note": "Catatan simulasi",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_bootstrap_styles(self)
