from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import ContactSubmission, Language, Page, SiteSettings, TextKey


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

    def test_dutch_site_uses_database_translation(self):
        response = self.client.get(reverse("website:home_i18n", kwargs={"lang_code": "nl"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Over Ons")
        self.assertContains(response, "Van ontwerp tot beheer en onderhoud")

    def test_new_language_falls_back_to_default_text(self):
        Language.objects.create(code="fr", name="French", native_name="Français", is_active=True, sort_order=3)
        response = self.client.get(reverse("website:home_i18n", kwargs={"lang_code": "fr"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, TextKey.objects.get(key="ABOUT_US").default_text)

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

    def test_sitemap_contains_active_pages_and_languages(self):
        response = self.client.get(reverse("website:sitemap"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/projects/solar-parks/")
        self.assertContains(response, "/nl/projects/solar-parks/")

    def test_admin_is_available_to_superuser(self):
        user = get_user_model().objects.create_superuser("admin", "admin@example.com", "test-password")
        self.client.force_login(user)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Website content and configuration")

    def test_site_settings_is_singleton(self):
        self.assertEqual(SiteSettings.load().pk, 1)
        self.assertEqual(SiteSettings.objects.count(), 1)
