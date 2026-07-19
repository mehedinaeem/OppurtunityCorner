from django.contrib import admin
from django import forms
from django.utils.html import format_html

from .models import Category, Country, Opportunity, Organization, Tag


RICH_TEXT_FIELDS = {
    "overview",
    "benefits",
    "eligibility",
    "required_documents",
    "application_process",
}


class OpportunityAdminForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = "__all__"
        widgets = {
            field: forms.Textarea(
                attrs={
                    "class": "django-rich-text",
                    "rows": 12,
                }
            )
            for field in RICH_TEXT_FIELDS
        }

    class Media:
        js = (
            "https://cdn.ckeditor.com/4.22.1/standard/ckeditor.js",
            "admin/js/rich-text-init.js",
        )
        css = {
            "all": ("admin/css/rich-text.css",),
        }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at",)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at",)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "logo_preview", "created_at")
    search_fields = ("name", "description", "website")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("logo_preview", "created_at")

    @admin.display(description="Logo")
    def logo_preview(self, obj):
        if not obj or not obj.logo:
            return "-"
        return format_html(
            '<img src="{}" alt="{} logo" style="height:48px;max-width:120px;object-fit:contain;" />',
            obj.logo.url,
            obj.name,
        )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    form = OpportunityAdminForm
    list_display = (
        "image_preview",
        "title",
        "opportunity_type",
        "category",
        "country",
        "organization",
        "deadline",
        "is_featured",
        "is_published",
        "is_expired",
        "updated_at",
        "created_at",
    )
    search_fields = (
        "title",
        "short_description",
        "overview",
        "organization__name",
        "country__name",
        "tags__name",
    )
    list_filter = (
        "opportunity_type",
        "funding_type",
        "education_level",
        "category",
        "country",
        "is_featured",
        "is_published",
        "is_expired",
        "created_at",
        "deadline",
    )
    actions = (
        "mark_as_published",
        "mark_as_featured",
        "mark_as_expired",
    )
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    date_hierarchy = "created_at"
    readonly_fields = ("image_preview", "created_at", "updated_at")
    fieldsets = (
        (
            "Core Details",
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "opportunity_type",
                    "country",
                    "organization",
                    "funding_type",
                    "education_level",
                    "deadline",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "short_description",
                    "overview",
                    "benefits",
                    "eligibility",
                    "required_documents",
                    "application_process",
                    "image",
                    "image_preview",
                    "tags",
                )
            },
        ),
        (
            "Links and Source",
            {
                "fields": (
                    "official_link",
                    "source_name",
                    "source_url",
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
                    "is_featured",
                    "is_published",
                    "is_expired",
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

    @admin.action(description="Mark selected opportunities as published")
    def mark_as_published(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} opportunity item(s) marked as published.")

    @admin.action(description="Mark selected opportunities as featured")
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} opportunity item(s) marked as featured.")

    @admin.action(description="Mark selected opportunities as expired")
    def mark_as_expired(self, request, queryset):
        updated = queryset.update(is_expired=True)
        self.message_user(request, f"{updated} opportunity item(s) marked as expired.")
