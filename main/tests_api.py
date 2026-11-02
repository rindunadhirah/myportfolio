from datetime import date
import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience, Project


class PortfolioApiTest(APITestCase):
    """Test the Tutorial 7 DRF API contract."""

    def setUp(self):
        Project.objects.all().delete()
        Experience.objects.all().delete()

        self.owner = User.objects.create_superuser(
            username="owner",
            password="test-password",
        )
        self.visitor = User.objects.create_user(
            username="visitor",
            password="test-password",
        )
        self.editor = User.objects.create_user(
            username="editor",
            password="test-password",
        )
        editor_group = Group.objects.create(name="Editor")
        self.editor.groups.add(editor_group)

        self.project = Project.objects.create(
            title="Portfolio",
            slug="portfolio",
            summary="My website",
            context="Tutorial 7",
            role="Developer",
            contributions=["Built the API."],
            technologies=["Django"],
            project_url="https://example.com/portfolio/",
            image_path="img/projects/sortify.webp",
            started_on=date(2026, 10, 1),
        )
        self.experience = Experience.objects.create(
            title="Product Intern",
            organization="Example Organization",
            description="Supported product development.",
            responsibilities=["Prepared product requirements."],
            category="internship",
            started_on=date(2026, 9, 1),
        )

        self.project_list_url = reverse("api:project-list")
        self.project_detail_url = reverse(
            "api:project-detail",
            args=[self.project.id],
        )
        self.project_star_url = reverse(
            "api:project-star",
            args=[self.project.id],
        )
        self.experience_list_url = reverse(
            "api:experience-list"
        )
        self.experience_detail_url = reverse(
            "api:experience-detail",
            args=[self.experience.id],
        )
        self.experience_star_url = reverse(
            "api:experience-star",
            args=[self.experience.id],
        )

    def project_payload(self, **changes):
        data = {
            "title": "New API Project",
            "slug": "new-api-project",
            "summary": "Created through DRF.",
            "context": "Tutorial 7",
            "role": "Developer",
            "contributions": ["Built the REST API."],
            "technologies": ["Django", "DRF"],
            "project_url": "https://example.com/new-project/",
            "image_path": "img/projects/sortify.webp",
            "started_on": "2026-10-10",
            "ended_on": None,
            "achievement": "",
            "is_featured": False,
        }
        data.update(changes)
        return data

    def experience_payload(self, **changes):
        data = {
            "title": "Product Mentee",
            "organization": "RISTEK Fasilkom UI",
            "description": "Learned product management.",
            "responsibilities": ["Prepared requirements."],
            "category": "program",
            "thumbnail": None,
            "started_on": "2026-10-01",
            "ended_on": None,
        }
        data.update(changes)
        return data

    def test_public_project_list_detail_search_and_empty_results(self):
        list_response = self.client.get(self.project_list_url)
        detail_response = self.client.get(self.project_detail_url)
        search_response = self.client.get(
            self.project_list_url,
            {"title": "port"},
        )
        empty_response = self.client.get(
            self.project_list_url,
            {"title": "does-not-exist"},
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data[0]["id"], str(self.project.id))
        self.assertNotIn("fields", list_response.data[0])
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(search_response.data[0]["title"], "Portfolio")
        self.assertEqual(empty_response.data, [])

    def test_guest_and_regular_user_cannot_manage_projects(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)

            self.assertEqual(
                self.client.post(
                    self.project_list_url,
                    self.project_payload(),
                    format="json",
                ).status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(
                    self.project_detail_url,
                    {"title": "Changed"},
                    format="json",
                ).status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(
                    self.project_detail_url
                ).status_code,
                status.HTTP_403_FORBIDDEN,
            )

        self.assertEqual(Project.objects.count(), 1)

    def test_owner_can_create_project(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.project_list_url,
            self.project_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Project.objects.filter(pk=response.data["id"]).exists()
        )

    def test_project_serializer_validation(self):
        self.client.force_authenticate(user=self.owner)
        invalid_payloads = [
            ({"title": " "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
            (
                {
                    "started_on": "2026-10-10",
                    "ended_on": "2026-10-01",
                },
                "ended_on",
            ),
        ]

        for changes, field in invalid_payloads:
            with self.subTest(field=field):
                response = self.client.post(
                    self.project_list_url,
                    self.project_payload(**changes),
                    format="json",
                )
                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn(field, response.data)

        self.assertEqual(Project.objects.count(), 1)

    def test_project_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        patch_response = self.client.patch(
            self.project_detail_url,
            {"title": "Changed"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Changed")
        self.assertEqual(self.project.summary, "My website")

        incomplete_put = self.client.put(
            self.project_detail_url,
            {"title": "Incomplete"},
            format="json",
        )
        self.assertEqual(
            incomplete_put.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        complete_put = self.client.put(
            self.project_detail_url,
            self.project_payload(slug="portfolio"),
            format="json",
        )
        self.assertEqual(complete_put.status_code, status.HTTP_200_OK)

        delete_response = self.client.delete(self.project_detail_url)
        self.assertEqual(
            delete_response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertEqual(delete_response.content, b"")
        self.assertFalse(
            Project.objects.filter(pk=self.project.id).exists()
        )

    def test_project_star_requires_login_and_toggles(self):
        self.assertEqual(
            self.client.post(self.project_star_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.client.force_authenticate(user=self.visitor)
        first_response = self.client.post(self.project_star_url)
        second_response = self.client.post(self.project_star_url)

        self.assertTrue(first_response.data["is_starred"])
        self.assertEqual(first_response.data["star_count"], 1)
        self.assertFalse(second_response.data["is_starred"])
        self.assertEqual(second_response.data["star_count"], 0)
        self.assertEqual(
            self.client.get(self.project_star_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_project_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        payload = {
            **self.project_payload(),
            "star_count": 99,
            "is_starred": True,
            "starred_by_names": "forged",
            "starred_by": [self.visitor.id],
        }
        response = self.client.post(
            self.project_list_url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")

    def test_staff_and_editor_cannot_manage_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.client.force_authenticate(user=self.visitor)
        staff_response = self.client.patch(
            self.project_detail_url,
            {"title": "Staff Change"},
            format="json",
        )

        self.client.force_authenticate(user=self.editor)
        editor_response = self.client.patch(
            self.project_detail_url,
            {"title": "Editor Change"},
            format="json",
        )

        self.assertEqual(staff_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(editor_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_methods_and_missing_project(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(
            self.client.delete(self.project_list_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        missing_url = reverse(
            "api:project-detail",
            args=[uuid.uuid4()],
        )
        self.assertEqual(
            self.client.get(missing_url).status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(
            client.login(
                username="owner",
                password="test-password",
            )
        )
        response = client.post(
            self.project_list_url,
            self.project_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        page = client.get(
            self.project_list_url,
            HTTP_ACCEPT="text/html",
        )
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.project_list_url,
            self.project_payload(),
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_experience_editor_permissions(self):
        public_response = self.client.get(
            self.experience_list_url,
            {"search": "Product", "category": "internship"},
        )
        self.assertEqual(public_response.status_code, status.HTTP_200_OK)
        self.assertEqual(public_response.data[0]["id"], str(self.experience.id))

        self.client.force_authenticate(user=self.editor)
        patch_response = self.client.patch(
            self.experience_detail_url,
            {"title": "Updated by Editor"},
            format="json",
        )
        create_response = self.client.post(
            self.experience_list_url,
            self.experience_payload(),
            format="json",
        )
        delete_response = self.client.delete(self.experience_detail_url)

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_experience_owner_validation_and_stars(self):
        self.client.force_authenticate(user=self.owner)
        create_response = self.client.post(
            self.experience_list_url,
            self.experience_payload(
                title="Product <b>Mentee</b>",
                description=(
                    "<script>alert('x')</script>Safe description."
                ),
            ),
            format="json",
        )
        invalid_response = self.client.post(
            self.experience_list_url,
            self.experience_payload(
                started_on="2026-10-10",
                ended_on="2026-10-01",
            ),
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data["title"], "Product Mentee")
        self.assertNotIn("<script>", create_response.data["description"])
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ended_on", invalid_response.data)

        self.client.force_authenticate(user=self.visitor)
        first_star = self.client.post(self.experience_star_url)
        second_star = self.client.post(self.experience_star_url)
        self.assertTrue(first_star.data["is_starred"])
        self.assertFalse(second_star.data["is_starred"])
