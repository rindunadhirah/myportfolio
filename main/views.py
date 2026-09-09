from django.shortcuts import render

from main.models import Experience


def show_main(request):
    context = {
        "name": "Rindu Maharani Nadhirah",
        "npm": "2506587131",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Computer Science undergraduate at Universitas"
            "Indonesia with a growing interest in data science,"
            "product management, and business development."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Rindu Maharani Nadhirah",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)