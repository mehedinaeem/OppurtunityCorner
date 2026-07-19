from django.contrib import admin

from .models import ContactMessage, OpportunitySubmission


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "created_at")
    search_fields = ("name", "email", "subject", "message")
    list_filter = ("created_at",)
    readonly_fields = ("name", "email", "subject", "message", "created_at")


@admin.register(OpportunitySubmission)
class OpportunitySubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "organization",
        "opportunity_type",
        "submitter_name",
        "is_reviewed",
        "created_at",
    )
    search_fields = (
        "title",
        "organization",
        "submitter_name",
        "submitter_email",
        "description",
    )
    list_filter = ("opportunity_type", "is_reviewed", "created_at")
    readonly_fields = (
        "submitter_name",
        "submitter_email",
        "title",
        "organization",
        "opportunity_type",
        "official_link",
        "description",
        "created_at",
    )
