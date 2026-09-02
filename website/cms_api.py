import json
from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import models, transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils.dateparse import parse_date, parse_datetime
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import ContactSubmission, HeroSlide, HomeBlock, HomeFeature, MediaAsset, Page, PageSection, SectionItem, SiteSettings, TextKey


RESOURCE_SPECS = {
    "pages": {"model": Page, "label": "Page", "plural": "Pages", "group": "Website", "description": "Services, projects and standard pages shown on the website.", "fields": ("kind", "slug", "title_key", "intro_key", "seo_title_key", "seo_description_key", "card_media", "card_image", "legacy_card_image_path", "show_on_homepage", "show_in_navigation", "published_at", "is_active", "sort_order"), "list_fields": ("kind", "slug", "title_key", "show_on_homepage", "show_in_navigation", "is_active", "updated_at"), "search_fields": ("slug", "title_key__default_text", "intro_key__default_text")},
    "sections": {"model": PageSection, "label": "Page section", "plural": "Page sections", "group": "Website", "description": "Reorder and redesign the content sections within any page.", "fields": ("page", "admin_name", "title_key", "body_key", "layout", "background", "media", "image", "legacy_image_path", "video", "legacy_video_path", "is_active", "sort_order"), "list_fields": ("page", "admin_name", "layout", "background", "is_active", "sort_order"), "search_fields": ("admin_name", "page__slug")},
    "section-items": {"model": SectionItem, "label": "Section item", "plural": "Section items", "group": "Website", "description": "Paragraphs, bullets, numbered items and subheadings inside page sections.", "fields": ("section", "text_key", "item_type", "is_active", "sort_order"), "list_fields": ("section", "text_key", "item_type", "is_active", "sort_order"), "search_fields": ("section__admin_name", "text_key__key", "text_key__default_text")},
    "hero-slides": {"model": HeroSlide, "label": "Hero slide", "plural": "Hero slides", "group": "Homepage", "description": "Homepage hero imagery, alternative text and display order.", "fields": ("title", "media", "image", "legacy_image_path", "alt_text_key", "is_active", "sort_order"), "list_fields": ("title", "media", "is_active", "sort_order"), "search_fields": ("title",)},
    "home-blocks": {"model": HomeBlock, "label": "Homepage block", "plural": "Homepage blocks", "group": "Homepage", "description": "Homepage content blocks, themes and their order.", "fields": ("admin_name", "title_key", "intro_key", "background", "is_active", "sort_order"), "list_fields": ("admin_name", "title_key", "background", "is_active", "sort_order"), "search_fields": ("admin_name", "title_key__default_text")},
    "home-features": {"model": HomeFeature, "label": "Homepage feature", "plural": "Homepage features", "group": "Homepage", "description": "Feature cards belonging to homepage content blocks.", "fields": ("block", "title_key", "body_key", "media", "is_active", "sort_order"), "list_fields": ("block", "title_key", "media", "is_active", "sort_order"), "search_fields": ("block__admin_name", "title_key__default_text")},
    "text": {"model": TextKey, "label": "Text entry", "plural": "Website text", "group": "Content", "description": "Edit the English wording used throughout the website.", "fields": ("key", "default_text", "description"), "list_fields": ("key", "default_text", "description", "updated_at"), "search_fields": ("key", "default_text", "description")},
    "media": {"model": MediaAsset, "label": "Media asset", "plural": "Media library", "group": "Assets", "description": "Upload and organise images, videos and documents.", "fields": ("title", "kind", "file", "legacy_path", "alt_text_key", "is_active", "sort_order"), "list_fields": ("title", "kind", "file", "is_active", "sort_order", "created_at"), "search_fields": ("title", "legacy_path", "alt_text_key__default_text")},
    "settings": {"model": SiteSettings, "label": "Appearance & settings", "plural": "Appearance & settings", "group": "Manage", "description": "Choose the logo colours, website font, contact details, visibility and SEO defaults.", "fields": ("brand_name", "logo", "legacy_logo_path", "primary_colour", "secondary_colour", "surface_colour", "font_family", "contact_email", "uk_phone", "notification_email", "hero_enabled", "about_enabled", "services_enabled", "projects_enabled", "contact_enabled", "footer_enabled", "video_enabled", "video", "legacy_video_path", "default_seo_title", "default_seo_description", "organisation_schema_enabled"), "list_fields": ("brand_name", "font_family", "primary_colour", "updated_at"), "search_fields": ("brand_name", "contact_email"), "singleton": True},
    "enquiries": {"model": ContactSubmission, "label": "Enquiry", "plural": "Enquiries", "group": "Inbox", "description": "Customer messages, follow-up status and private internal notes.", "fields": ("first_name", "last_name", "email", "phone", "message", "status", "email_sent", "internal_notes"), "readonly": ("first_name", "last_name", "email", "phone", "message", "email_sent"), "list_fields": ("first_name", "last_name", "email", "status", "created_at"), "search_fields": ("first_name", "last_name", "email", "phone", "message")},
}


def _staff_api(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication required."}, status=401)
        if not request.user.is_staff:
            return JsonResponse({"detail": "Administrator access required."}, status=403)
        return view(request, *args, **kwargs)
    return wrapped


def _json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None


def _resource_payload(key, spec):
    return {"key": key, "label": spec["label"], "plural": spec["plural"], "group": spec["group"], "description": spec["description"], "singleton": spec.get("singleton", False)}


def _field_type(field):
    if isinstance(field, models.ForeignKey): return "relation"
    if isinstance(field, models.FileField): return "file"
    if isinstance(field, models.BooleanField): return "boolean"
    if isinstance(field, (models.PositiveIntegerField, models.IntegerField)): return "number"
    if isinstance(field, models.DateTimeField): return "datetime"
    if isinstance(field, models.DateField): return "date"
    if isinstance(field, models.EmailField): return "email"
    if isinstance(field, models.TextField): return "textarea"
    if field.name.endswith("colour"): return "color"
    if field.choices: return "select"
    return "text"


def _field_schema(spec, field_name):
    field = spec["model"]._meta.get_field(field_name)
    schema = {"name": field.name, "label": str(field.verbose_name).replace("_", " ").title(), "type": _field_type(field), "required": not field.blank and not field.null and not isinstance(field, models.BooleanField), "readonly": field.name in spec.get("readonly", ()) or not field.editable, "help": str(field.help_text or "")}
    if field.choices:
        schema["options"] = [{"value": value, "label": str(label)} for value, label in field.choices]
    elif isinstance(field, models.ForeignKey):
        schema["options"] = [{"value": item.pk, "label": str(item)} for item in field.remote_field.model._default_manager.all()[:1500]]
    if isinstance(field, models.FileField):
        schema["accept"] = "image/*" if "image" in field.name or field.name in {"logo", "flag"} else ""
    return schema


def _raw_value(obj, field):
    value = getattr(obj, field.name)
    if isinstance(field, models.ForeignKey): return getattr(obj, f"{field.name}_id")
    if isinstance(field, models.FileField):
        if not value: return ""
        try: return {"name": value.name, "url": value.url}
        except ValueError: return {"name": value.name, "url": ""}
    if isinstance(field, (models.DateTimeField, models.DateField)): return value.isoformat() if value else None
    return value


def _display_value(obj, field):
    value = getattr(obj, field.name)
    if isinstance(field, models.ForeignKey): return str(value) if value else "—"
    if isinstance(field, models.FileField): return value.name.rsplit("/", 1)[-1] if value else "—"
    if field.choices and value not in (None, ""): return str(getattr(obj, f"get_{field.name}_display")())
    if isinstance(field, models.BooleanField): return "Yes" if value else "No"
    if isinstance(field, models.DateTimeField): return value.strftime("%d %b %Y, %H:%M") if value else "—"
    if isinstance(field, models.DateField): return value.strftime("%d %b %Y") if value else "—"
    return str(value) if value not in (None, "") else "—"


def _preview_details(obj):
    if isinstance(obj, MediaAsset):
        return obj.url, obj.kind
    if isinstance(obj, Page):
        return obj.card_image_url, MediaAsset.IMAGE
    if isinstance(obj, PageSection):
        if obj.media:
            return obj.media.url, obj.media.kind
        if obj.media_url:
            return obj.media_url, MediaAsset.IMAGE
        if obj.video_url:
            return obj.video_url, MediaAsset.VIDEO
    if isinstance(obj, HeroSlide):
        return obj.image_url, MediaAsset.IMAGE
    if isinstance(obj, HomeFeature) and obj.media:
        return obj.media.url, obj.media.kind
    if isinstance(obj, SiteSettings):
        return obj.logo_url, MediaAsset.IMAGE
    return "", ""


def _serialize_item(obj, spec):
    fields, cells = {}, {}
    for field_name in set(spec["fields"]) | set(spec["list_fields"]):
        field = obj._meta.get_field(field_name)
        fields[field_name] = _raw_value(obj, field)
        cells[field_name] = _display_value(obj, field)
    preview, preview_type = _preview_details(obj)
    return {"id": obj.pk, "display": str(obj), "fields": fields, "cells": cells, "preview": preview, "previewType": preview_type}


def _coerce_value(field, value):
    if isinstance(field, models.ForeignKey): return None if value in (None, "", "null") else int(value)
    if isinstance(field, models.BooleanField): return value is True or str(value).lower() in {"1", "true", "yes", "on"}
    if isinstance(field, (models.PositiveIntegerField, models.IntegerField)): return None if value in (None, "") and field.null else int(value or 0)
    if isinstance(field, models.DateTimeField): return parse_datetime(value) if value else None
    if isinstance(field, models.DateField): return parse_date(value) if value else None
    return value


def _save_object(request, spec, obj=None):
    multipart = request.content_type and request.content_type.startswith("multipart/form-data")
    payload = request.POST.dict() if multipart else _json_body(request)
    if payload is None: return None, JsonResponse({"detail": "Invalid JSON request."}, status=400)
    obj = obj or spec["model"]()
    for field_name in spec["fields"]:
        if field_name in spec.get("readonly", ()): continue
        field = obj._meta.get_field(field_name)
        if isinstance(field, models.FileField):
            if field_name in request.FILES: setattr(obj, field_name, request.FILES[field_name])
            elif str(payload.get(f"clear_{field_name}", "")).lower() == "true": setattr(obj, field_name, "")
            continue
        if field_name not in payload: continue
        value = _coerce_value(field, payload[field_name])
        if isinstance(field, models.ForeignKey): setattr(obj, f"{field_name}_id", value)
        else: setattr(obj, field_name, value)
    try:
        with transaction.atomic():
            obj.full_clean()
            obj.save()
    except ValidationError as exc:
        errors = getattr(exc, "message_dict", {"__all__": exc.messages})
        return None, JsonResponse({"detail": "Please correct the highlighted fields.", "errors": errors}, status=400)
    return obj, None


@ensure_csrf_cookie
@require_GET
def session_view(request):
    token = get_token(request)
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({"authenticated": False, "csrfToken": token})
    return JsonResponse({"authenticated": True, "csrfToken": token, "user": {"id": request.user.pk, "username": request.user.get_username(), "name": request.user.get_full_name() or request.user.get_username()}})


@require_POST
def login_view(request):
    payload = _json_body(request)
    if payload is None: return JsonResponse({"detail": "Invalid request."}, status=400)
    user = authenticate(request, username=payload.get("username", ""), password=payload.get("password", ""))
    if user is None or not user.is_staff: return JsonResponse({"detail": "The username or password is incorrect."}, status=400)
    login(request, user)
    return JsonResponse({"authenticated": True, "user": {"id": user.pk, "username": user.get_username(), "name": user.get_full_name() or user.get_username()}})


@require_POST
@_staff_api
def logout_view(request):
    logout(request)
    return JsonResponse({"authenticated": False})


@require_GET
@_staff_api
def dashboard_view(request):
    resources = []
    for key, spec in RESOURCE_SPECS.items():
        queryset = spec["model"]._default_manager.all()
        item = _resource_payload(key, spec)
        item["count"] = queryset.count()
        if any(field.name == "is_active" for field in spec["model"]._meta.fields): item["activeCount"] = queryset.filter(is_active=True).count()
        resources.append(item)
    recent = ContactSubmission.objects.order_by("-created_at")[:6]
    return JsonResponse({"resources": resources, "summary": {"pages": Page.objects.count(), "activePages": Page.objects.filter(is_active=True).count(), "sections": PageSection.objects.filter(is_active=True).count(), "media": MediaAsset.objects.count(), "newEnquiries": ContactSubmission.objects.filter(status=ContactSubmission.NEW).count()}, "recentEnquiries": [_serialize_item(item, RESOURCE_SPECS["enquiries"]) for item in recent]})


@require_http_methods(["GET", "POST"])
@_staff_api
def resource_list(request, resource):
    spec = RESOURCE_SPECS.get(resource)
    if not spec: return JsonResponse({"detail": "Unknown content type."}, status=404)
    if request.method == "POST":
        obj, error = _save_object(request, spec)
        if error: return error
        return JsonResponse({"item": _serialize_item(obj, spec)}, status=201)
    queryset = spec["model"]._default_manager.all()
    query = request.GET.get("q", "").strip()
    if query and spec.get("search_fields"):
        filters = Q()
        for field_name in spec["search_fields"]: filters |= Q(**{f"{field_name}__icontains": query})
        queryset = queryset.filter(filters).distinct()
    if not queryset.ordered:
        queryset = queryset.order_by("pk")
    page_number = max(int(request.GET.get("page", "1") or 1), 1)
    page_size = min(max(int(request.GET.get("pageSize", "50") or 50), 1), 200)
    paginator = Paginator(queryset, page_size)
    page = paginator.get_page(page_number)
    return JsonResponse({"resource": _resource_payload(resource, spec), "schema": [_field_schema(spec, name) for name in spec["fields"]], "listFields": [{"name": name, "label": str(spec["model"]._meta.get_field(name).verbose_name).replace("_", " ").title()} for name in spec["list_fields"]], "items": [_serialize_item(item, spec) for item in page.object_list], "pagination": {"page": page.number, "pages": paginator.num_pages, "total": paginator.count, "pageSize": page_size}})


@require_http_methods(["GET", "PATCH", "POST", "DELETE"])
@_staff_api
def resource_detail(request, resource, pk):
    spec = RESOURCE_SPECS.get(resource)
    if not spec: return JsonResponse({"detail": "Unknown content type."}, status=404)
    try: obj = spec["model"]._default_manager.get(pk=pk)
    except spec["model"].DoesNotExist: return JsonResponse({"detail": "Item not found."}, status=404)
    if request.method == "GET": return JsonResponse({"resource": _resource_payload(resource, spec), "schema": [_field_schema(spec, name) for name in spec["fields"]], "item": _serialize_item(obj, spec)})
    if request.method == "DELETE":
        if spec.get("singleton"): return JsonResponse({"detail": "Global settings cannot be deleted."}, status=400)
        try: obj.delete()
        except ProtectedError: return JsonResponse({"detail": "This item is still used elsewhere. Hide it or remove those links first."}, status=409)
        return JsonResponse({"deleted": True})
    obj, error = _save_object(request, spec, obj)
    if error: return error
    return JsonResponse({"item": _serialize_item(obj, spec)})
