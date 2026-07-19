from django import forms

from guides.models import GuidePost
from opportunities.models import Opportunity


class OpportunityForm(forms.ModelForm):
    publish_now = forms.BooleanField(
        label="Publish now",
        required=False,
        help_text="Check this to publish the opportunity immediately.",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = Opportunity
        fields = [
            "title",
            "category",
            "opportunity_type",
            "country",
            "organization",
            "funding_type",
            "education_level",
            "deadline",
            "short_description",
            "overview",
            "benefits",
            "eligibility",
            "required_documents",
            "application_process",
            "official_link",
            "source_name",
            "source_url",
            "meta_title",
            "meta_description",
            "image",
            "tags",
            "is_featured",
            "is_published",
        ]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "short_description": forms.Textarea(attrs={"rows": 3}),
            "overview": forms.Textarea(attrs={"rows": 8}),
            "benefits": forms.Textarea(attrs={"rows": 6}),
            "eligibility": forms.Textarea(attrs={"rows": 6}),
            "required_documents": forms.Textarea(attrs={"rows": 6}),
            "application_process": forms.Textarea(attrs={"rows": 6}),
            "meta_description": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "title": "Use a clear title that matches the official opportunity name.",
            "category": "Choose the main category visitors will use to find this post.",
            "opportunity_type": "Select the opportunity type shown on cards and filters.",
            "deadline": "Leave blank only if the opportunity has no fixed deadline.",
            "short_description": "Write a short summary for cards, search results and meta fallback.",
            "overview": "Explain the opportunity, host organization and who it is for.",
            "benefits": "List funding, stipend, travel support, certificates or other benefits.",
            "eligibility": "Describe who can apply and any restrictions.",
            "required_documents": "List documents applicants should prepare.",
            "application_process": "Explain how applicants should apply step by step.",
            "official_link": "Use the official application or program page.",
            "source_name": "Optional source label, such as the organization or announcement site.",
            "source_url": "Optional source URL if different from the official application link.",
            "meta_title": "Optional SEO title. If empty, the opportunity title is used.",
            "meta_description": "Optional SEO description. If empty, the short description is used.",
            "image": "Upload a relevant image for cards, Open Graph and the detail page.",
            "tags": "Hold Ctrl or Cmd to select multiple tags.",
            "is_featured": "Featured opportunities can appear in highlighted homepage sections.",
            "is_published": "Published opportunities are visible on the public website.",
        }

    def __init__(self, *args, **kwargs):
        show_publish_now = kwargs.pop("show_publish_now", True)
        super().__init__(*args, **kwargs)
        self.fields["deadline"].input_formats = ["%Y-%m-%d"]
        for field_name, help_text in self.Meta.help_texts.items():
            if field_name in self.fields:
                self.fields[field_name].help_text = help_text
        if not show_publish_now:
            self.fields.pop("publish_now", None)
        else:
            self.fields.pop("is_published", None)
        for field_name, field in self.fields.items():
            if field_name == "publish_now":
                continue
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs.setdefault("class", "form-select")
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.setdefault("class", "form-control")
            else:
                field.widget.attrs.setdefault("class", "form-control")


OpportunityCreateForm = OpportunityForm


class GuidePostForm(forms.ModelForm):
    class Meta:
        model = GuidePost
        fields = [
            "title",
            "category",
            "short_description",
            "content",
            "image",
            "author_name",
            "meta_title",
            "meta_description",
        ]
        widgets = {
            "short_description": forms.Textarea(attrs={"rows": 3}),
            "content": forms.Textarea(attrs={"rows": 12}),
            "meta_description": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "title": "Use a clear SEO-friendly title for the guide.",
            "category": "Choose the guide category readers will browse.",
            "short_description": "Short summary for guide cards and meta description fallback.",
            "content": "Write the full guide article content.",
            "image": "Optional image for guide cards, detail page and social sharing.",
            "author_name": "Optional author name displayed on the guide detail page.",
            "meta_title": "Optional SEO title. If empty, the guide title is used.",
            "meta_description": "Optional SEO description. If empty, the short description is used.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, help_text in self.Meta.help_texts.items():
            if field_name in self.fields:
                self.fields[field_name].help_text = help_text
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.setdefault("class", "form-control")
            else:
                field.widget.attrs.setdefault("class", "form-control")
