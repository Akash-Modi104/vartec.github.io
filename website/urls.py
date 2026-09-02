from django.conf import settings
from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "website"

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "favicon.ico",
        RedirectView.as_view(url=f"{settings.STATIC_URL}image/logo.png", permanent=True),
    ),
    path("services/<slug:slug>/", views.page_detail, {"kind": "service"}, name="service_detail"),
    path("projects/<slug:slug>/", views.page_detail, {"kind": "project"}, name="project_detail"),
    path("robots.txt", views.robots, name="robots"),
    path("sitemap.xml", views.sitemap, name="sitemap"),
    path("media/<path:path>", views.media_file, name="media_file"),
]
