"""Form pendampingan mentor dan pencatatan kegiatan."""

from django import forms
from django.contrib.auth import get_user_model

from accounts.roles import Role

from .models import Mentorship, MentorshipActivity

User = get_user_model()
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"


def _apply_bootstrap_styles(form):
    for field in form.fields.values():
        css_class = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
        field.widget.attrs.setdefault("class", css_class)


class MentorshipForm(forms.ModelForm):
    class Meta:
        model = Mentorship
        fields = ("farmer", "mentor", "topic", "description", "scheduled_at", "status")
        widgets = {
            "topic": forms.TextInput(attrs={"placeholder": "Contoh: Teknik panen microgreens"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "scheduled_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format=DATETIME_FORMAT,
            ),
        }
        labels = {
            "farmer": "Petani",
            "mentor": "Mentor",
            "topic": "Materi pembelajaran",
            "description": "Detail materi",
            "scheduled_at": "Jadwal pendampingan",
            "status": "Status",
        }

    def __init__(self, *args, is_admin=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["farmer"].queryset = User.objects.filter(role=Role.FARMER.value)
        self.fields["mentor"].queryset = User.objects.filter(role=Role.MENTOR.value)
        self.fields["scheduled_at"].input_formats = [
            DATETIME_FORMAT,
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
        ]
        if not is_admin:
            self.fields.pop("mentor")
        _apply_bootstrap_styles(self)


class ActivityForm(forms.ModelForm):
    class Meta:
        model = MentorshipActivity
        fields = ("activity_date", "description", "evaluation")
        widgets = {
            "activity_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format=DATETIME_FORMAT,
            ),
            "description": forms.Textarea(attrs={"rows": 3}),
            "evaluation": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "activity_date": "Waktu kegiatan",
            "description": "Riwayat kegiatan",
            "evaluation": "Catatan evaluasi (opsional)",
        }
        help_texts = {
            "evaluation": "Jika diisi, catatan ini juga disimpan sebagai evaluasi pendampingan.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["activity_date"].input_formats = [
            DATETIME_FORMAT,
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
        ]
        _apply_bootstrap_styles(self)
