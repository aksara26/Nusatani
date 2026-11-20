"""Autentikasi yang memaafkan spasi, kapital, dan mendukung email."""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class ForgivingModelBackend(ModelBackend):
    """Cocokkan username atau email tanpa memperhatikan spasi dan kapital.

    Username Django tidak boleh mengandung spasi, jadi menghapus spasi
    tidak akan membuat akun sah menjadi tidak bisa login. Ini membantu pengguna
    yang tanpa sengaja mengetik "petani 1" atau "Petani1". Email dipakai sebagai
    alternatif agar peran seperti HOREKA dan mitra bank bisa masuk dengan
    identitas usaha mereka.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return None

        normalized = "".join(str(username).split())
        user = UserModel._default_manager.filter(username__iexact=normalized).first()
        if user is None:
            user = UserModel._default_manager.filter(email__iexact=normalized).first()
        if user is None:
            return None
        if not user.check_password(password):
            return None
        if not self.user_can_authenticate(user):
            return None
        return user
