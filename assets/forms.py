"""Form pencatatan aset, starter kit, dan simulasi ijarah."""

from django import forms

from .models import Asset, FinancingScheme


def _apply_bootstrap_styles(form):
    for field in form.fields.values():
        css_class = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
        field.widget.attrs.setdefault("class", css_class)


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = (
            "name",
            "category",
            "quantity",
            "unit",
            "condition",
            "acquisition_date",
            "financing_scheme",
            "ijarah_duration_months",
            "ijarah_monthly_payment",
            "notes",
        )
        widgets = {
            "acquisition_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "name": "Nama aset",
            "category": "Kategori",
            "quantity": "Jumlah",
            "unit": "Satuan",
            "condition": "Kondisi",
            "acquisition_date": "Tanggal diperoleh",
            "financing_scheme": "Skema perolehan",
            "ijarah_duration_months": "Tenor ijarah (bulan)",
            "ijarah_monthly_payment": "Cicilan ijarah per bulan (Rp)",
            "notes": "Catatan",
        }
        help_texts = {
            "financing_scheme": "Pilih Starter kit untuk aset bawah usaha atau Ijarah untuk simulasi pembiayaan.",
            "ijarah_duration_months": "Isi hanya jika skema perolehan Ijarah.",
            "ijarah_monthly_payment": "Isi hanya jika skema perolehan Ijarah.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["acquisition_date"].input_formats = ["%Y-%m-%d"]
        _apply_bootstrap_styles(self)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("financing_scheme") == FinancingScheme.IJARAH.value:
            if not cleaned_data.get("ijarah_duration_months"):
                self.add_error("ijarah_duration_months", "Tenor wajib diisi untuk skema ijarah.")
            if not cleaned_data.get("ijarah_monthly_payment"):
                self.add_error("ijarah_monthly_payment", "Cicilan bulanan wajib diisi untuk skema ijarah.")
        else:
            cleaned_data["ijarah_duration_months"] = None
            cleaned_data["ijarah_monthly_payment"] = None
        return cleaned_data
