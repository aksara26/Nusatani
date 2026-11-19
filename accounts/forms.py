"""Form profil pengguna."""

from django import forms

from .models import CustomUser


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email")
        labels = {
            "first_name": "Nama depan",
            "last_name": "Nama belakang",
            "email": "Alamat email",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Nama depan"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Nama belakang"}),
            "email": forms.EmailInput(attrs={"placeholder": "nama@contoh.com"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
