from django.forms import ModelForm, TextInput, Textarea, URLInput, DateInput

from main.models import Project


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "slug",
            "summary",
            "context",
            "role",
            "project_url",
            "image_path",
            "started_on",
            "ended_on",
            "achievement",
            "is_featured",
        ]

        labels = {
            "title": "Nama Proyek",
            "slug": "Slug Proyek",
            "summary": "Ringkasan Proyek",
            "context": "Konteks Proyek",
            "role": "Peran",
            "project_url": "URL Proyek",
            "image_path": "Path Gambar Proyek",
            "started_on": "Tanggal Mulai",
            "ended_on": "Tanggal Selesai",
            "achievement": "Pencapaian",
            "is_featured": "Tampilkan di Halaman Utama",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 100,
                }
            ),
            "slug": TextInput(
                attrs={
                    "placeholder": "portfolio-website",
                    "maxlength": 120,
                }
            ),
            "summary": Textarea(
                attrs={
                    "placeholder": "Ceritakan proyekmu secara singkat",
                    "rows": 3,
                }
            ),
            "context": TextInput(
                attrs={
                    "placeholder": "Personal Project / Hackathon / Coursework",
                }
            ),
            "role": TextInput(
                attrs={
                    "placeholder": "Frontend Developer / Product Manager",
                    "maxlength": 100,
                }
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/username/project",
                }
            ),
            "image_path": TextInput(
                attrs={
                    "placeholder": "img/projects/namafile.webp",
                }
            ),
            "started_on": DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "ended_on": DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "achievement": TextInput(
                attrs={
                    "placeholder": "Best Final Project / Semifinalist / etc.",
                }
            ),
        }