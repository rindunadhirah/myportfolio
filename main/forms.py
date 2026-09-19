from django.forms import ModelForm, TextInput, Textarea, URLInput, DateInput

from main.models import Experience, Project


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

# Form for creating and updating experience data
class ExperienceForm(ModelForm):
    class Meta:
        model = Experience

        # Include every field that users can edit
        fields = [
            "title",
            "organization",
            "description",
            "responsibilities",
            "category",
            "thumbnail",
            "started_on",
            "ended_on",
        ]

        # Display clear names above the form fields
        labels = {
            "title": "Role Title",
            "organization": "Organization",
            "description": "Description",
            "responsibilities": "Responsibilities",
            "category": "Experience Type",
            "thumbnail": "Thumbnail URL",
            "started_on": "Start Date",
            "ended_on": "End Date",
        }

        # Make each input easier to understand and complete
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Product Management Intern",
                }
            ),
            "organization": TextInput(
                attrs={
                    "placeholder": "Organization name",
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Describe this experience",
                    "rows": 4,
                }
            ),
            "responsibilities": Textarea(
                attrs={
                    "placeholder": (
                        '["First responsibility", '
                        '"Second responsibility"]'
                    ),
                    "rows": 4,
                }
            ),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://example.com/image.jpg",
                }
            ),
            "started_on": DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                },
            ),
            "ended_on": DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                },
            ),
        }

    def clean(self):
        """Check that the Experience date range is valid."""
        cleaned_data = super().clean()
        started_on = cleaned_data.get("started_on")
        ended_on = cleaned_data.get("ended_on")

        # The end date cannot be earlier than the start date
        if started_on and ended_on and ended_on < started_on:
            self.add_error(
                "ended_on",
                "End date cannot be earlier than start date.",
            )

        return cleaned_data
