from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from opportunities.sitemaps import sitemaps
from pages import views as page_views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", page_views.robots_txt, name="robots_txt"),
    path("", include("dashboard.urls")),
    path("", include("newsletter.urls")),
    path("", include("guides.urls")),
    path("", include("opportunities.urls")),
    path("", include("pages.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
