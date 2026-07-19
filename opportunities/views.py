import json

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Category, Country, Opportunity


def published_opportunities():
    return (
        Opportunity.objects.filter(is_published=True)
        .select_related("category", "country", "organization")
        .prefetch_related("tags")
    )


def paginate(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def filter_opportunities(request, queryset):
    category = request.GET.get("category")
    opportunity_type = request.GET.get("opportunity_type")
    country = request.GET.get("country")
    funding_type = request.GET.get("funding_type")
    education_level = request.GET.get("education_level")
    deadline = request.GET.get("deadline")

    if category:
        queryset = queryset.filter(category__slug=category)
    if opportunity_type:
        queryset = queryset.filter(opportunity_type=opportunity_type)
    if country:
        queryset = queryset.filter(country__slug=country)
    if funding_type:
        queryset = queryset.filter(funding_type=funding_type)
    if education_level:
        queryset = queryset.filter(education_level=education_level)
    if deadline == "upcoming":
        queryset = queryset.filter(deadline__gte=timezone.localdate())
    elif deadline == "expired":
        today = timezone.localdate()
        queryset = queryset.filter(Q(deadline__lt=today) | Q(is_expired=True))
    elif deadline == "no_deadline":
        queryset = queryset.filter(deadline__isnull=True)

    return queryset


def filter_context(request):
    params = request.GET.copy()
    params.pop("page", None)

    return {
        "categories": Category.objects.all(),
        "countries": Country.objects.all(),
        "opportunity_type_choices": Opportunity.OpportunityType.choices,
        "funding_type_choices": Opportunity.FundingType.choices,
        "education_level_choices": Opportunity.EducationLevel.choices,
        "selected": request.GET,
        "query_string": params.urlencode(),
    }


def absolute_url(request, path):
    return request.build_absolute_uri(path)


def opportunity_image_url(request, opportunity):
    if opportunity.image:
        return request.build_absolute_uri(opportunity.image.url)
    return ""


def opportunity_structured_data(request, opportunity):
    url = absolute_url(request, opportunity.get_absolute_url())
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": opportunity.seo_title,
        "description": opportunity.seo_description,
        "url": url,
        "datePublished": opportunity.created_at.date().isoformat(),
        "dateModified": opportunity.updated_at.date().isoformat(),
        "author": {
            "@type": "Organization",
            "name": "OpportunityHub",
        },
        "publisher": {
            "@type": "Organization",
            "name": "OpportunityHub",
        },
        "about": opportunity.get_opportunity_type_display(),
    }
    image_url = opportunity_image_url(request, opportunity)
    if image_url:
        data["image"] = image_url
    return data


def job_posting_structured_data(request, opportunity):
    if opportunity.opportunity_type != Opportunity.OpportunityType.JOB:
        return None

    data = {
        "@context": "https://schema.org",
        "@type": "JobPosting",
        "title": opportunity.title,
        "description": opportunity.overview or opportunity.short_description,
        "datePosted": opportunity.created_at.date().isoformat(),
        "hiringOrganization": {
            "@type": "Organization",
            "name": opportunity.organization.name,
        },
        "jobLocation": {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "addressCountry": opportunity.country.name,
            },
        },
        "url": absolute_url(request, opportunity.get_absolute_url()),
    }
    if opportunity.organization.website:
        data["hiringOrganization"]["sameAs"] = opportunity.organization.website
    if opportunity.organization.logo:
        data["hiringOrganization"]["logo"] = request.build_absolute_uri(
            opportunity.organization.logo.url
        )
    if opportunity.deadline:
        data["validThrough"] = opportunity.deadline.isoformat()
    return data


def opportunity_list(request):
    opportunities = filter_opportunities(request, published_opportunities())

    context = {
        "page_title": "Scholarships, Jobs, Internships and Fellowships",
        "page_description": "Browse the latest scholarships, internships, jobs, fellowships and global opportunity updates.",
        "canonical_url": absolute_url(request, request.path),
        "opportunities": paginate(request, opportunities),
        **filter_context(request),
    }
    return render(request, "opportunities/opportunity_list.html", context)


def opportunity_detail(request, slug):
    opportunity = get_object_or_404(published_opportunities(), slug=slug)
    tag_ids = opportunity.tags.values_list("id", flat=True)
    related_opportunities = (
        published_opportunities()
        .filter(Q(category=opportunity.category) | Q(tags__in=tag_ids))
        .exclude(pk=opportunity.pk)
        .distinct()[:4]
    )
    job_posting_schema = job_posting_structured_data(request, opportunity)

    return render(
        request,
        "opportunities/opportunity_detail.html",
        {
            "opportunity": opportunity,
            "related_opportunities": related_opportunities,
            "canonical_url": absolute_url(request, opportunity.get_absolute_url()),
            "og_image": opportunity_image_url(request, opportunity),
            "structured_data_json": json.dumps(
                opportunity_structured_data(request, opportunity)
            ),
            "job_posting_schema_json": json.dumps(job_posting_schema)
            if job_posting_schema
            else "",
        },
    )


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    opportunities = filter_opportunities(
        request,
        published_opportunities().filter(category=category),
    )

    context = {
        "page_title": category.name,
        "page_description": category.description
        or f"Latest {category.name.lower()} opportunities.",
        "canonical_url": absolute_url(request, category.get_absolute_url()),
        "opportunities": paginate(request, opportunities),
        "category": category,
        **filter_context(request),
    }
    return render(request, "opportunities/category_detail.html", context)


def country_detail(request, slug):
    country = get_object_or_404(Country, slug=slug)
    opportunities = filter_opportunities(
        request,
        published_opportunities().filter(country=country),
    )

    context = {
        "page_title": f"Opportunities in {country.name}",
        "page_description": f"Browse scholarships, jobs, internships and fellowships in {country.name}.",
        "canonical_url": absolute_url(request, country.get_absolute_url()),
        "opportunities": paginate(request, opportunities),
        "country": country,
        **filter_context(request),
    }
    return render(request, "opportunities/country_detail.html", context)


def search_results(request):
    query = request.GET.get("q", "").strip()
    opportunities = published_opportunities()

    if query:
        opportunities = opportunities.filter(
            Q(title__icontains=query)
            | Q(short_description__icontains=query)
            | Q(overview__icontains=query)
            | Q(benefits__icontains=query)
            | Q(eligibility__icontains=query)
            | Q(organization__name__icontains=query)
            | Q(country__name__icontains=query)
            | Q(category__name__icontains=query)
            | Q(tags__name__icontains=query)
        ).distinct()
    else:
        opportunities = opportunities.none()

    params = request.GET.copy()
    params.pop("page", None)

    return render(
        request,
        "opportunities/search_results.html",
        {
            "query": query,
            "opportunities": paginate(request, opportunities),
            "query_string": params.urlencode(),
            "canonical_url": absolute_url(request, request.path),
        },
    )
