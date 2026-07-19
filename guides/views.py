from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import GuideCategory, GuidePost


def published_posts():
    return GuidePost.objects.filter(is_published=True).select_related("category")


def paginate(request, queryset, per_page=9):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def absolute_url(request, path):
    return request.build_absolute_uri(path)


def guide_list(request):
    posts = published_posts()
    context = {
        "page_title": "Guides",
        "page_description": "Helpful guides for scholarships, internships, jobs, fellowships and global applications.",
        "posts": paginate(request, posts),
        "categories": GuideCategory.objects.all(),
        "canonical_url": absolute_url(request, request.path),
    }
    return render(request, "guides/guide_list.html", context)


def guide_detail(request, slug):
    post = get_object_or_404(published_posts(), slug=slug)
    related_posts = (
        published_posts()
        .filter(category=post.category)
        .exclude(pk=post.pk)[:3]
    )
    image_url = request.build_absolute_uri(post.image.url) if post.image else ""
    context = {
        "post": post,
        "related_posts": related_posts,
        "canonical_url": absolute_url(request, post.get_absolute_url()),
        "og_image": image_url,
    }
    return render(request, "guides/guide_detail.html", context)


def guide_category(request, slug):
    category = get_object_or_404(GuideCategory, slug=slug)
    posts = published_posts().filter(category=category)
    context = {
        "page_title": category.name,
        "page_description": category.description or f"Guide articles about {category.name.lower()}.",
        "posts": paginate(request, posts),
        "categories": GuideCategory.objects.all(),
        "category": category,
        "canonical_url": absolute_url(request, category.get_absolute_url()),
    }
    return render(request, "guides/guide_category.html", context)
