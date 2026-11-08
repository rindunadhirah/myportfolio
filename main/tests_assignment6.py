from datetime import date
import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience


class AssignmentSixExperienceApiTest(APITestCase):
    """Test the Experience API rules required by Assignment 6."""

    @classmethod
    def setUpTestData(cls):
        Experience.objects.all().delete()
        cls.password = "test-password"
        cls.owner = User.objects.create_superuser(
            username="portfolio-owner",
            password=cls.password,
        )
        cls.regular_user = User.objects.create_user(
            username="regular-user",
            password=cls.password,
        )
        cls.editor = User.objects.create_user(
            username="experience-editor",
            password=cls.password,
        )
        editor_group = Group.objects.create(name="Editor")
        cls.editor.groups.add(editor_group)

        cls.experience = Experience.objects.create(
            title="Product Management Intern",
            organization="Example Organization",
            description="Supported product development.",
            responsibilities=["Prepared product requirements."],
            category="internship",
            started_on=date(2026, 6, 1),
            ended_on=date(2026, 8, 31),
        )

    def setUp(self):
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse(
            "api:experience-detail",
            args=[self.experience.id],
        )
        self.star_url = reverse(
            "api:experience-star",
            args=[self.experience.id],
        )

    def experience_payload(self, **changes):
        """Return valid API data that a test can customize."""
        data = {
            "title": "Product Mentee",
            "organization": "RISTEK Fasilkom UI",
            "description": "Learned product management.",
            "responsibilities": ["Prepared requirements."],
            "category": "program",
            "thumbnail": None,
            "started_on": "2026-09-01",
            "ended_on": "2026-10-01",
        }
        data.update(changes)
        return data

    def test_public_can_read_search_filter_and_sort(self):
        older_experience = Experience.objects.create(
            title="Alpha Volunteer",
            organization="Community Group",
            description="Supported a community program.",
            responsibilities=["Coordinated participants."],
            category="volunteer",
            started_on=date(2025, 1, 1),
        )

        list_response = self.client.get(self.list_url)
        detail_response = self.client.get(self.detail_url)
        search_response = self.client.get(
            self.list_url,
            {"search": "Example"},
        )
        filter_response = self.client.get(
            self.list_url,
            {"category": "volunteer"},
        )
        oldest_response = self.client.get(
            self.list_url,
            {"ordering": "oldest"},
        )
        title_response = self.client.get(
            self.list_url,
            {"ordering": "title"},
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(search_response.data[0]["id"], str(self.experience.id))
        self.assertEqual(filter_response.data[0]["id"], str(older_experience.id))
        self.assertEqual(
            [item["id"] for item in oldest_response.data],
            [str(older_experience.id), str(self.experience.id)],
        )
        self.assertEqual(
            [item["title"] for item in title_response.data],
            ["Alpha Volunteer", "Product Management Intern"],
        )

    def test_visitor_writes_are_rejected_without_database_changes(self):
        original_title = self.experience.title

        create_response = self.client.post(
            self.list_url,
            self.experience_payload(),
            format="json",
        )
        update_response = self.client.patch(
            self.detail_url,
            {"title": "Visitor Change"},
            format="json",
        )
        delete_response = self.client.delete(self.detail_url)

        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, original_title)

    def test_regular_user_writes_are_rejected_without_database_changes(self):
        self.client.force_authenticate(user=self.regular_user)
        original_description = self.experience.description

        create_response = self.client.post(
            self.list_url,
            self.experience_payload(),
            format="json",
        )
        update_response = self.client.patch(
            self.detail_url,
            {"description": "Regular user change"},
            format="json",
        )
        delete_response = self.client.delete(self.detail_url)

        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.description, original_description)

    def test_editor_can_patch_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)

        update_response = self.client.patch(
            self.detail_url,
            {"title": "Updated by Editor"},
            format="json",
        )
        create_response = self.client.post(
            self.list_url,
            self.experience_payload(),
            format="json",
        )
        delete_response = self.client.delete(self.detail_url)

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Updated by Editor")

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        create_response = self.client.post(
            self.list_url,
            self.experience_payload(),
            format="json",
        )
        created_detail_url = reverse(
            "api:experience-detail",
            args=[create_response.data["id"]],
        )
        update_response = self.client.patch(
            created_detail_url,
            {"title": "Updated Product Mentee"},
            format="json",
        )
        delete_response = self.client.delete(created_detail_url)

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["title"], "Updated Product Mentee")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(delete_response.content, b"")
        self.assertEqual(Experience.objects.count(), 1)

    def test_serializer_cleans_text_and_rejects_invalid_input(self):
        self.client.force_authenticate(user=self.owner)
        invalid_payloads = [
            ({"title": "<b></b>"}, "title"),
            ({"organization": "<i></i>"}, "organization"),
            ({"description": "<script></script>"}, "description"),
            ({"responsibilities": []}, "responsibilities"),
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
                    self.list_url,
                    self.experience_payload(**changes),
                    format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)

        clean_response = self.client.post(
            self.list_url,
            self.experience_payload(
                title="<b>Product Mentee</b>",
                organization="<i>RISTEK Fasilkom UI</i>",
                description="<p>Learned product management.</p>",
                responsibilities=["<strong>Prepared requirements.</strong>"],
            ),
            format="json",
        )

        self.assertEqual(clean_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(clean_response.data["title"], "Product Mentee")
        self.assertEqual(clean_response.data["organization"], "RISTEK Fasilkom UI")
        self.assertEqual(
            clean_response.data["responsibilities"],
            ["Prepared requirements."],
        )
        self.assertEqual(Experience.objects.count(), 2)

    def test_star_requires_login_and_uses_current_user(self):
        visitor_response = self.client.post(self.star_url)
        self.assertEqual(visitor_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.experience.starred_by.count(), 0)

        self.client.force_authenticate(user=self.regular_user)
        add_response = self.client.post(
            self.star_url,
            {"user_id": self.owner.id},
            format="json",
        )
        self.assertEqual(add_response.status_code, status.HTTP_200_OK)
        self.assertTrue(add_response.data["is_starred"])
        self.assertEqual(add_response.data["star_count"], 1)
        self.assertTrue(
            self.experience.starred_by.filter(pk=self.regular_user.pk).exists()
        )
        self.assertFalse(
            self.experience.starred_by.filter(pk=self.owner.pk).exists()
        )

        remove_response = self.client.post(self.star_url)
        self.assertFalse(remove_response.data["is_starred"])
        self.assertEqual(remove_response.data["star_count"], 0)

    def test_computed_fields_are_read_only_and_hide_sensitive_data(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {
                **self.experience_payload(),
                "star_count": 99,
                "is_starred": True,
                "starred_by": [self.regular_user.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertNotIn("email", response.data)
        self.assertNotIn("password", response.data)
        self.assertNotIn("starred_by", response.data)

    def test_missing_records_and_wrong_methods_return_clear_statuses(self):
        missing_url = reverse(
            "api:experience-detail",
            args=[uuid.uuid4()],
        )

        self.assertEqual(
            self.client.get(missing_url).status_code,
            status.HTTP_404_NOT_FOUND,
        )

        # Authenticate first so DRF can reach its method check
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(
            self.client.delete(self.list_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertEqual(
            self.client.get(self.star_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_session_write_requires_a_valid_csrf_token(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(
            client.login(
                username=self.owner.username,
                password=self.password,
            )
        )

        rejected_response = client.post(
            self.list_url,
            self.experience_payload(),
            format="json",
        )
        self.assertEqual(rejected_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)

        page_response = client.get(reverse("main:show_experience"))
        self.assertEqual(page_response.status_code, status.HTTP_200_OK)
        csrf_token = client.cookies["csrftoken"].value
        accepted_response = client.post(
            self.list_url,
            self.experience_payload(),
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(accepted_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Experience.objects.count(), 2)
