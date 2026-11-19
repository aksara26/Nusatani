"""Form pemeriksaan kualitas oleh petugas QC."""

from django import forms

from .models import QcStatus, QualityInspection


class InspectionForm(forms.ModelForm):
    class Meta:
        model = QualityInspection
        fields = (
            "visual_ok",
            "cleanliness_ok",
            "freshness_ok",
            "weight_ok",
            "notes",
            "result",
        )
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["result"].choices = [
            (value, label)
            for value, label in QcStatus.choices
            if value != QcStatus.MENUNGGU.value
        ]
        for field in self.fields.values():
            css_class = (
                "form-check-input"
                if isinstance(field.widget, forms.CheckboxInput)
                else "form-control"
            )
            field.widget.attrs.setdefault("class", css_class)
