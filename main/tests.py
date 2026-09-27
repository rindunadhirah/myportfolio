from datetime import date

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
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
        # Use the portfolio owner for existing CRUD tests
        self.owner = User.objects.create_superuser(
            username="portfolio-owner",
            password="test-password",
        )
        self.client.force_login(self.owner)

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
            follow=True,
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
        self.assertContains(
            response,
            "Experience added successfully.",
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


class AssignmentFourAccessTest(TestCase):
    def setUp(self):
        # Create content for permission tests
        self.project = Project.objects.create(
            title="Permission Test Project",
            slug="permission-test-project",
            summary="A project used to test permissions.",
            context="Assignment 4",
            role="Developer",
            contributions=["Built the project."],
            technologies=["Django"],
            project_url="https://example.com/project/",
            image_path="img/projects/sortify.webp",
            started_on=date(2026, 9, 1),
        )
        self.experience = Experience.objects.create(
            title="Permission Test Experience",
            organization="Test Organization",
            description="An experience used to test permissions.",
            responsibilities=["Completed the assigned work."],
            category="program",
            started_on=date(2026, 9, 1),
        )

        # Create the three authenticated user roles
        self.regular_user = User.objects.create_user(
            username="regular-user",
            password="test-password",
        )
        self.editor = User.objects.create_user(
            username="editor-user",
            password="test-password",
        )
        self.owner = User.objects.create_superuser(
            username="portfolio-owner-test",
            password="test-password",
        )

        editor_group = Group.objects.create(name="Editor")
        self.editor.groups.add(editor_group)

    def test_regular_user_can_star_but_cannot_manage_content(self):
        # A regular user may star projects and experiences
        self.client.force_login(self.regular_user)

        project_response = self.client.post(
            reverse(
                "main:toggle_project_star",
                args=[self.project.id],
            )
        )
        experience_response = self.client.post(
            reverse(
                "main:toggle_experience_star",
                args=[self.experience.id],
            )
        )

        self.assertEqual(project_response.status_code, 302)
        self.assertEqual(experience_response.status_code, 302)
        self.assertTrue(
            self.project.starred_by.filter(
                pk=self.regular_user.pk,
            ).exists()
        )
        self.assertTrue(
            self.experience.starred_by.filter(
                pk=self.regular_user.pk,
            ).exists()
        )

        # A regular user cannot create, update, or delete content
        protected_requests = [
            self.client.get(reverse("main:create_project")),
            self.client.get(reverse("main:create_experience")),
            self.client.get(
                reverse(
                    "main:update_project",
                    args=[self.project.id],
                )
            ),
            self.client.get(
                reverse(
                    "main:update_experience",
                    args=[self.experience.id],
                )
            ),
            self.client.post(
                reverse(
                    "main:delete_project",
                    args=[self.project.id],
                )
            ),
            self.client.post(
                reverse(
                    "main:delete_experience",
                    args=[self.experience.id],
                )
            ),
        ]

        for response in protected_requests:
            self.assertEqual(response.status_code, 403)

    def test_editor_can_update_but_cannot_create_or_delete(self):
        # An Editor may update projects and experiences
        self.client.force_login(self.editor)

        project_update = self.client.get(
            reverse(
                "main:update_project",
                args=[self.project.id],
            )
        )
        experience_update = self.client.get(
            reverse(
                "main:update_experience",
                args=[self.experience.id],
            )
        )

        self.assertEqual(project_update.status_code, 200)
        self.assertEqual(experience_update.status_code, 200)

        # An Editor cannot create or delete content
        forbidden_requests = [
            self.client.get(reverse("main:create_project")),
            self.client.get(reverse("main:create_experience")),
            self.client.post(
                reverse(
                    "main:delete_project",
                    args=[self.project.id],
                )
            ),
            self.client.post(
                reverse(
                    "main:delete_experience",
                    args=[self.experience.id],
                )
            ),
        ]

        for response in forbidden_requests:
            self.assertEqual(response.status_code, 403)

        # An Editor may also star portfolio content
        self.client.post(
            reverse(
                "main:toggle_project_star",
                args=[self.project.id],
            )
        )
        self.client.post(
            reverse(
                "main:toggle_experience_star",
                args=[self.experience.id],
            )
        )

        self.assertTrue(
            self.project.starred_by.filter(
                pk=self.editor.pk,
            ).exists()
        )
        self.assertTrue(
            self.experience.starred_by.filter(
                pk=self.editor.pk,
            ).exists()
        )

    def test_visitor_can_read_content_but_cannot_use_account_actions(self):
        # Public portfolio pages and JSON remain readable
        public_urls = [
            reverse("main:show_main"),
            reverse("main:show_projects"),
            reverse("main:show_experience"),
            reverse("main:get_projects_json"),
            reverse("main:get_experiences_json"),
        ]

        for url in public_urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

        # Account actions redirect visitors to the login page
        protected_responses = [
            self.client.get(reverse("main:create_project")),
            self.client.get(reverse("main:create_experience")),
            self.client.get(
                reverse(
                    "main:update_project",
                    args=[self.project.id],
                )
            ),
            self.client.get(
                reverse(
                    "main:update_experience",
                    args=[self.experience.id],
                )
            ),
            self.client.post(
                reverse(
                    "main:delete_project",
                    args=[self.project.id],
                )
            ),
            self.client.post(
                reverse(
                    "main:delete_experience",
                    args=[self.experience.id],
                )
            ),
            self.client.post(
                reverse(
                    "main:toggle_project_star",
                    args=[self.project.id],
                )
            ),
            self.client.post(
                reverse(
                    "main:toggle_experience_star",
                    args=[self.experience.id],
                )
            ),
        ]

        for response in protected_responses:
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse("main:login"), response.url)

    def test_owner_can_manage_projects_and_experiences(self):
        # The portfolio owner may access every management form
        self.client.force_login(self.owner)

        allowed_pages = [
            self.client.get(reverse("main:create_project")),
            self.client.get(reverse("main:create_experience")),
            self.client.get(
                reverse(
                    "main:update_project",
                    args=[self.project.id],
                )
            ),
            self.client.get(
                reverse(
                    "main:update_experience",
                    args=[self.experience.id],
                )
            ),
        ]

        for response in allowed_pages:
            self.assertEqual(response.status_code, 200)

        # The portfolio owner may delete both types of content
        project_delete = self.client.post(
            reverse(
                "main:delete_project",
                args=[self.project.id],
            )
        )
        experience_delete = self.client.post(
            reverse(
                "main:delete_experience",
                args=[self.experience.id],
            )
        )

        self.assertEqual(project_delete.status_code, 302)
        self.assertEqual(experience_delete.status_code, 302)
        self.assertFalse(
            Project.objects.filter(pk=self.project.id).exists()
        )
        self.assertFalse(
            Experience.objects.filter(pk=self.experience.id).exists()
        )

    def test_owner_can_create_and_update_a_project(self):
        # Project CRUD must work for the portfolio owner
        self.client.force_login(self.owner)
        create_data = {
            "title": "Owner Project",
            "slug": "owner-project",
            "summary": "Created by the portfolio owner.",
            "context": "Assignment 4",
            "role": "Developer",
            "project_url": "https://example.com/owner-project/",
            "image_path": "img/projects/sortify.webp",
            "started_on": "2026-09-20",
            "ended_on": "",
            "achievement": "",
            "is_featured": "on",
        }

        create_response = self.client.post(
            reverse("main:create_project"),
            data=create_data,
        )
        self.assertRedirects(
            create_response,
            reverse("main:show_projects"),
        )
        self.assertTrue(
            Project.objects.filter(slug="owner-project").exists()
        )

        update_data = {
            **create_data,
            "title": "Updated Permission Project",
            "slug": self.project.slug,
        }
        update_response = self.client.post(
            reverse(
                "main:update_project",
                args=[self.project.id],
            ),
            data=update_data,
        )
        self.project.refresh_from_db()

        self.assertRedirects(
            update_response,
            reverse("main:show_projects"),
        )
        self.assertEqual(
            self.project.title,
            "Updated Permission Project",
        )

    def test_star_actions_require_post_and_csrf(self):
        # A GET request must never change a star
        self.client.force_login(self.regular_user)
        project_url = reverse(
            "main:toggle_project_star",
            args=[self.project.id],
        )
        experience_url = reverse(
            "main:toggle_experience_star",
            args=[self.experience.id],
        )

        self.assertEqual(self.client.get(project_url).status_code, 405)
        self.assertEqual(self.client.get(experience_url).status_code, 405)

        # A POST without a CSRF token must be rejected
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.regular_user)
        self.assertEqual(csrf_client.post(project_url).status_code, 403)
        self.assertEqual(csrf_client.post(experience_url).status_code, 403)

    def test_star_can_be_added_once_and_removed(self):
        # Repeating the action removes the existing star
        self.client.force_login(self.regular_user)
        project_url = reverse(
            "main:toggle_project_star",
            args=[self.project.id],
        )
        experience_url = reverse(
            "main:toggle_experience_star",
            args=[self.experience.id],
        )

        self.client.post(project_url)
        self.client.post(experience_url)
        self.assertEqual(self.project.starred_by.count(), 1)
        self.assertEqual(self.experience.starred_by.count(), 1)

        self.client.post(project_url)
        self.client.post(experience_url)
        self.assertEqual(self.project.starred_by.count(), 0)
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_json_does_not_expose_user_star_data(self):
        # Public JSON must not reveal usernames or star relationships
        self.project.starred_by.add(self.regular_user)
        self.experience.starred_by.add(self.regular_user)

        project_response = self.client.get(
            reverse("main:get_projects_json")
        )
        experience_response = self.client.get(
            reverse("main:get_experiences_json")
        )
        project_fields = project_response.json()[0]["fields"]
        experience_fields = experience_response.json()[0]["fields"]

        self.assertNotIn("starred_by", project_fields)
        self.assertNotIn("starred_by", experience_fields)
        self.assertNotContains(
            project_response,
            self.regular_user.username,
        )
        self.assertNotContains(
            experience_response,
            self.regular_user.username,
        )

    def test_management_buttons_match_the_user_role(self):
        # Visitors only see the login link for starring content
        visitor_projects = self.client.get(reverse("main:show_projects"))
        visitor_experiences = self.client.get(
            reverse("main:show_experience")
        )
        self.assertContains(visitor_projects, "Log in to star")
        self.assertContains(visitor_experiences, "Log in to star")
        self.assertNotContains(visitor_projects, "Add Project")
        self.assertNotContains(visitor_projects, "Edit Project")
        self.assertNotContains(visitor_projects, "Delete Project")
        self.assertNotContains(visitor_experiences, "Add Experience")
        self.assertNotContains(visitor_experiences, "Edit Experience")
        self.assertNotContains(visitor_experiences, "Delete Experience")

        # Editors see edit actions but not owner actions
        self.client.force_login(self.editor)
        editor_projects = self.client.get(reverse("main:show_projects"))
        editor_experiences = self.client.get(
            reverse("main:show_experience")
        )
        self.assertContains(editor_projects, "Edit Project")
        self.assertContains(editor_experiences, "Edit Experience")
        self.assertNotContains(editor_projects, "Add Project")
        self.assertNotContains(editor_projects, "Delete Project")
        self.assertNotContains(editor_experiences, "Add Experience")
        self.assertNotContains(editor_experiences, "Delete Experience")

        # The owner sees all management actions
        self.client.force_login(self.owner)
        owner_projects = self.client.get(reverse("main:show_projects"))
        owner_experiences = self.client.get(
            reverse("main:show_experience")
        )
        self.assertContains(owner_projects, "Add Project")
        self.assertContains(owner_projects, "Edit Project")
        self.assertContains(owner_projects, "Delete Project")
        self.assertContains(owner_experiences, "Add Experience")
        self.assertContains(owner_experiences, "Edit Experience")
        self.assertContains(owner_experiences, "Delete Experience")

    def test_project_search_and_role_filter_work_together(self):
        # Add unrelated content that should be removed by the filters
        Project.objects.create(
            title="Research Tool",
            slug="research-tool",
            summary="An unrelated project.",
            context="Research",
            role="Researcher",
            contributions=["Conducted research."],
            technologies=["Python"],
            project_url="https://example.com/research/",
            image_path="img/projects/sispro.webp",
            started_on=date(2026, 8, 1),
        )

        response = self.client.get(
            reverse("main:show_projects"),
            {"title": "Permission", "role": "Developer"},
        )

        self.assertContains(response, self.project.title)
        self.assertNotContains(response, "Research Tool")

    def test_experience_search_and_category_filter_work_together(self):
        # Add unrelated content that should be removed by the filters
        Experience.objects.create(
            title="Volunteer Designer",
            organization="Other Organization",
            description="An unrelated experience.",
            responsibilities=["Designed an event poster."],
            category="volunteer",
            started_on=date(2026, 8, 1),
        )

        response = self.client.get(
            reverse("main:show_experience"),
            {"search": "Test Organization", "category": "program"},
        )

        self.assertContains(response, self.experience.title)
        self.assertNotContains(response, "Volunteer Designer")

    def test_login_cookie_and_logout_session(self):
        # Login creates a session and records the latest login time
        login_response = self.client.post(
            reverse("main:login"),
            {
                "username": self.regular_user.username,
                "password": "test-password",
            },
        )

        self.assertEqual(login_response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)
        self.assertIn("last_login", login_response.cookies)
        self.assertTrue(login_response.cookies["last_login"].value)

        # Logout clears the session and the login cookie
        logout_response = self.client.get(reverse("main:logout"))

        self.assertEqual(logout_response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(
            logout_response.cookies["last_login"]["max-age"],
            0,
        )

    def test_registration_creates_a_regular_user(self):
        # Website registration must not grant elevated permissions
        response = self.client.post(
            reverse("main:register"),
            {
                "username": "new-regular-user",
                "password1": "SafeTestPassword2468",
                "password2": "SafeTestPassword2468",
            },
        )
        new_user = User.objects.get(username="new-regular-user")

        self.assertRedirects(response, reverse("main:login"))
        self.assertFalse(new_user.is_superuser)
        self.assertFalse(new_user.is_staff)
        self.assertFalse(new_user.groups.filter(name="Editor").exists())
