from django import forms

from .models import ContactMessage, OpportunitySubmission


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 6}),
        }


class OpportunitySubmissionForm(forms.ModelForm):
    class Meta:
        model = OpportunitySubmission
        fields = [
            "submitter_name",
            "submitter_email",
            "title",
            "organization",
            "opportunity_type",
            "official_link",
            "description",
        ]
        widgets = {
            "submitter_name": forms.TextInput(attrs={"class": "form-control"}),
            "submitter_email": forms.EmailInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "organization": forms.TextInput(attrs={"class": "form-control"}),
            "opportunity_type": forms.Select(attrs={"class": "form-select"}),
            "official_link": forms.URLInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 7}),
        }
