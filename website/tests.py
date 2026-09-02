from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import ContactSubmission, Language, MediaAsset, Page, SiteSettings


class CmsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_vartec", "--force", verbosity=0)

    def test_home_renders_existing_vartec_content(self):
        response = self.client.get(reverse("website:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VARTEC")
        self.assertContains(response, "From design through operation and maintenance")
        self.assertContains(response, "finalmerge.mp4")

    def test_only_english_is_active_and_language_routes_are_removed(self):
        self.assertEqual(list(Language.objects.filter(is_active=True).values_list("code", flat=True)), ["en"])
        self.assertEqual(self.client.get("/nl/").status_code, 404)

    def test_hidden_project_returns_404(self):
        page = Page.objects.get(kind=Page.PROJECT, slug="solar-parks")
        page.is_active = False
        page.save(update_fields=("is_active",))
        response = self.client.get(page.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_safe_deploy_seed_does_not_overwrite_admin_visibility(self):
        page = Page.objects.get(kind=Page.PROJECT, slug="solar-parks")
        page.is_active = False
        page.save(update_fields=("is_active",))
        call_command("seed_vartec", "--if-empty", verbosity=0)
        page.refresh_from_db()
        self.assertFalse(page.is_active)

    def test_contact_submission_is_saved(self):
        response = self.client.post(
            reverse("website:home"),
            {
                "first_name": "Test",
                "last_name": "Customer",
                "email": "customer@example.com",
                "phone": "+44 20 0000 0000",
                "message": "Please contact me about an existing VARTEC service.",
                "website": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactSubmission.objects.count(), 1)
        self.assertEqual(ContactSubmission.objects.get().language_code, "en")

    def test_sitemap_contains_only_canonical_english_pages(self):
        response = self.client.get(reverse("website:sitemap"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/projects/solar-parks/")
        self.assertNotContains(response, "/nl/")

    def test_admin_is_available_to_superuser(self):
        user = get_user_model().objects.create_superuser("admin", "admin@example.com", "test-password")
        self.client.force_login(user)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Website content and configuration")

    def test_angular_cms_shell_and_session_are_available(self):
        response = self.client.get(reverse("cms"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<cms-root>", b"".join(response.streaming_content))
        session = self.client.get(reverse("cms-session"))
        self.assertEqual(session.status_code, 200)
        self.assertFalse(session.json()["authenticated"])

    def test_cms_api_requires_staff_access(self):
        response = self.client.get(reverse("cms-dashboard"))
        self.assertEqual(response.status_code, 401)

    def test_cms_api_can_list_and_update_page_visibility(self):
        user = get_user_model().objects.create_superuser("cms-admin", "cms@example.com", "test-password")
        self.client.force_login(user)
        response = self.client.get(reverse("cms-resource-list", kwargs={"resource": "pages"}))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.json()["pagination"]["total"], 0)
        page = Page.objects.get(kind=Page.PROJECT, slug="solar-parks")
        response = self.client.patch(
            reverse("cms-resource-detail", kwargs={"resource": "pages", "pk": page.pk}),
            data='{"is_active": false}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        page.refresh_from_db()
        self.assertFalse(page.is_active)

    def test_cms_is_english_only_and_exposes_media_previews(self):
        user = get_user_model().objects.create_superuser("preview-admin", "preview@example.com", "test-password")
        self.client.force_login(user)
        dashboard = self.client.get(reverse("cms-dashboard")).json()
        keys = {item["key"] for item in dashboard["resources"]}
        self.assertNotIn("languages", keys)
        self.assertNotIn("translations", keys)
        self.assertIn("sections", dashboard["summary"])
        media = MediaAsset.objects.filter(kind=MediaAsset.IMAGE).exclude(legacy_path="").first()
        response = self.client.get(reverse("cms-resource-detail", kwargs={"resource": "media", "pk": media.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["item"]["previewType"], "image")
        self.assertTrue(response.json()["item"]["preview"])

    def test_cms_appearance_exposes_colours_and_font(self):
        user = get_user_model().objects.create_superuser("appearance-admin", "appearance@example.com", "test-password")
        self.client.force_login(user)
        settings = SiteSettings.load()
        response = self.client.get(reverse("cms-resource-detail", kwargs={"resource": "settings", "pk": settings.pk}))
        schema = {field["name"]: field for field in response.json()["schema"]}
        self.assertEqual(schema["primary_colour"]["type"], "color")
        self.assertEqual(schema["secondary_colour"]["type"], "color")
        self.assertEqual(schema["surface_colour"]["type"], "color")
        self.assertEqual(schema["font_family"]["type"], "select")

    def test_site_settings_is_singleton(self):
        self.assertEqual(SiteSettings.load().pk, 1)
        self.assertEqual(SiteSettings.objects.count(), 1)
