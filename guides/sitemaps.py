from django.contrib.sitemaps import Sitemap

from .models import GuideCategory, GuidePost


class GuidePostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return GuidePost.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class GuideCategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return GuideCategory.objects.all()
