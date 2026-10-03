import json

from django.forms import (
    CharField,
    DateInput,
    ModelForm,
    Textarea,
    TextInput,
    URLInput,
)
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

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

    def clean_title(self):
        """Remove HTML tags and reject an empty project title."""
        title = strip_tags(self.cleaned_data["title"]).strip()

        if not title:
            raise ValidationError(
                "Project title cannot contain only HTML tags."
            )

        return title

    def clean_summary(self):
        """Store the project summary without HTML tags."""
        return strip_tags(
            self.cleaned_data["summary"]
        ).strip()

    def clean_context(self):
        """Store the project context without HTML tags."""
        return strip_tags(
            self.cleaned_data["context"]
        ).strip()

    def clean_role(self):
        """Store the project role without HTML tags."""
        return strip_tags(
            self.cleaned_data["role"]
        ).strip()

    def clean_achievement(self):
        """Store the optional achievement without HTML tags."""
        return strip_tags(
            self.cleaned_data.get("achievement", "")
        ).strip()

    def clean(self):
        """Check that the Project date range is valid."""
        cleaned_data = super().clean()
        started_on = cleaned_data.get("started_on")
        ended_on = cleaned_data.get("ended_on")

        # The project cannot end before it starts
        if started_on and ended_on and ended_on < started_on:
            self.add_error(
                "ended_on",
                "End date cannot be earlier than start date.",
            )

        return cleaned_data

# Form for creating and updating experience data
class ExperienceForm(ModelForm):
    responsibilities = CharField(
        label="Responsibilities",
        help_text="Write one responsibility per line.",
        widget=Textarea(
            attrs={
                "placeholder": (
                    "Prepared product requirements\n"
                    "Coordinated with the development team"
                ),
                "rows": 4,
            }
        ),
    )

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

    def __init__(self, *args, **kwargs):
        """Show stored responsibilities as readable lines."""
        super().__init__(*args, **kwargs)
        responsibilities = self.initial.get("responsibilities")

        if isinstance(responsibilities, list):
            self.initial["responsibilities"] = "\n".join(
                str(item) for item in responsibilities
            )

    def clean_title(self):
        """Store the role title without HTML tags."""
        title = strip_tags(self.cleaned_data["title"]).strip()

        if not title:
            raise ValidationError(
                "Role title cannot contain only HTML tags."
            )

        return title

    def clean_organization(self):
        """Store the organization without HTML tags."""
        organization = strip_tags(
            self.cleaned_data["organization"]
        ).strip()

        if not organization:
            raise ValidationError(
                "Organization cannot contain only HTML tags."
            )

        return organization

    def clean_description(self):
        """Store the description without HTML tags."""
        description = strip_tags(
            self.cleaned_data["description"]
        ).strip()

        if not description:
            raise ValidationError(
                "Description cannot contain only HTML tags."
            )

        return description

    def clean_responsibilities(self):
        """Convert responsibility lines into a safe list."""
        raw_value = self.cleaned_data["responsibilities"].strip()

        # Keep older JSON input compatible with the new simple format
        try:
            parsed_value = json.loads(raw_value)
        except json.JSONDecodeError:
            parsed_value = raw_value.splitlines()

        if not isinstance(parsed_value, list):
            raise ValidationError(
                "Write one responsibility per line."
            )

        responsibilities = [
            strip_tags(str(item)).strip()
            for item in parsed_value
            if strip_tags(str(item)).strip()
        ]

        if not responsibilities:
            raise ValidationError(
                "Add at least one responsibility."
            )

        return responsibilities

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
