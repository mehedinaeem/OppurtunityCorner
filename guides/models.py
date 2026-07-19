from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def unique_slugify(instance, value):
    base_slug = slugify(value) or "item"
    slug = base_slug
    model_class = instance.__class__
    counter = 1

    while model_class.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        counter += 1
        slug = f"{base_slug}-{counter}"

    return slug


class GuideCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "guide categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("guides:category", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)


class GuidePost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    category = models.ForeignKey(
        GuideCategory,
        on_delete=models.PROTECT,
        related_name="posts",
    )
    short_description = models.TextField(blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to="guides/images/", blank=True)
    author_name = models.CharField(max_length=120, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def seo_title(self):
        return self.meta_title or self.title

    @property
    def seo_description(self):
        return self.meta_description or self.short_description

    def get_absolute_url(self):
        return reverse("guides:detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)
