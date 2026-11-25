#!/usr/bin/env bash
# Perbarui aplikasi NusaTani yang sudah berjalan di PythonAnywhere.
#
# Jalankan dari Bash console PythonAnywhere:
#
#     cd ~/Nusatani
#     bash deploy/pythonanywhere_update.sh
#
# Skrip ini menarik kode terbaru, memperbarui dependensi, menjalankan migrasi,
# mengumpulkan static files, lalu memicu reload web app bila file WSGI ditemukan.

set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> Menarik kode terbaru dari GitHub"
git pull --ff-only origin main

echo "==> Mengaktifkan virtualenv"
if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
else
  echo "Virtualenv tidak ditemukan (.venv atau venv)." >&2
  exit 1
fi

echo "==> Memasang dependensi"
pip install -r requirements.txt

echo "==> Menjalankan migrasi database"
python manage.py migrate --noinput

echo "==> Mengumpulkan static files"
python manage.py collectstatic --noinput

echo "==> Versi aktif:"
git log -1 --oneline

wsgi_file="/var/www/$(whoami)_pythonanywhere_com_wsgi.py"
if [ -f "$wsgi_file" ]; then
  touch "$wsgi_file"
  echo "==> Reload web app dipicu lewat $wsgi_file"
else
  echo "==> File WSGI tidak ditemukan. Klik Reload di tab Web PythonAnywhere."
fi

echo "Selesai. Buka https://$(whoami).pythonanywhere.com/health/ untuk verifikasi."
