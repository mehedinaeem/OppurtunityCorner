from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from .forms import NewsletterSubscriberForm
from .models import NewsletterSubscriber


def subscribe(request):
    redirect_to = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("pages:home")

    if request.method != "POST":
        return redirect(redirect_to)

    form = NewsletterSubscriberForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please enter a valid email address to subscribe.")
        return redirect(redirect_to)

    email = form.cleaned_data["email"].strip().lower()
    name = form.cleaned_data.get("name", "").strip()
    subscriber = NewsletterSubscriber.objects.filter(email__iexact=email).first()

    if subscriber:
        if subscriber.is_active:
            messages.error(request, "This email is already subscribed to the newsletter.")
        else:
            subscriber.is_active = True
            if name and not subscriber.name:
                subscriber.name = name
            subscriber.save(update_fields=["is_active", "name"])
            messages.success(request, "Welcome back. Your newsletter subscription is active again.")
        return redirect(redirect_to)

    NewsletterSubscriber.objects.create(email=email, name=name)
    messages.success(request, "Thanks for subscribing to the OpportunityHub newsletter.")
    return redirect(redirect_to)
