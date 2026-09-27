import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project


def user_is_editor(user):
    """Check whether a user belongs to the Editor group."""
    return (
        user.is_authenticated
        and user.groups.filter(name="Editor").exists()
    )


def show_main(request):
    """Display the main portfolio page."""
    last_login = request.COOKIES.get('last_login', 'No active login session / Cookie not found')
    context = {
        "name": "Rindu Maharani Nadhirah",
        "npm": "2506587131",
        "study_program": "B.S. Computer Science",
        "bio": (
            "Computer Science undergraduate at Universitas "
            "Indonesia with a growing interest in data science, "
            "product management, and business development."
        ),
        "project_preview_list": Project.objects.all()[:3],
        "last_login": last_login,
    }
    return render(request, "index.html", context)


# Project data delivery
def get_projects_json(request):
    """Return project data in JSON format."""
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize(
        "json", projects, use_natural_foreign_keys=True  # Tambahkan argumen ini
    )
    return HttpResponse(
        projects_json,
        content_type="application/json",
    )


def show_projects(request):
    """Deserialize and display project data."""
    json_response = get_projects_json(request)

    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    project_list = [project.object for project in projects]

    context = {
        "name": "Rindu Maharani Nadhirah",
        "project_list": project_list,
        "title_query": request.GET.get("title", "").strip(),
        "is_editor": user_is_editor(request.user),
    }
    return render(request, "projects.html", context)


@login_required(login_url="main:login")
def create_project(request):
    """Create a project using ProjectForm."""
    # Only the portfolio owner can create project data
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Project added successfully.",
        )
        return redirect("main:show_projects")

    context = {
        "name": "Rindu Maharani Nadhirah",
        "form": form,
        "form_title": "Add Project",
        "submit_label": "Add Project",
    }
    return render(request, "projects_form.html", context)


@login_required(login_url="main:login")
def update_project(request, project_id):
    """Update an existing project."""
    # Editors and the portfolio owner can update project data
    if not (
        request.user.is_superuser
        or user_is_editor(request.user)
    ):
        raise PermissionDenied

    project = get_object_or_404(
        Project,
        pk=project_id,
    )
    form = ProjectForm(
        request.POST or None,
        instance=project,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Project updated successfully.",
        )
        return redirect("main:show_projects")

    context = {
        "name": "Rindu Maharani Nadhirah",
        "form": form,
        "form_title": "Edit Project",
        "submit_label": "Save Changes",
    }
    return render(request, "projects_form.html", context)


@login_required(login_url="main:login")
@require_POST
def delete_project(request, project_id):
    """Delete a project using a POST request."""
    # Only the portfolio owner can delete project data
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(
        Project,
        pk=project_id,
    )
    project.delete()

    messages.success(
        request,
        "Project deleted successfully.",
    )
    return redirect("main:show_projects")


# Experience data delivery
def get_experiences_json(request):
    """Return experience data in JSON format."""
    category_query = request.GET.get("category", "").strip()
    experiences = Experience.objects.all()

    if category_query:
        experiences = experiences.filter(
            category=category_query,
        )

    experiences_json = serializers.serialize(
        "json",
        experiences,
    )
    return HttpResponse(
        experiences_json,
        content_type="application/json",
    )


def show_experience(request):
    """Deserialize and display experience data."""
    json_response = get_experiences_json(request)

    experiences = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    experience_list = [
        experience.object
        for experience in experiences
    ]

    context = {
        "name": "Rindu Maharani Nadhirah",
        "experience_list": experience_list,
        "experience_categories": Experience.EXPERIENCE_CHOICES,
        "category_query": request.GET.get(
            "category",
            "",
        ).strip(),
        "is_editor": user_is_editor(request.user),
    }
    return render(request, "experience.html", context)


# Experience form actions
@login_required(login_url="main:login")
def create_experience(request):
    """Create an experience using ExperienceForm."""
    # Only the portfolio owner can create experience data
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Experience added successfully.",
        )
        return redirect("main:show_experience")

    context = {
        "name": "Rindu Maharani Nadhirah",
        "form": form,
        "form_title": "Add Experience",
        "submit_label": "Add Experience",
    }
    return render(request, "experience_form.html", context)


@login_required(login_url="main:login")
def update_experience(request, experience_id):
    """Update an existing experience."""
    # Editors and the portfolio owner can update experience data
    if not (
        request.user.is_superuser
        or user_is_editor(request.user)
    ):
        raise PermissionDenied

    experience = get_object_or_404(
        Experience,
        pk=experience_id,
    )
    form = ExperienceForm(
        request.POST or None,
        instance=experience,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Experience updated successfully.",
        )
        return redirect("main:show_experience")

    context = {
        "name": "Rindu Maharani Nadhirah",
        "form": form,
        "form_title": "Edit Experience",
        "submit_label": "Save Changes",
    }
    return render(request, "experience_form.html", context)


@login_required(login_url="main:login")
@require_POST
def delete_experience(request, experience_id):
    """Delete an experience using a POST request."""
    # Only the portfolio owner can delete experience data
    if not request.user.is_superuser:
        raise PermissionDenied
    experience = get_object_or_404(
        Experience,
        pk=experience_id,
    )
    experience.delete()

    messages.success(
        request,
        "Experience deleted successfully.",
    )
    return redirect("main:show_experience")


@login_required(login_url="main:login")
@require_POST
def toggle_experience_star(request, experience_id):
    """Add or remove the current user's Experience star."""
    experience = get_object_or_404(
        Experience,
        pk=experience_id,
    )

    # Remove an existing star or add a new star
    if experience.starred_by.filter(pk=request.user.pk).exists():
        experience.starred_by.remove(request.user)
        message = f"Removed your star from {experience.title}."
    else:
        experience.starred_by.add(request.user)
        message = f"Starred {experience.title}."

    messages.success(request, message)
    return redirect("main:show_experience")


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect("main:login")

    context = {
        "name": "Nadhirah",
        "form": form,
    }
    return render(request, "register.html", context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Nadhirah",
        "form": form,
    }
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response


@login_required(login_url="main:login")
@require_POST
def toggle_project_star(request, project_id):
    """Add or remove the current user's Project star."""
    project = get_object_or_404(
        Project,
        pk=project_id,
    )

    # Remove an existing star or add a new star
    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
        message = f"Removed your star from {project.title}."
    else:
        project.starred_by.add(request.user)
        message = f"Starred {project.title}."

    messages.success(request, message)
    return redirect("main:show_projects")
