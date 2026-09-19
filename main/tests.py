from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape
from main.models import Experience, Project
from main.forms import ExperienceForm


class MainTest(TestCase):
    def setUp(self):
        # Start each test with only one experience.
        Experience.objects.all().delete()
        self.experience = Experience.objects.create(
            title="Teaching Assistant for Discrete Mathematics 1",
            organization="Faculty of Computer Science, Universitas Indonesia",
            description=(
                "Grade quizzes and help students understand "
                "Discrete Mathematics concepts."
            ),
            responsibilities=[
                (
                    "Grade quizzes and assess students' understanding "
                    "of Discrete Mathematics concepts."
                ),
                (
                    "Conduct teaching assistance sessions to explain "
                    "course materials and answer students' questions."
                ),
                (
                    "Supervise students during quizzes to help the "
                    "assessments run smoothly."
                ),
            ],
            category="part-time",
            started_on=date(2026, 8, 1),
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(
            response,
            f'href="{reverse("main:show_experience")}"',
            count=2,
        )
        self.assertContains(response, "The journey behind my work")
        self.assertContains(
            response,
            f'href="{reverse("main:show_projects")}"',
        )

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/a-page-that-does-not-exist/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(
            str(self.experience),
            "Teaching Assistant for Discrete Mathematics 1",
        )
        self.assertEqual(
            self.experience.organization,
            "Faculty of Computer Science, Universitas Indonesia",
        )
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)
        self.assertEqual(len(self.experience.responsibilities), 3)

        def test_experience_end_date_cannot_be_before_start_date(self):
            # Submit an invalid Experience date range
            form = ExperienceForm(
                data={
                    "title": "Product Management Intern",
                    "organization": "Test Organization",
                    "description": "Test experience.",
                    "responsibilities": '["Created documentation."]',
                    "category": "internship",
                    "thumbnail": "",
                    "started_on": "2026-09-10",
                    "ended_on": "2026-09-01",
                }
            )

            self.assertFalse(form.is_valid())
            self.assertIn(
                "End date cannot be earlier than start date.",
                form.errors["ended_on"],
            )

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        for responsibility in self.experience.responsibilities:
            self.assertContains(response, escape(responsibility))
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Ongoing")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "No experience has been added yet.")

    def test_completed_experience(self):
        self.experience.ended_on = date(2026, 8, 31)
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Completed")
        self.assertNotContains(response, "Ongoing")


class ExperienceWorkflowTest(TestCase):
    def setUp(self):
        # Start each test with an empty Experience table
        Experience.objects.all().delete()

        # Create one Experience for update, delete, and JSON tests
        self.experience = Experience.objects.create(
            title="Product Management Intern",
            organization="Test Organization",
            description="A test experience.",
            responsibilities=[
                "Created product documentation.",
            ],
            category="internship",
            started_on=date(2026, 7, 1),
            ended_on=date(2026, 8, 31),
        )

    def experience_form_data(self, **changes):
        """Return valid form data with optional changes."""
        data = {
            "title": "Product Management Mentee",
            "organization": "RISTEK Fasilkom UI",
            "description": "Learned product management.",
            "responsibilities": (
                '["Prepared product requirements."]'
            ),
            "category": "program",
            "thumbnail": "",
            "started_on": "2026-07-01",
            "ended_on": "2026-08-31",
        }
        data.update(changes)
        return data

    def test_experience_json_endpoint(self):
        # Confirm that Experience data is serialized as JSON
        response = self.client.get(
            reverse("main:get_experiences_json")
        )
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["fields"]["title"],
            self.experience.title,
        )

    def test_experience_page_uses_deserialized_data(self):
        # The page receives a list created from deserialized JSON
        response = self.client.get(
            reverse("main:show_experience")
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(
            response.context["experience_list"],
            list,
        )
        self.assertContains(response, self.experience.title)

    def test_create_experience(self):
        # Submit valid data through ExperienceForm
        response = self.client.post(
            reverse("main:create_experience"),
            data=self.experience_form_data(),
        )

        self.assertRedirects(
            response,
            reverse("main:show_experience"),
        )
        self.assertTrue(
            Experience.objects.filter(
                title="Product Management Mentee",
            ).exists()
        )

    def test_update_experience(self):
        # Update the existing Experience using its UUID
        response = self.client.post(
            reverse(
                "main:update_experience",
                args=[self.experience.id],
            ),
            data=self.experience_form_data(
                title="Updated Experience",
            ),
        )
        self.experience.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("main:show_experience"),
        )
        self.assertEqual(
            self.experience.title,
            "Updated Experience",
        )

    def test_delete_experience_with_post(self):
        # Delete is allowed through a POST request
        response = self.client.post(
            reverse(
                "main:delete_experience",
                args=[self.experience.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("main:show_experience"),
        )
        self.assertFalse(
            Experience.objects.filter(
                id=self.experience.id,
            ).exists()
        )

    def test_delete_experience_rejects_get(self):
        # A GET request must not delete data
        response = self.client.get(
            reverse(
                "main:delete_experience",
                args=[self.experience.id],
            )
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(
            Experience.objects.filter(
                id=self.experience.id,
            ).exists()
        )

    def test_filter_experience_by_category(self):
        # Create another category to test the filter
        Experience.objects.create(
            title="Volunteer Experience",
            organization="Test Community",
            description="A volunteer experience.",
            responsibilities=["Supported an event."],
            category="volunteer",
            started_on=date(2026, 6, 1),
        )

        response = self.client.get(
            reverse("main:show_experience"),
            {"category": "internship"},
        )

        self.assertContains(
            response,
            self.experience.title,
        )
        self.assertNotContains(
            response,
            "Volunteer Experience",
        )


class ProjectPageTest(TestCase):
    def setUp(self):
        # Start each test with only one project.
        Project.objects.all().delete()

        self.project = Project.objects.create(
            title="Test Portfolio",
            slug="test-portfolio",
            summary="A portfolio project used for testing.",
            context="Independent web project",
            role="Developer",
            contributions=[
                "Built the project interface.",
                "Connected the page to Django.",
            ],
            technologies=["Django", "HTML5", "CSS3"],
            project_url="https://example.com/portfolio/",
            image_path="img/projects/sortify.webp",
            started_on=date(2026, 9, 1),
            is_featured=True,
        )

    def test_main_page_displays_project_preview(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.summary)
        self.assertContains(
            response,
            f'href="{reverse("main:show_projects")}"',
        )

    def test_projects_url_uses_correct_template(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")

    def test_projects_page_displays_database_content(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.summary)
        self.assertContains(response, self.project.role)
        self.assertContains(response, "Built the project interface.")
        self.assertContains(response, "Django")

    def test_empty_projects_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, "No projects have been added yet.")

    def test_projects_are_ordered_by_newest(self):
        Project.objects.create(
            title="Older Project",
            slug="older-project",
            summary="An older portfolio project.",
            context="Independent web project",
            role="Developer",
            contributions=["Built the project."],
            technologies=["Django"],
            project_url="https://example.com/older-project/",
            image_path="img/projects/sispro.webp",
            started_on=date(2026, 8, 1),
        )

        response = self.client.get(reverse("main:show_projects"))
        project_titles = [
            project.title
            for project in response.context["project_list"]
        ]

        self.assertEqual(
            project_titles,
            ["Test Portfolio", "Older Project"],
        )
