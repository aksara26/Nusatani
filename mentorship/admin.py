from django.contrib import admin

from .models import Mentorship, MentorshipActivity


@admin.register(Mentorship)
class MentorshipAdmin(admin.ModelAdmin):
    list_display = ("topic", "farmer", "mentor", "scheduled_at", "status")
    list_filter = ("status", "mentor")
    search_fields = ("topic", "farmer__username", "mentor__username", "description", "evaluation")
    autocomplete_fields = ("farmer", "mentor")
    readonly_fields = ("created_at", "updated_at")


@admin.register(MentorshipActivity)
class MentorshipActivityAdmin(admin.ModelAdmin):
    list_display = ("mentorship", "activity_date", "author")
    list_filter = ("activity_date",)
    search_fields = ("mentorship__topic", "description", "evaluation", "author__username")
    autocomplete_fields = ("mentorship", "author")
    readonly_fields = ("created_at",)
