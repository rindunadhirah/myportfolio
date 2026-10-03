import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

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


def get_projects_json(request):
    """Return filtered projects and the current user's star status."""
    title_query = request.GET.get("title", "").strip()
    role_query = request.GET.get("role", "").strip()
    projects = Project.objects.prefetch_related("starred_by").all()

    # Search by project title
    if title_query:
        projects = projects.filter(title__icontains=title_query)

    # Filter by the user's role in the project
    if role_query:
        projects = projects.filter(role=role_query)

    project_data = []

    for project in projects:
        starred_users = list(project.starred_by.all())
        is_starred = (
            request.user.is_authenticated
            and request.user in starred_users
        )

        project_data.append(
            {
                "pk": str(project.id),
                "fields": {
                    "title": project.title,
                    "slug": project.slug,
                    "summary": project.summary,
                    "context": project.context,
                    "role": project.role,
                    "contributions": project.contributions,
                    "technologies": project.technologies,
                    "project_url": project.project_url,
                    "image_path": project.image_path,
                    "started_on": project.started_on,
                    "ended_on": project.ended_on,
                    "achievement": project.achievement,
                    "is_featured": project.is_featured,
                    "star_count": len(starred_users),
                    "is_starred": is_starred,
                },
            }
        )

    return JsonResponse(project_data, safe=False)


@ensure_csrf_cookie
def show_projects(request):
    """Display the Projects page before AJAX loads its data."""
    context = {
        "name": "Rindu Maharani Nadhirah",
        "title_query": request.GET.get("title", "").strip(),
        "role_query": request.GET.get("role", "").strip(),
        "is_editor": user_is_editor(request.user),
        "project_roles": Project.objects.order_by("role").values_list(
            "role",
            flat=True,
        ).distinct(),
        "form": ProjectForm(),
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


@require_POST
def create_project_ajax(request):
    """Create a project and return a JSON response."""
    # Return JSON instead of redirecting unauthorized users
    if not request.user.is_superuser:
        return JsonResponse(
            {
                "message": (
                    "Only the portfolio owner can add projects."
                )
            },
            status=403,
        )

    form = ProjectForm(request.POST)

    if form.is_valid():
        project = form.save()

        return JsonResponse(
            {
                "message": "Project added successfully.",
                "pk": str(project.id),
            },
            status=201,
        )

    return JsonResponse(
        {"errors": form.errors.get_json_data()},
        status=400,
    )


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
    """Return filtered experiences and safe star information."""
    search_query = request.GET.get("search", "").strip()
    category_query = request.GET.get("category", "").strip()
    experiences = Experience.objects.prefetch_related("starred_by").all()

    # Search by role title or organization
    if search_query:
        experiences = experiences.filter(
            Q(title__icontains=search_query)
            | Q(organization__icontains=search_query)
        )

    # Filter by experience type
    if category_query:
        experiences = experiences.filter(
            category=category_query,
        )

    experience_data = []

    for experience in experiences:
        starred_users = list(experience.starred_by.all())
        is_starred = (
            request.user.is_authenticated
            and request.user in starred_users
        )

        experience_data.append(
            {
                "pk": str(experience.id),
                "fields": {
                    "title": experience.title,
                    "organization": experience.organization,
                    "description": experience.description,
                    "responsibilities": experience.responsibilities,
                    "category": experience.category,
                    "category_label": experience.get_category_display(),
                    "thumbnail": experience.thumbnail,
                    "started_on": experience.started_on.isoformat(),
                    "ended_on": (
                        experience.ended_on.isoformat()
                        if experience.ended_on
                        else None
                    ),
                    "is_ongoing": experience.is_ongoing,
                    "star_count": len(starred_users),
                    "is_starred": is_starred,
                },
            }
        )

    return JsonResponse(experience_data, safe=False)


@ensure_csrf_cookie
def show_experience(request):
    """Display the Experience page before AJAX loads its data."""
    context = {
        "name": "Rindu Maharani Nadhirah",
        "experience_categories": Experience.EXPERIENCE_CHOICES,
        "search_query": request.GET.get("search", "").strip(),
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
