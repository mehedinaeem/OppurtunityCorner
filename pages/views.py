from datetime import timedelta

from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from guides.models import GuidePost
from opportunities.models import Country, Opportunity

from .forms import ContactMessageForm, OpportunitySubmissionForm


def home(request):
    today = timezone.localdate()
    approaching_deadline = today + timedelta(days=30)
    opportunities = (
        Opportunity.objects.filter(is_published=True)
        .select_related("category", "country", "organization")
        .prefetch_related("tags")
    )
    context = {
        "featured_opportunities": opportunities.filter(is_featured=True)[:6],
        "latest_opportunities": opportunities[:8],
        "deadline_approaching": opportunities.filter(
            is_expired=False,
            deadline__gte=today,
            deadline__lte=approaching_deadline,
        ).order_by("deadline")[:6],
        "country_opportunities": Country.objects.annotate(
            published_count=Count(
                "opportunities",
                filter=Q(opportunities__is_published=True),
            )
        )
        .filter(published_count__gt=0)
        .order_by("-published_count", "name")[:8],
        "latest_guides": GuidePost.objects.filter(is_published=True)
        .select_related("category")[:3],
    }
    return render(request, "pages/home.html", context)


def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def about(request):
    return render(request, "pages/about.html")


def contact(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for contacting us. We will get back to you soon.")
            return redirect("pages:contact")
    else:
        form = ContactMessageForm()

    return render(request, "pages/contact.html", {"form": form})


def privacy_policy(request):
    return render(request, "pages/privacy_policy.html")


def terms_and_conditions(request):
    return render(request, "pages/terms_and_conditions.html")


def disclaimer(request):
    return render(request, "pages/disclaimer.html")


def advertise(request):
    return render(request, "pages/advertise.html")


def submit_opportunity(request):
    if request.method == "POST":
        form = OpportunitySubmissionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thanks for submitting this opportunity. Our team will review it before publication.",
            )
            return redirect("pages:submit_opportunity")
    else:
        form = OpportunitySubmissionForm()

    return render(request, "pages/submit_opportunity.html", {"form": form})
