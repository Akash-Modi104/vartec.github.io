from django.core.mail import send_mail
from django.db.models import Prefetch

from .models import HomeBlock, HomeFeature, Language, Page, PageSection, SectionItem, SiteSettings, TextKey


def active_language():
    return Language.objects.filter(code="en", is_active=True).first()


def text_map(language):
    return {item.key: item.default_text for item in TextKey.objects.all()}


def localized_pages(kind, language, homepage_only=False, navigation_only=False):
    items = Page.objects.filter(kind=kind, is_active=True).select_related("title_key", "intro_key", "seo_title_key", "seo_description_key", "card_media")
    if homepage_only:
        items = items.filter(show_on_homepage=True)
    if navigation_only:
        items = items.filter(show_in_navigation=True)
    pages = list(items.order_by("sort_order", "pk"))
    for page in pages:
        localize_page(page, language, include_sections=False)
    return pages


def localize_page(page, language, include_sections=True):
    page.localized_title = page.title_key.default_text
    page.localized_intro = page.intro_key.default_text if page.intro_key else ""
    page.localized_seo_title = page.seo_title_key.default_text if page.seo_title_key else f"{page.localized_title} | VARTEC"
    page.localized_seo_description = page.seo_description_key.default_text if page.seo_description_key else page.localized_intro
    if include_sections:
        sections = list(
            page.sections.filter(is_active=True)
            .select_related("title_key", "body_key", "media")
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=SectionItem.objects.filter(is_active=True).select_related("text_key").order_by("sort_order", "pk"),
                )
            )
            .order_by("sort_order", "pk")
        )
        for section in sections:
            section.localized_title = section.title_key.default_text if section.title_key else ""
            section.localized_body = section.body_key.default_text if section.body_key else ""
            section.localized_items = list(section.items.all())
            for item in section.localized_items:
                item.localized_text = item.text_key.default_text
        page.localized_sections = sections
    return page


def localized_home_blocks(language):
    blocks = list(
        HomeBlock.objects.filter(is_active=True)
        .select_related("title_key", "intro_key")
        .prefetch_related(
            Prefetch(
                "features",
                queryset=HomeFeature.objects.filter(is_active=True)
                .select_related("title_key", "body_key", "media")
                .order_by("sort_order", "pk"),
            )
        )
        .order_by("sort_order", "pk")
    )
    for block in blocks:
        block.localized_title = block.title_key.default_text
        block.localized_intro = block.intro_key.default_text if block.intro_key else ""
        block.localized_features = list(block.features.all())
        for feature in block.localized_features:
            feature.localized_title = feature.title_key.default_text
            feature.localized_body = feature.body_key.default_text
    return blocks


def send_contact_notification(submission, settings):
    recipient = settings.notification_email or settings.contact_email
    if not recipient:
        return False
    body = (
        f"New website enquiry from {submission.first_name} {submission.last_name}\n\n"
        f"Email: {submission.email}\nPhone: {submission.phone}\n\n"
        f"Message:\n{submission.message}"
    )
    sent = send_mail(
        subject=f"VARTEC website enquiry from {submission.first_name} {submission.last_name}",
        message=body,
        from_email=None,
        recipient_list=[recipient],
        fail_silently=True,
    )
    submission.email_sent = bool(sent)
    submission.save(update_fields=("email_sent", "updated_at"))
    return bool(sent)


def base_context(request, language, page=None):
    settings = SiteSettings.load()
    return {
        "site_settings": settings,
        "language": language,
        "texts": text_map(language),
        "navigation_services": localized_pages(Page.SERVICE, language, navigation_only=True),
        "navigation_projects": localized_pages(Page.PROJECT, language, navigation_only=True),
        "contact_form": getattr(request, "contact_form", None),
    }
