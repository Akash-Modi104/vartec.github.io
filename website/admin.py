from django.contrib import admin
from django.utils.html import format_html

from .models import (
    ContactSubmission,
    HeroSlide,
    HomeBlock,
    HomeFeature,
    Language,
    MediaAsset,
    Page,
    PageSection,
    SectionItem,
    SiteSettings,
    TextKey,
    TextTranslation,
)


class TextTranslationInline(admin.StackedInline):
    model = TextTranslation
    extra = 0
    autocomplete_fields = ("language",)


@admin.register(TextKey)
class TextKeyAdmin(admin.ModelAdmin):
    list_display = ("key", "short_default", "translation_count", "updated_at")
    search_fields = ("key", "default_text", "translations__value")
    readonly_fields = ("updated_at",)
    inlines = (TextTranslationInline,)

    @admin.display(description="Default text")
    def short_default(self, obj):
        return obj.default_text[:100]

    @admin.display(description="Translations")
    def translation_count(self, obj):
        return obj.translations.count()


@admin.register(TextTranslation)
class TextTranslationAdmin(admin.ModelAdmin):
    list_display = ("text_key", "language", "short_value", "updated_at")
    list_filter = ("language",)
    search_fields = ("text_key__key", "value")
    autocomplete_fields = ("text_key", "language")

    @admin.display(description="Text")
    def short_value(self, obj):
        return obj.value[:110]


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("native_name", "code", "is_default", "is_active", "sort_order")
    list_editable = ("is_default", "is_active", "sort_order")
    search_fields = ("name", "native_name", "code")


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "preview", "is_active", "sort_order")
    list_filter = ("kind", "is_active")
    list_editable = ("is_active", "sort_order")
    search_fields = ("title", "legacy_path")
    autocomplete_fields = ("alt_text_key",)

    @admin.display(description="Preview")
    def preview(self, obj):
        if obj.kind == MediaAsset.IMAGE and obj.url:
            return format_html('<img src="{}" alt="" style="width:72px;height:48px;object-fit:cover;border-radius:4px">', obj.url)
        return "—"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Brand", {"fields": ("brand_name", "logo", "legacy_logo_path", "primary_colour")}),
        ("Contact", {"fields": ("contact_email", "uk_phone", "nl_phone", "notification_email")}),
        ("Homepage features", {"fields": ("hero_enabled", "about_enabled", "services_enabled", "projects_enabled", "contact_enabled", "footer_enabled", "video_enabled", "video", "legacy_video_path")}),
        ("SEO", {"fields": ("default_seo_title", "default_seo_description", "organisation_schema_enabled")}),
        ("System", {"fields": ("updated_at",)}),
    )
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class PageSectionInline(admin.TabularInline):
    model = PageSection
    extra = 0
    fields = ("admin_name", "title_key", "layout", "background", "is_active", "sort_order")
    autocomplete_fields = ("title_key",)
    show_change_link = True


@admin.action(description="Publish/show selected pages")
def show_pages(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Hide selected pages")
def hide_pages(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "slug", "is_active", "show_in_navigation", "show_on_homepage", "sort_order", "updated_at")
    list_filter = ("kind", "is_active", "show_in_navigation", "show_on_homepage")
    list_editable = ("is_active", "show_in_navigation", "show_on_homepage", "sort_order")
    search_fields = ("slug", "title_key__key", "title_key__default_text", "intro_key__default_text")
    autocomplete_fields = ("title_key", "intro_key", "seo_title_key", "seo_description_key", "card_media")
    inlines = (PageSectionInline,)
    actions = (show_pages, hide_pages)

    @admin.display(ordering="title_key__default_text")
    def title(self, obj):
        return obj.title_key.default_text


class SectionItemInline(admin.TabularInline):
    model = SectionItem
    extra = 0
    autocomplete_fields = ("text_key",)


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ("admin_name", "page", "layout", "background", "is_active", "sort_order")
    list_filter = ("page__kind", "background", "layout", "is_active")
    list_editable = ("is_active", "sort_order")
    search_fields = ("admin_name", "page__title_key__default_text", "title_key__default_text")
    autocomplete_fields = ("page", "title_key", "body_key", "media")
    inlines = (SectionItemInline,)


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("title", "preview", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    autocomplete_fields = ("media", "alt_text_key")

    @admin.display(description="Preview")
    def preview(self, obj):
        return format_html('<img src="{}" alt="" style="width:96px;height:54px;object-fit:cover;border-radius:4px">', obj.image_url) if obj.image_url else "—"


class HomeFeatureInline(admin.TabularInline):
    model = HomeFeature
    extra = 0
    autocomplete_fields = ("title_key", "body_key", "media")


@admin.register(HomeBlock)
class HomeBlockAdmin(admin.ModelAdmin):
    list_display = ("admin_name", "title_key", "background", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    list_filter = ("background", "is_active")
    search_fields = ("admin_name", "title_key__default_text", "intro_key__default_text")
    autocomplete_fields = ("title_key", "intro_key")
    inlines = (HomeFeatureInline,)


@admin.register(SectionItem)
class SectionItemAdmin(admin.ModelAdmin):
    list_display = ("text_key", "section", "item_type", "is_active", "sort_order")
    list_filter = ("item_type", "is_active", "section__page__kind")
    list_editable = ("is_active", "sort_order")
    search_fields = ("text_key__key", "text_key__default_text", "section__admin_name")
    autocomplete_fields = ("section", "text_key")


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "status", "email_sent", "created_at")
    list_filter = ("status", "email_sent", "language_code", "created_at")
    list_editable = ("status",)
    search_fields = ("first_name", "last_name", "email", "phone", "message")
    readonly_fields = ("first_name", "last_name", "email", "phone", "message", "language_code", "email_sent", "created_at", "updated_at")
    date_hierarchy = "created_at"

    @admin.display(description="Name")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def has_add_permission(self, request):
        return False
