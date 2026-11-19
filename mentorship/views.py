"""Halaman Mentorku untuk mentor dan petani yang dibimbing."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from accounts.roles import Role
from accounts.views import role_required

from .forms import ActivityForm, MentorshipForm
from .models import Mentorship


def _visible_mentorships(request):
    mentorships = Mentorship.objects.select_related("farmer", "mentor")
    if request.user.is_superuser:
        return mentorships
    if request.user.role == Role.MENTOR.value:
        return mentorships.filter(mentor=request.user)
    if request.user.role == Role.FARMER.value:
        return mentorships.filter(farmer=request.user)
    raise PermissionDenied("Peran Anda tidak memiliki akses ke Mentorku.")


def _viewable_mentorship(request, pk):
    mentorship = get_object_or_404(
        Mentorship.objects.select_related("farmer", "mentor"), pk=pk
    )
    if not request.user.is_superuser and request.user.pk not in {
        mentorship.farmer_id,
        mentorship.mentor_id,
    }:
        raise PermissionDenied("Anda tidak memiliki akses ke pendampingan ini.")
    return mentorship


def _managed_mentorship(request, pk):
    mentorship = get_object_or_404(Mentorship, pk=pk)
    if not request.user.is_superuser and mentorship.mentor_id != request.user.pk:
        raise PermissionDenied("Hanya mentor yang dapat mengubah pendampingan ini.")
    return mentorship


@role_required(Role.FARMER.value, Role.MENTOR.value)
def mentorship_list(request):
    return render(
        request,
        "mentorship/mentorship_list.html",
        {"mentorships": list(_visible_mentorships(request))},
    )


@role_required(Role.MENTOR.value)
def mentorship_create(request):
    if request.method == "POST":
        form = MentorshipForm(request.POST, is_admin=request.user.is_superuser)
        if form.is_valid():
            mentorship = form.save(commit=False)
            mentorship.mentor = form.cleaned_data.get("mentor") or request.user
            mentorship.save()
            messages.success(request, "Jadwal pendampingan berhasil dicatat.")
            return redirect("mentorship:detail", pk=mentorship.pk)
    else:
        form = MentorshipForm(is_admin=request.user.is_superuser)
    return render(
        request,
        "mentorship/mentorship_form.html",
        {"form": form, "title": "Tambah pendampingan", "mentorship": None},
    )


@role_required(Role.MENTOR.value)
def mentorship_update(request, pk):
    mentorship = _managed_mentorship(request, pk)
    if request.method == "POST":
        form = MentorshipForm(
            request.POST,
            instance=mentorship,
            is_admin=request.user.is_superuser,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Data pendampingan berhasil diperbarui.")
            return redirect("mentorship:detail", pk=mentorship.pk)
    else:
        form = MentorshipForm(instance=mentorship, is_admin=request.user.is_superuser)
    return render(
        request,
        "mentorship/mentorship_form.html",
        {"form": form, "title": "Ubah pendampingan", "mentorship": mentorship},
    )


@login_required
def mentorship_detail(request, pk):
    mentorship = _viewable_mentorship(request, pk)
    can_manage = request.user.is_superuser or mentorship.mentor_id == request.user.pk
    return render(
        request,
        "mentorship/mentorship_detail.html",
        {
            "mentorship": mentorship,
            "activities": mentorship.activities.select_related("author"),
            "can_manage": can_manage,
        },
    )


@role_required(Role.FARMER.value, Role.MENTOR.value)
def activity_create(request, pk):
    mentorship = _viewable_mentorship(request, pk)
    if request.method == "POST":
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.mentorship = mentorship
            activity.author = request.user
            activity.save()
            if activity.evaluation.strip():
                mentorship.evaluation = activity.evaluation
                mentorship.save(update_fields=["evaluation", "updated_at"])
            messages.success(request, "Kegiatan pendampingan berhasil dicatat.")
            return redirect("mentorship:detail", pk=mentorship.pk)
    else:
        form = ActivityForm()
    return render(
        request,
        "mentorship/activity_form.html",
        {"form": form, "mentorship": mentorship},
    )
