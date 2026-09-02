from django.conf import settings as django_settings
from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.static import serve

from .forms import ContactForm
from .models import HeroSlide, Page, SiteSettings
from .services import active_language, base_context, localized_home_blocks, localized_pages, localize_page, send_contact_notification, text_map


def cms_shell(request, path=""):
    """Return the Angular CMS shell; Angular handles client-side admin routes."""
    index_path = django_settings.BASE_DIR / "static" / "cms" / "index.html"
    if not index_path.exists():
        return HttpResponse("Angular CMS build is not available. Run npm run build:admin.", status=503)
    response = FileResponse(index_path.open("rb"), content_type="text/html")
    response["Cache-Control"] = "no-store"
    return response


def _language_or_404():
    language = active_language()
    if not language:
        raise Http404("No active language is configured")
    return language


def _process_contact(request, language):
    if request.method != "POST":
        request.contact_form = ContactForm()
        return None
    form = ContactForm(request.POST)
    request.contact_form = form
    if not form.is_valid():
        return None
    submission = form.save(commit=False)
    submission.language_code = language.code
    submission.save()
    send_contact_notification(submission, SiteSettings.load())
    messages.success(request, text_map(language).get("CONTACT_SUCCESS", "Thank you. Your message has been received."))
    return submission


def _redirect_with_anchor(request):
    return redirect(f"{request.path}?sent=1#contact")


@require_http_methods(["GET", "POST"])
def home(request):
    language = _language_or_404()
    if _process_contact(request, language):
        return _redirect_with_anchor(request)
    context = base_context(request, language)
    slides = list(HeroSlide.objects.filter(is_active=True).select_related("media", "alt_text_key").order_by("sort_order", "pk"))
    for slide in slides:
        slide.localized_alt = slide.alt_text_key.default_text if slide.alt_text_key else slide.title
    context.update(
        {
            "hero_slides": slides,
            "services": localized_pages(Page.SERVICE, language, homepage_only=True),
            "projects": localized_pages(Page.PROJECT, language, homepage_only=True),
            "home_blocks": localized_home_blocks(language),
            "seo_title": context["site_settings"].default_seo_title,
            "seo_description": context["site_settings"].default_seo_description,
            "canonical_url": request.build_absolute_uri(reverse("website:home")),
        }
    )
    return render(request, "website/home.html", context)


@require_http_methods(["GET", "POST"])
def page_detail(request, kind, slug):
    language = _language_or_404()
    page = get_object_or_404(Page.objects.select_related("title_key", "intro_key", "seo_title_key", "seo_description_key", "card_media"), kind=kind, slug=slug, is_active=True)
    page = localize_page(page, language)
    if _process_contact(request, language):
        return _redirect_with_anchor(request)
    context = base_context(request, language, page)
    context.update(
        {
            "page": page,
            "seo_title": page.localized_seo_title,
            "seo_description": page.localized_seo_description,
            "canonical_url": request.build_absolute_uri(page.get_absolute_url()),
        }
    )
    return render(request, "website/page_detail.html", context)


def robots(request):
    sitemap_url = request.build_absolute_uri(reverse("website:sitemap"))
    return HttpResponse(f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /django-admin/\nDisallow: /cms-api/\nSitemap: {sitemap_url}\n", content_type="text/plain")


def sitemap(request):
    pages = Page.objects.filter(is_active=True).select_related("title_key")
    urls = [{"location": request.build_absolute_uri(reverse("website:home")), "modified": None}]
    for page in pages:
        urls.append({"location": request.build_absolute_uri(page.get_absolute_url()), "modified": page.updated_at})
    return render(request, "website/sitemap.xml", {"urls": urls}, content_type="application/xml")


def media_file(request, path):
    """Serve administrator uploads from the configured persistent media volume."""
    response = serve(request, path, document_root=django_settings.MEDIA_ROOT)
    response["Cache-Control"] = "public, max-age=86400"
    return response
