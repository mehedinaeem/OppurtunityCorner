from django.contrib import admin
from django.utils.html import format_html

from .models import GuideCategory, GuidePost


@admin.register(GuideCategory)
class GuideCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(GuidePost)
class GuidePostAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "title",
        "category",
        "author_name",
        "is_published",
        "created_at",
        "updated_at",
    )
    search_fields = ("title", "short_description", "content", "author_name", "category__name")
    list_filter = ("category", "is_published", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("image_preview", "created_at", "updated_at")
    fieldsets = (
        (
            "Content",
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "short_description",
                    "content",
                    "image",
                    "image_preview",
                    "author_name",
                )
            },
        ),
        (
            "SEO",
            {
                "fields": (
                    "meta_title",
                    "meta_description",
                )
            },
        ),
        (
            "Publishing",
            {
                "fields": (
                    "is_published",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(description="Image")
    def image_preview(self, obj):
        if not obj or not obj.image:
            return "-"
        return format_html(
            '<img src="{}" alt="{}" style="height:56px;width:84px;object-fit:cover;border-radius:4px;" />',
            obj.image.url,
            obj.title,
        )
