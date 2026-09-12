from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Project


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="PBP Teaching Assistant",
            description="Help students understand web development.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(
            response,
            f'href="{reverse("main:show_projects")}"',
        )

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/a-page-that-does-not-exist/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "PBP Teaching Assistant")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Ongoing")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "No experience has been added yet.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Completed")
        self.assertNotContains(response, "Ongoing")


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
        project_titles = list(
            response.context["project_list"].values_list(
                "title",
                flat=True,
            )
        )

        self.assertEqual(
            project_titles,
            ["Test Portfolio", "Older Project"],
        )
