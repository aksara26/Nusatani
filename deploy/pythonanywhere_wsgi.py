"""Template WSGI untuk deployment di PythonAnywhere.

Cara pakai:
1. Salin file ini ke `/var/www/<username>_pythonanywhere_com_wsgi.py`
   melalui tab Web → link WSGI configuration file di PythonAnywhere.
2. Ganti `<username>` pada variabel `path` dengan username PythonAnywhere Anda.
   Contoh: /home/aksara26/Nusatani
3. Pastikan file `.env` sudah dibuat di folder proyek (lihat
   `.env.pythonanywhere.example`), lalu klik Reload di tab Web.

File ini tidak dipakai di Render; Render menggunakan `config/wsgi.py`.
"""

import os
import sys

# Ganti <username> sesuai akun PythonAnywhere Anda.
path = "/home/<username>/Nusatani"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
