from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from guides.sitemaps import GuideCategorySitemap, GuidePostSitemap

from .models import Category, Country, Opportunity


class OpportunitySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Opportunity.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Category.objects.all()


class CountrySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Country.objects.all()


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return [
            "pages:home",
            "opportunities:list",
            "opportunities:search",
            "guides:list",
            "pages:about",
            "pages:contact",
            "pages:privacy_policy",
            "pages:terms_and_conditions",
            "pages:disclaimer",
            "pages:advertise",
            "pages:submit_opportunity",
        ]

    def location(self, item):
        return reverse(item)


sitemaps = {
    "static": StaticViewSitemap,
    "opportunities": OpportunitySitemap,
    "categories": CategorySitemap,
    "countries": CountrySitemap,
    "guide_posts": GuidePostSitemap,
    "guide_categories": GuideCategorySitemap,
}
