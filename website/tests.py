from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import ContactSubmission, Language, MediaAsset, Page, SiteSettings, TextKey


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
        self.assertContains(response, "Solar energy projects, engineered for performance.")
        self.assertContains(response, "data-autoplay-video")
        self.assertContains(response, "autoplay")
        self.assertContains(response, 'rel="preload" as="image"')
        self.assertContains(response, "data-chatbot")
        self.assertContains(response, "VARTEC Assistant")

    def test_only_english_is_active_and_language_routes_are_removed(self):
        self.assertEqual(list(Language.objects.filter(is_active=True).values_list("code", flat=True)), ["en"])
        self.assertEqual(self.client.get("/nl/").status_code, 404)

    def test_landing_labels_are_editable(self):
        TextKey.objects.update_or_create(key="DISCUSS_PROJECT", defaults={"default_text": "Plan your solar project"})
        response = self.client.get(reverse("website:home"))
        self.assertContains(response, "Plan your solar project")
        self.assertContains(response, 'property="og:locale" content="en_GB"')

    def test_hidden_about_has_no_navigation_link(self):
        settings = SiteSettings.load()
        settings.about_enabled = False
        settings.save()
        response = self.client.get(reverse("website:home"))
        self.assertNotContains(response, 'href="/#about"')

    def test_hidden_project_returns_404(self):
        page = Page.objects.get(kind=Page.PROJECT, slug="solar-parks")
        page.is_active = False
        page.save(update_fields=("is_active",))
        response = self.client.get(page.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_unsafe_saved_colours_have_readable_rendering(self):
        settings = SiteSettings.load()
        settings.secondary_colour = '#f8ba4f'
        settings.surface_colour = '#000000'
        settings.save()
        response = self.client.get(reverse('website:home'))
        self.assertContains(response, '--black:#080909')
        self.assertContains(response, '--light:#FFFFFF')
        settings.refresh_from_db()
        self.assertEqual(settings.secondary_colour, '#f8ba4f')

    def test_palette_retains_safe_brand_colours(self):
        settings = SiteSettings(primary_colour='#FFC107', secondary_colour='#171817', surface_colour='#FFFFFF')
        self.assertEqual(settings.accessible_palette, {'primary': '#FFC107', 'dark': '#171817', 'surface': '#FFFFFF'})

    def test_chatbot_is_inert_until_opened(self):
        response = self.client.get(reverse('website:home'))
        self.assertContains(response, 'aria-hidden="true" inert')

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

    def test_project_crud_updates_public_site_without_build(self):
        user = get_user_model().objects.create_superuser('project-editor', 'editor@example.com', 'test-password')
        self.client.force_login(user)
        title = TextKey.objects.create(key='TEST_NEW_PROJECT', default_text='New solar project test')
        response = self.client.post(reverse('cms-resource-list', kwargs={'resource': 'pages'}),
            data={'kind': Page.PROJECT, 'slug': 'test-new-project', 'title_key': title.pk}, content_type='application/json')
        self.assertEqual(response.status_code, 201, response.content)
        pk = response.json()['item']['id']
        endpoint = reverse('cms-resource-detail', kwargs={'resource': 'pages', 'pk': pk})
        page_url = Page.objects.get(pk=pk).get_absolute_url()
        self.assertContains(self.client.get('/'), 'New solar project test')
        self.assertContains(self.client.get(reverse('website:sitemap')), page_url)
        for visible in (False, True):
            self.assertEqual(self.client.patch(endpoint, data={'is_active': visible}, content_type='application/json').status_code, 200)
            self.assertEqual(self.client.get(page_url).status_code, 200 if visible else 404)
            if visible:
                self.assertContains(self.client.get('/'), 'New solar project test')
            else:
                self.assertNotContains(self.client.get('/'), 'New solar project test')
                self.assertNotContains(self.client.get(reverse('website:sitemap')), page_url)
        self.assertEqual(self.client.delete(endpoint).status_code, 200)
        self.assertNotContains(self.client.get('/'), 'New solar project test')
        self.assertEqual(self.client.get(page_url).status_code, 404)

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
        self.assertEqual(schema["chatbot_enabled"]["type"], "boolean")
        self.assertEqual(schema["chatbot_title"]["type"], "text")

    def test_chatbot_can_be_hidden_from_site_settings(self):
        settings = SiteSettings.load()
        settings.chatbot_enabled = False
        settings.save(update_fields=("chatbot_enabled", "updated_at"))
        self.assertNotContains(self.client.get(reverse("website:home")), "data-chatbot")

    def test_site_settings_is_singleton(self):
        self.assertEqual(SiteSettings.load().pk, 1)
        self.assertEqual(SiteSettings.objects.count(), 1)

    def login_editor(self):
        user = get_user_model().objects.create_superuser('workflow-editor', 'workflow@example.com', 'test-password')
        self.client.force_login(user)

    def test_editor_exposes_wording_instead_of_internal_text_relations(self):
        self.login_editor()
        page = Page.objects.first()
        response = self.client.get(reverse('cms-resource-detail', kwargs={'resource': 'pages', 'pk': page.pk})).json()
        schema = {field['name']: field for field in response['schema']}
        self.assertIn('title_key_text', schema)
        self.assertNotIn('title_key', schema)
        self.assertEqual(response['item']['fields']['title_key_text'], page.title_key.default_text)

    def test_direct_wording_edit_preserves_other_owners_of_shared_text(self):
        self.login_editor()
        page = Page.objects.first()
        shared = page.title_key
        other = Page.objects.exclude(pk=page.pk).first()
        other.title_key = shared
        other.save()
        endpoint = reverse('cms-resource-detail', kwargs={'resource': 'pages', 'pk': page.pk})
        response = self.client.patch(endpoint, {'title_key_text': 'Updated page wording'}, content_type='application/json')
        self.assertEqual(response.status_code, 200, response.content)
        page.refresh_from_db(); other.refresh_from_db(); shared.refresh_from_db()
        self.assertEqual(page.title_key.default_text, 'Updated page wording')
        self.assertEqual(other.title_key_id, shared.pk)
        self.assertNotEqual(shared.default_text, 'Updated page wording')
        self.assertContains(self.client.get(page.get_absolute_url()), 'Updated page wording')

    def test_new_page_can_be_created_without_a_text_identifier(self):
        self.login_editor()
        response = self.client.post(reverse('cms-resource-list', kwargs={'resource': 'pages'}),
            {'kind': 'project', 'slug': 'direct-wording', 'title_key_text': 'A new project'}, content_type='application/json')
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(Page.objects.get(slug='direct-wording').title_key.default_text, 'A new project')

    def test_project_and_section_can_be_created_from_their_names(self):
        from .models import PageSection
        self.login_editor()
        endpoint = reverse('cms-resource-list', kwargs={'resource': 'pages'})
        payload = {'kind':'project', 'title_key_text':'New solar project'}
        first = self.client.post(endpoint, payload, content_type='application/json')
        second = self.client.post(endpoint, payload, content_type='application/json')
        self.assertEqual(first.status_code, 201, first.content)
        self.assertEqual(second.status_code, 201, second.content)
        project = Page.objects.get(pk=first.json()['item']['id'])
        other = Page.objects.get(pk=second.json()['item']['id'])
        self.assertEqual(project.slug, 'new-solar-project')
        self.assertEqual(other.slug, 'new-solar-project-2')
        response = self.client.post(reverse('cms-resource-list', kwargs={'resource':'sections'}),
            {'page':project.pk,'title_key_text':'Project overview','body_key_text':'Details of the solar project.'}, content_type='application/json')
        self.assertEqual(response.status_code, 201, response.content)
        section = PageSection.objects.get(pk=response.json()['item']['id'])
        self.assertEqual(section.page_id, project.pk)
        self.assertEqual(section.admin_name, 'Project overview')
        self.assertContains(self.client.get(project.get_absolute_url()), 'Details of the solar project.')

    def test_invalid_page_rolls_back_generated_wording(self):
        self.login_editor()
        page = Page.objects.first()
        before = TextKey.objects.count()
        response = self.client.patch(reverse('cms-resource-detail', kwargs={'resource': 'pages', 'pk': page.pk}),
            {'title_key_text': 'Must not be saved', 'slug': 'not a valid slug'}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(TextKey.objects.count(), before)
        page.refresh_from_db()
        self.assertNotEqual(page.title_key.default_text, 'Must not be saved')

    def test_blank_required_wording_has_a_visible_editor_error(self):
        self.login_editor()
        page = Page.objects.first()
        response = self.client.patch(reverse('cms-resource-detail', kwargs={'resource': 'pages', 'pk': page.pk}),
            {'title_key_text': ''}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('title_key_text', response.json()['errors'])

    def test_page_and_child_lists_are_scoped_to_the_selected_owner(self):
        from .models import HomeFeature, PageSection, SectionItem
        self.login_editor()
        listing = lambda resource, filters: self.client.get(reverse('cms-resource-list', kwargs={'resource': resource}), filters).json()['items']
        services = listing('pages', {'kind': 'service'})
        self.assertTrue(services)
        self.assertTrue(all(item['fields']['kind'] == 'service' for item in services))
        section = PageSection.objects.first()
        sections = listing('sections', {'page': section.page_id})
        self.assertTrue(sections)
        self.assertTrue(all(item['fields']['page'] == section.page_id for item in sections))
        item = SectionItem.objects.first()
        paragraphs = listing('section-items', {'section': item.section_id})
        self.assertTrue(paragraphs)
        self.assertTrue(all(row['fields']['section'] == item.section_id for row in paragraphs))
        feature = HomeFeature.objects.first()
        features = listing('home-features', {'block': feature.block_id})
        self.assertTrue(features)
        self.assertTrue(all(row['fields']['block'] == feature.block_id for row in features))
        invalid = self.client.get(reverse('cms-resource-list', kwargs={'resource': 'sections'}), {'page': 'invalid'})
        self.assertEqual(invalid.status_code, 400)
