from django.urls import path

from . import views

app_name = "mentorship"

urlpatterns = [
    path("baru/", views.mentorship_create, name="create"),
    path("<int:pk>/ubah/", views.mentorship_update, name="update"),
    path("<int:pk>/kegiatan/", views.activity_create, name="activity_create"),
    path("<int:pk>/", views.mentorship_detail, name="detail"),
    path("", views.mentorship_list, name="list"),
]
