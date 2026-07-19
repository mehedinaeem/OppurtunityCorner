from django import forms


class NewsletterSubscriberForm(forms.Form):
    name = forms.CharField(
        max_length=120,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your name",
                "autocomplete": "name",
            }
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Email address",
                "autocomplete": "email",
                "required": True,
            }
        ),
    )
