"""Endpoint pemeriksaan kesehatan untuk Render dan monitoring dasar."""

from django.db import connection
from django.http import JsonResponse


def health(request):
    """Mengembalikan 200 bila aplikasi dan database dapat diakses."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return JsonResponse(
            {"status": "error", "database": "unavailable"}, status=503
        )
    return JsonResponse({"status": "ok", "database": "ok"})
