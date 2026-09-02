from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.templatetags.static import static
from django.urls import reverse


class OrderedActiveModel(models.Model):
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        abstract = True


class Language(OrderedActiveModel):
    code = models.CharField(
        max_length=12,
        unique=True,
        validators=[RegexValidator(r"^[a-z]{2,3}(?:-[A-Z]{2})?$", "Use a code such as en, nl, or en-GB.")],
    )
    name = models.CharField(max_length=80)
    native_name = models.CharField(max_length=80)
    is_default = models.BooleanField(default=False)
    flag = models.FileField(upload_to="languages/flags/", blank=True)
    legacy_flag_path = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ("sort_order", "name")

    def __str__(self):
        return f"{self.native_name} ({self.code})"

    @property
    def flag_url(self):
        if self.flag:
            return self.flag.url
        return static(self.legacy_flag_path) if self.legacy_flag_path else ""

    def save(self, *args, **kwargs):
        if self.is_default:
            Language.objects.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class TextKey(models.Model):
    key = models.CharField(
        max_length=120,
        unique=True,
        validators=[RegexValidator(r"^[A-Z0-9_]+$", "Use uppercase letters, numbers, and underscores.")],
    )
    default_text = models.TextField()
    description = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("key",)

    def __str__(self):
        return self.key

    def translated(self, language):
        if not language:
            return self.default_text
        cached = getattr(self, "_prefetched_objects_cache", {}).get("translations")
        if cached is not None:
            match = next((item for item in cached if item.language_id == language.pk), None)
            return match.value if match and match.value else self.default_text
        translation = self.translations.filter(language=language).first()
        return translation.value if translation and translation.value else self.default_text


class TextTranslation(models.Model):
    text_key = models.ForeignKey(TextKey, on_delete=models.CASCADE, related_name="translations")
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="translations")
    value = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("language__sort_order", "language__code")
        constraints = [models.UniqueConstraint(fields=("text_key", "language"), name="unique_text_translation")]

    def __str__(self):
        return f"{self.text_key.key} – {self.language.code}"


class MediaAsset(OrderedActiveModel):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    KIND_CHOICES = ((IMAGE, "Image"), (VIDEO, "Video"), (DOCUMENT, "Document"))

    title = models.CharField(max_length=180)
    kind = models.CharField(max_length=12, choices=KIND_CHOICES, default=IMAGE)
    file = models.FileField(upload_to="website/assets/", blank=True)
    legacy_path = models.CharField(max_length=300, blank=True, help_text="Existing path inside src/assets.")
    alt_text_key = models.ForeignKey(TextKey, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("sort_order", "title")

    def __str__(self):
        return self.title

    @property
    def url(self):
        if self.file:
            return self.file.url
        return static(self.legacy_path) if self.legacy_path else ""


class SiteSettings(models.Model):
    FONT_MONTSERRAT = "montserrat"
    FONT_HELVETICA = "helvetica"
    FONT_ARIAL = "arial"
    FONT_GEORGIA = "georgia"
    FONT_CHOICES = (
        (FONT_MONTSERRAT, "Montserrat"),
        (FONT_HELVETICA, "Helvetica / Segoe UI"),
        (FONT_ARIAL, "Arial"),
        (FONT_GEORGIA, "Georgia"),
    )
    FONT_STACKS = {
        FONT_MONTSERRAT: '"Montserrat", "Segoe UI", Arial, sans-serif',
        FONT_HELVETICA: '"Helvetica Neue", "Segoe UI", Arial, sans-serif',
        FONT_ARIAL: 'Arial, Helvetica, sans-serif',
        FONT_GEORGIA: 'Georgia, "Times New Roman", serif',
    }

    brand_name = models.CharField(max_length=80, default="VARTEC")
    logo = models.FileField(upload_to="website/branding/", blank=True)
    legacy_logo_path = models.CharField(max_length=255, default="image/logo.png")
    primary_colour = models.CharField(max_length=7, default="#FFC107", validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Use a six-digit hex colour such as #FFC107.")], help_text="Primary gold from the VARTEC logo.")
    secondary_colour = models.CharField(max_length=7, default="#080909", validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Use a six-digit hex colour such as #080909.")], help_text="Dark logo colour used for headings and panels.")
    surface_colour = models.CharField(max_length=7, default="#F5F5F2", validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Use a six-digit hex colour such as #F5F5F2.")], help_text="Light neutral shade used behind content cards.")
    font_family = models.CharField(max_length=20, choices=FONT_CHOICES, default=FONT_MONTSERRAT, help_text="Typography used across the public website.")
    contact_email = models.EmailField(default="info@vartec.global")
    uk_phone = models.CharField(max_length=40, default="+44 800 772 0316")
    nl_phone = models.CharField(max_length=40, default="+31 6 3834 2809")
    notification_email = models.EmailField(blank=True)
    hero_enabled = models.BooleanField(default=True)
    about_enabled = models.BooleanField(default=True)
    services_enabled = models.BooleanField(default=True)
    projects_enabled = models.BooleanField(default=True)
    contact_enabled = models.BooleanField(default=True)
    footer_enabled = models.BooleanField(default=True)
    video_enabled = models.BooleanField(default=True)
    video = models.FileField(upload_to="website/video/", blank=True)
    legacy_video_path = models.CharField(max_length=255, default="video/finalmerge.mp4")
    default_seo_title = models.CharField(max_length=180, default="Solar EPC, Battery Storage & O&M in the UK | VARTEC")
    default_seo_description = models.TextField(default="VARTEC delivers solar EPC, battery storage, carports, floating solar and operations and maintenance services across the UK and Europe.")
    organisation_schema_enabled = models.BooleanField(default=True)
    chatbot_enabled = models.BooleanField(default=True, help_text="Show the website help chat in the bottom corner.")
    chatbot_title = models.CharField(max_length=80, default="VARTEC Assistant")
    chatbot_welcome = models.CharField(max_length=240, default="Hello. How can we help with your solar energy project?")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Global website settings"

    def clean(self):
        if self.pk and self.pk != 1:
            raise ValidationError("Only one Site Settings record is allowed.")

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        return cls.objects.get_or_create(pk=1)[0]

    @property
    def logo_url(self):
        return self.logo.url if self.logo else static(self.legacy_logo_path)

    @property
    def video_url(self):
        return self.video.url if self.video else static(self.legacy_video_path)

    @property
    def font_stack(self):
        return self.FONT_STACKS.get(self.font_family, self.FONT_STACKS[self.FONT_MONTSERRAT])


class HeroSlide(OrderedActiveModel):
    title = models.CharField(max_length=120)
    media = models.ForeignKey(MediaAsset, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.FileField(upload_to="website/hero/", blank=True)
    legacy_image_path = models.CharField(max_length=255, blank=True)
    alt_text_key = models.ForeignKey(TextKey, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ("sort_order", "pk")

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        if self.media:
            return self.media.url
        if self.image:
            return self.image.url
        return static(self.legacy_image_path) if self.legacy_image_path else ""


class HomeBlock(OrderedActiveModel):
    WHITE = "white"
    GOLD = "gold"
    LIGHT = "light"
    DARK = "dark"
    BACKGROUND_CHOICES = ((WHITE, "White"), (GOLD, "Gold"), (LIGHT, "Light grey"), (DARK, "Black"))

    admin_name = models.CharField(max_length=140)
    title_key = models.ForeignKey(TextKey, on_delete=models.PROTECT, related_name="home_block_titles")
    intro_key = models.ForeignKey(TextKey, on_delete=models.SET_NULL, null=True, blank=True, related_name="home_block_intros")
    background = models.CharField(max_length=10, choices=BACKGROUND_CHOICES, default=WHITE)

    class Meta:
        ordering = ("sort_order", "pk")

    def __str__(self):
        return self.admin_name


class HomeFeature(OrderedActiveModel):
    block = models.ForeignKey(HomeBlock, on_delete=models.CASCADE, related_name="features")
    title_key = models.ForeignKey(TextKey, on_delete=models.PROTECT, related_name="home_feature_titles")
    body_key = models.ForeignKey(TextKey, on_delete=models.PROTECT, related_name="home_feature_bodies")
    media = models.ForeignKey(MediaAsset, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ("sort_order", "pk")

    def __str__(self):
        return f"{self.block.admin_name}: {self.title_key.default_text}"


class Page(OrderedActiveModel):
    SERVICE = "service"
    PROJECT = "project"
    STANDARD = "standard"
    KIND_CHOICES = ((SERVICE, "Service"), (PROJECT, "Project"), (STANDARD, "Standard page"))

    kind = models.CharField(max_length=12, choices=KIND_CHOICES, db_index=True)
    slug = models.SlugField(max_length=120)
    title_key = models.ForeignKey(TextKey, on_delete=models.PROTECT, related_name="page_titles")
    intro_key = models.ForeignKey(TextKey, on_delete=models.PROTECT, related_name="page_intros", null=True, blank=True)
    seo_title_key = models.ForeignKey(TextKey, on_delete=models.SET_NULL, related_name="page_seo_titles", null=True, blank=True)
    seo_description_key = models.ForeignKey(TextKey, on_delete=models.SET_NULL, related_name="page_seo_descriptions", null=True, blank=True)
    card_media = models.ForeignKey(MediaAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name="page_cards")
    card_image = models.FileField(upload_to="website/page-cards/", blank=True)
    legacy_card_image_path = models.CharField(max_length=300, blank=True)
    show_on_homepage = models.BooleanField(default=True)
    show_in_navigation = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("kind", "sort_order", "title_key__key")
        constraints = [models.UniqueConstraint(fields=("kind", "slug"), name="unique_page_kind_slug")]

    def __str__(self):
        return f"{self.get_kind_display()}: {self.title_key.default_text}"

    def get_absolute_url(self):
        name = "website:service_detail" if self.kind == self.SERVICE else "website:project_detail"
        kwargs = {"slug": self.slug}
        return reverse(name, kwargs=kwargs)

    @property
    def card_image_url(self):
        if self.card_media:
            return self.card_media.url
        if self.card_image:
            return self.card_image.url
        return static(self.legacy_card_image_path) if self.legacy_card_image_path else ""


class PageSection(OrderedActiveModel):
    TEXT_LEFT = "text_left"
    TEXT_RIGHT = "text_right"
    FULL = "full"
    LAYOUT_CHOICES = ((TEXT_LEFT, "Text left / media right"), (TEXT_RIGHT, "Media left / text right"), (FULL, "Full width"))
    WHITE = "white"
    GOLD = "gold"
    LIGHT = "light"
    BACKGROUND_CHOICES = ((WHITE, "White"), (GOLD, "Gold"), (LIGHT, "Light grey"))

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="sections")
    admin_name = models.CharField(max_length=140, help_text="Internal name shown in the admin.")
    title_key = models.ForeignKey(TextKey, on_delete=models.SET_NULL, null=True, blank=True, related_name="section_titles")
    body_key = models.ForeignKey(TextKey, on_delete=models.SET_NULL, null=True, blank=True, related_name="section_bodies")
    layout = models.CharField(max_length=16, choices=LAYOUT_CHOICES, default=TEXT_LEFT)
    background = models.CharField(max_length=10, choices=BACKGROUND_CHOICES, default=WHITE)
    media = models.ForeignKey(MediaAsset, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.FileField(upload_to="website/sections/", blank=True)
    legacy_image_path = models.CharField(max_length=300, blank=True)
    video = models.FileField(upload_to="website/sections/video/", blank=True)
    legacy_video_path = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ("sort_order", "pk")

    def __str__(self):
        return f"{self.page}: {self.admin_name}"

    @property
    def media_url(self):
        if self.media:
            return self.media.url
        if self.image:
            return self.image.url
        return static(self.legacy_image_path) if self.legacy_image_path else ""

    @property
    def video_url(self):
        if self.video:
            return self.video.url
        return static(self.legacy_video_path) if self.legacy_video_path else ""


class SectionItem(OrderedActiveModel):
    PARAGRAPH = "paragraph"
    BULLET = "bullet"
    NUMBERED = "numbered"
    SUBHEADING = "subheading"
    ITEM_CHOICES = ((PARAGRAPH, "Paragraph"), (BULLET, "Bullet"), (NUMBERED, "Numbered item"), (SUBHEADING, "Subheading"))

    section = models.ForeignKey(PageSection, on_delete=models.CASCADE, related_name="items")
    text_key = models.ForeignKey(TextKey, on_delete=models.PROTECT)
    item_type = models.CharField(max_length=12, choices=ITEM_CHOICES, default=PARAGRAPH)

    class Meta:
        ordering = ("sort_order", "pk")

    def __str__(self):
        return f"{self.section.admin_name}: {self.text_key.key}"


class ContactSubmission(models.Model):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    SPAM = "spam"
    STATUS_CHOICES = ((NEW, "New"), (IN_PROGRESS, "In progress"), (CLOSED, "Closed"), (SPAM, "Spam"))

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=60)
    message = models.TextField()
    language_code = models.CharField(max_length=12, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=NEW, db_index=True)
    email_sent = models.BooleanField(default=False)
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.first_name} {self.last_name} – {self.created_at:%Y-%m-%d}"
