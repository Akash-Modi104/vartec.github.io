from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from website import cms_api, views as website_views

admin.site.site_header = "VARTEC Website Administration"
admin.site.site_title = "VARTEC Admin"
admin.site.index_title = "Website content and configuration"

urlpatterns = [
    path("admin/", website_views.cms_shell, name="cms"),
    path("admin/<path:path>", website_views.cms_shell, name="cms-route"),
    path("cms-api/session/", cms_api.session_view, name="cms-session"),
    path("cms-api/login/", cms_api.login_view, name="cms-login"),
    path("cms-api/logout/", cms_api.logout_view, name="cms-logout"),
    path("cms-api/dashboard/", cms_api.dashboard_view, name="cms-dashboard"),
    path("cms-api/resources/<slug:resource>/", cms_api.resource_list, name="cms-resource-list"),
    path("cms-api/resources/<slug:resource>/<int:pk>/", cms_api.resource_detail, name="cms-resource-detail"),
    path("django-admin/", admin.site.urls),
    path("", include("website.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
