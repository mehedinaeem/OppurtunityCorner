from django.db import models
from django.urls import reverse
from django.utils import timezone
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


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("opportunities:category", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)


class Country(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("opportunities:country", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)


class Organization(models.Model):
    name = models.CharField(max_length=180, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="organizations/logos/", blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)


class Opportunity(models.Model):
    class OpportunityType(models.TextChoices):
        SCHOLARSHIP = "scholarship", "Scholarship"
        INTERNSHIP = "internship", "Internship"
        JOB = "job", "Job"
        FELLOWSHIP = "fellowship", "Fellowship"
        EXCHANGE_PROGRAM = "exchange_program", "Exchange Program"
        COMPETITION = "competition", "Competition"
        TRAINING = "training", "Training"

    class FundingType(models.TextChoices):
        FULLY_FUNDED = "fully_funded", "Fully Funded"
        PARTIALLY_FUNDED = "partially_funded", "Partially Funded"
        PAID = "paid", "Paid"
        UNPAID = "unpaid", "Unpaid"
        FREE = "free", "Free"
        OTHER = "other", "Other"

    class EducationLevel(models.TextChoices):
        BACHELOR = "bachelor", "Bachelor"
        MASTERS = "masters", "Masters"
        PHD = "phd", "PhD"
        UNDERGRADUATE = "undergraduate", "Undergraduate"
        GRADUATE = "graduate", "Graduate"
        ANY = "any", "Any"

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="opportunities",
    )
    opportunity_type = models.CharField(
        max_length=32,
        choices=OpportunityType.choices,
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="opportunities",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="opportunities",
    )
    funding_type = models.CharField(
        max_length=32,
        choices=FundingType.choices,
    )
    education_level = models.CharField(
        max_length=32,
        choices=EducationLevel.choices,
    )
    deadline = models.DateField(null=True, blank=True)
    short_description = models.TextField(blank=True)
    overview = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    eligibility = models.TextField(blank=True)
    required_documents = models.TextField(blank=True)
    application_process = models.TextField(blank=True)
    official_link = models.URLField(blank=True)
    source_name = models.CharField(max_length=180, blank=True)
    source_url = models.URLField(blank=True)
    image = models.ImageField(upload_to="opportunities/images/", blank=True)
    tags = models.ManyToManyField(Tag, related_name="opportunities", blank=True)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    @property
    def has_expired(self):
        return self.is_expired or (
            self.deadline is not None and self.deadline < timezone.localdate()
        )

    def get_absolute_url(self):
        return reverse("opportunities:detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)
