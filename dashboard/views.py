import json

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import GuidePostForm, OpportunityForm
from guides.models import GuideCategory, GuidePost
from guides.views import published_posts as public_published_guides
from newsletter.models import NewsletterSubscriber
from opportunities.models import Category, Country, Opportunity, Organization
from opportunities.views import (
    job_posting_structured_data,
    opportunity_image_url,
    opportunity_structured_data,
    published_opportunities as public_published_opportunities,
)


def paginate(request, queryset, per_page=20):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def opportunity_queryset():
    return Opportunity.objects.select_related(
        "category",
        "country",
        "organization",
    ).prefetch_related("tags")


def opportunity_filters(request, queryset):
    query = request.GET.get("q", "").strip()
    opportunity_type = request.GET.get("opportunity_type")
    category = request.GET.get("category")
    country = request.GET.get("country")
    is_published = request.GET.get("is_published")

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(organization__name__icontains=query)
        )
    if opportunity_type:
        queryset = queryset.filter(opportunity_type=opportunity_type)
    if category:
        queryset = queryset.filter(category_id=category)
    if country:
        queryset = queryset.filter(country_id=country)
    if is_published == "true":
        queryset = queryset.filter(is_published=True)
    elif is_published == "false":
        queryset = queryset.filter(is_published=False)

    params = request.GET.copy()
    params.pop("page", None)
    return queryset, params.urlencode()


def opportunity_list_context(request, queryset, page_title):
    queryset, query_string = opportunity_filters(request, queryset)
    return {
        "page_title": page_title,
        "opportunities": paginate(request, queryset),
        "categories": Category.objects.all(),
        "countries": Country.objects.all(),
        "opportunity_type_choices": Opportunity.OpportunityType.choices,
        "selected": request.GET,
        "query_string": query_string,
    }


@staff_member_required
def home(request):
    today = timezone.localdate()
    context = {
        "total_opportunities": Opportunity.objects.count(),
        "draft_opportunities": Opportunity.objects.filter(is_published=False).count(),
        "published_opportunities": Opportunity.objects.filter(is_published=True).count(),
        "expired_opportunities": Opportunity.objects.filter(
            Q(is_expired=True) | Q(deadline__lt=today)
        ).count(),
        "categories_count": Category.objects.count(),
        "countries_count": Country.objects.count(),
        "organizations_count": Organization.objects.count(),
        "subscribers_count": NewsletterSubscriber.objects.filter(is_active=True).count(),
        "recent_opportunities": opportunity_queryset()[:8],
    }
    return render(request, "dashboard/home.html", context)


def guide_queryset():
    return GuidePost.objects.select_related("category")


@staff_member_required
def opportunities_list(request):
    return render(
        request,
        "dashboard/opportunities_list.html",
        opportunity_list_context(request, opportunity_queryset(), "All Opportunities"),
    )


@staff_member_required
def add_opportunity(request):
    return redirect("dashboard:create_opportunity")


@staff_member_required
def create_opportunity(request):
    if request.method == "POST":
        form = OpportunityForm(request.POST, request.FILES)
        if form.is_valid():
            opportunity = form.save(commit=False)
            opportunity.is_published = form.cleaned_data["publish_now"]
            opportunity.save()
            form.save_m2m()
            messages.success(request, "Opportunity created successfully.")
            return redirect("dashboard:opportunities")
        messages.error(request, "Please correct the errors below.")
    else:
        form = OpportunityForm()

    return render(
        request,
        "dashboard/opportunity_form.html",
        {
            "form": form,
            "page_title": "Add Opportunity",
        },
    )


@staff_member_required
def edit_opportunity(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    if request.method == "POST":
        form = OpportunityForm(
            request.POST,
            request.FILES,
            instance=opportunity,
            show_publish_now=False,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Opportunity updated successfully.")
            return redirect("dashboard:opportunities")
        messages.error(request, "Please correct the errors below.")
    else:
        form = OpportunityForm(instance=opportunity, show_publish_now=False)

    return render(
        request,
        "dashboard/opportunity_form.html",
        {
            "form": form,
            "page_title": "Edit Opportunity",
            "opportunity": opportunity,
        },
    )


@staff_member_required
def delete_opportunity(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    if request.method == "POST":
        title = opportunity.title
        opportunity.delete()
        messages.success(request, f'"{title}" deleted successfully.')
        return redirect("dashboard:opportunities")

    return render(
        request,
        "dashboard/opportunity_confirm_delete.html",
        {
            "opportunity": opportunity,
            "page_title": "Delete Opportunity",
        },
    )


@staff_member_required
def preview_opportunity(request, pk):
    opportunity = get_object_or_404(opportunity_queryset(), pk=pk)
    tag_ids = opportunity.tags.values_list("id", flat=True)
    related_opportunities = (
        public_published_opportunities()
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
            "canonical_url": request.build_absolute_uri(opportunity.get_absolute_url()),
            "og_image": opportunity_image_url(request, opportunity),
            "structured_data_json": json.dumps(
                opportunity_structured_data(request, opportunity)
            ),
            "job_posting_schema_json": json.dumps(job_posting_schema)
            if job_posting_schema
            else "",
            "dashboard_preview": True,
        },
    )


def redirect_back(request):
    return redirect(request.POST.get("next") or "dashboard:opportunities")


@staff_member_required
@require_POST
def publish_opportunity(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    opportunity.is_published = True
    opportunity.save(update_fields=["is_published", "updated_at"])
    messages.success(request, f'"{opportunity.title}" published successfully.')
    return redirect_back(request)


@staff_member_required
@require_POST
def unpublish_opportunity(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    opportunity.is_published = False
    opportunity.save(update_fields=["is_published", "updated_at"])
    messages.success(request, f'"{opportunity.title}" unpublished successfully.')
    return redirect_back(request)


@staff_member_required
@require_POST
def feature_opportunity(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    opportunity.is_featured = True
    opportunity.save(update_fields=["is_featured", "updated_at"])
    messages.success(request, f'"{opportunity.title}" marked as featured.')
    return redirect_back(request)


@staff_member_required
@require_POST
def expire_opportunity(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    opportunity.is_expired = True
    opportunity.save(update_fields=["is_expired", "updated_at"])
    messages.success(request, f'"{opportunity.title}" marked as expired.')
    return redirect_back(request)


@staff_member_required
def guides_list(request):
    return render(
        request,
        "dashboard/guides_list.html",
        {
            "page_title": "Guide Posts",
            "posts": paginate(request, guide_queryset()),
        },
    )


def save_guide_form(request, form):
    post = form.save(commit=False)
    post.is_published = request.POST.get("publish_action") == "publish"
    post.save()
    return post


@staff_member_required
def create_guide(request):
    if request.method == "POST":
        form = GuidePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = save_guide_form(request, form)
            status = "published" if post.is_published else "saved as draft"
            messages.success(request, f'"{post.title}" {status} successfully.')
            return redirect("dashboard:guides")
        messages.error(request, "Please correct the errors below.")
    else:
        form = GuidePostForm()

    return render(
        request,
        "dashboard/guide_form.html",
        {
            "form": form,
            "page_title": "Add Guide Post",
        },
    )


@staff_member_required
def edit_guide(request, pk):
    post = get_object_or_404(GuidePost, pk=pk)
    if request.method == "POST":
        form = GuidePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = save_guide_form(request, form)
            status = "published" if post.is_published else "saved as draft"
            messages.success(request, f'"{post.title}" {status} successfully.')
            return redirect("dashboard:guides")
        messages.error(request, "Please correct the errors below.")
    else:
        form = GuidePostForm(instance=post)

    return render(
        request,
        "dashboard/guide_form.html",
        {
            "form": form,
            "page_title": "Edit Guide Post",
            "post": post,
        },
    )


@staff_member_required
def delete_guide(request, pk):
    post = get_object_or_404(GuidePost, pk=pk)
    if request.method == "POST":
        title = post.title
        post.delete()
        messages.success(request, f'"{title}" deleted successfully.')
        return redirect("dashboard:guides")

    return render(
        request,
        "dashboard/guide_confirm_delete.html",
        {
            "post": post,
            "page_title": "Delete Guide Post",
        },
    )


@staff_member_required
def preview_guide(request, pk):
    post = get_object_or_404(guide_queryset(), pk=pk)
    related_posts = (
        public_published_guides()
        .filter(category=post.category)
        .exclude(pk=post.pk)[:3]
    )
    image_url = request.build_absolute_uri(post.image.url) if post.image else ""

    return render(
        request,
        "guides/guide_detail.html",
        {
            "post": post,
            "related_posts": related_posts,
            "canonical_url": request.build_absolute_uri(post.get_absolute_url()),
            "og_image": image_url,
            "dashboard_preview": True,
        },
    )


@staff_member_required
def draft_opportunities(request):
    return render(
        request,
        "dashboard/opportunities_list.html",
        opportunity_list_context(
            request,
            opportunity_queryset().filter(is_published=False),
            "Draft Opportunities",
        ),
    )


@staff_member_required
def published_opportunities(request):
    return render(
        request,
        "dashboard/opportunities_list.html",
        opportunity_list_context(
            request,
            opportunity_queryset().filter(is_published=True),
            "Published Opportunities",
        ),
    )


@staff_member_required
def expired_opportunities(request):
    today = timezone.localdate()
    return render(
        request,
        "dashboard/opportunities_list.html",
        opportunity_list_context(
            request,
            opportunity_queryset().filter(Q(is_expired=True) | Q(deadline__lt=today)),
            "Expired Opportunities",
        ),
    )


@staff_member_required
def categories(request):
    return render(
        request,
        "dashboard/simple_list.html",
        {
            "page_title": "Categories",
            "items": paginate(request, Category.objects.all()),
            "columns": ("Name", "Slug", "Created"),
            "model_name": "category",
        },
    )


@staff_member_required
def countries(request):
    return render(
        request,
        "dashboard/simple_list.html",
        {
            "page_title": "Countries",
            "items": paginate(request, Country.objects.all()),
            "columns": ("Name", "Slug", "Created"),
            "model_name": "country",
        },
    )


@staff_member_required
def organizations(request):
    return render(
        request,
        "dashboard/organizations_list.html",
        {
            "page_title": "Organizations",
            "organizations": paginate(request, Organization.objects.all()),
        },
    )


@staff_member_required
def newsletter_subscribers(request):
    subscribers = NewsletterSubscriber.objects.all()
    return render(
        request,
        "dashboard/subscribers_list.html",
        {
            "page_title": "Newsletter Subscribers",
            "subscribers": paginate(request, subscribers),
        },
    )
