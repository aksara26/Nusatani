"""Form profil, pendaftaran, dan autentikasi pengguna."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import CustomUser
from .roles import Role


class NusaTaniAuthenticationForm(AuthenticationForm):
    """Pesan error yang jujur: username memaafkan spasi/kapital, password tidak."""

    error_messages = {
        "invalid_login": (
            "Username atau password salah. Username tidak peka huruf besar/kecil "
            "dan spasi diabaikan, tetapi password harus sama persis."
        ),
        "inactive": "Akun ini sedang tidak aktif.",
    }


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


class RegistrationForm(forms.ModelForm):
    """Pendaftaran mandiri hanya untuk peran yang bisa mendaftar sendiri."""

    ROLE_CHOICES = (
        (Role.FARMER.value, "Petani"),
        (Role.HORECA.value, "HOREKA"),
        (Role.CONSUMER.value, "Konsumen Rumah Tangga"),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Peran")
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Minimal 8 karakter"}),
    )
    password2 = forms.CharField(
        label="Ulangi password",
        widget=forms.PasswordInput(attrs={"placeholder": "Ketik ulang password"}),
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name", "role")
        labels = {
            "username": "Username",
            "email": "Alamat email",
            "first_name": "Nama depan",
            "last_name": "Nama belakang",
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "misalnya petani_sari"}),
            "email": forms.EmailInput(attrs={"placeholder": "nama@contoh.com"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Nama depan"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Nama belakang"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Username sudah digunakan. Silakan pilih yang lain.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if email and CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Alamat email sudah terdaftar.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and len(password1) < 8:
            raise forms.ValidationError("Password minimal 8 karakter.")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Konfirmasi password tidak sama.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
