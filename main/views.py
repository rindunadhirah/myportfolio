from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project


def show_main(request):
    """Display the main portfolio page."""
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
    }
    return render(request, "index.html", context)


# Project data delivery
def get_projects_json(request):
    """Return project data in JSON format."""
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
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
    }
    return render(request, "projects.html", context)


def create_project(request):
    """Create a project using ProjectForm."""
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
    }
    return render(request, "projects_form.html", context)


def delete_project(request, project_id):
    """Delete a project after a POST request."""
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
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
    }
    return render(request, "experience.html", context)


# Experience form actions
def create_experience(request):
    """Create an experience using ExperienceForm."""
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


def update_experience(request, experience_id):
    """Update an existing experience."""
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


@require_POST
def delete_experience(request, experience_id):
    """Delete an experience using a POST request."""
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