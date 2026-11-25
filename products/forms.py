"""Form katalog dan stok untuk petani."""

from django import forms

from .models import Inventory, Product


def _apply_bootstrap_styles(form):
    """Tambahkan kelas Bootstrap pada widget tanpa mengubah perilaku field."""
    for field in form.fields.values():
        css_class = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
        field.widget.attrs.setdefault("class", css_class)


class ProductForm(forms.ModelForm):
    """Form tambah/ubah produk sekaligus menetapkan stok awal."""

    initial_stock = forms.IntegerField(
        min_value=0,
        initial=0,
        label="Jumlah stok",
        help_text="Stok dapat diubah lagi setelah produk dibuat.",
    )

    class Meta:
        model = Product
        fields = (
            "variety",
            "name",
            "description",
            "price",
            "photo_url",
            "is_surplus",
            "available_from",
            "is_active",
            "initial_stock",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "available_from": forms.DateInput(attrs={"type": "date"}),
            "photo_url": forms.URLInput(
                attrs={"placeholder": "https://contoh.com/foto-produk.jpg"}
            ),
        }
        help_texts = {
            "photo_url": (
                "Opsional. Biarkan kosong untuk memakai gambar contoh sesuai varietas."
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_bootstrap_styles(self)
        if self.instance and self.instance.pk:
            inventory = Inventory.objects.filter(product=self.instance).first()
            if inventory:
                self.fields["initial_stock"].initial = inventory.quantity

    def save(self, commit=True):
        product = super().save(commit=commit)
        if commit:
            Inventory.objects.update_or_create(
                product=product,
                defaults={"quantity": self.cleaned_data["initial_stock"]},
            )
        return product


class InventoryForm(forms.ModelForm):
    """Form cepat untuk memperbarui jumlah stok."""

    class Meta:
        model = Inventory
        fields = ("quantity",)
        labels = {"quantity": "Jumlah stok"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_bootstrap_styles(self)
