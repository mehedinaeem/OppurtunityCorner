from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, Country, Opportunity, Organization, Tag


class OpportunityPublicPageTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Scholarships")
        self.country = Country.objects.create(name="United States")
        self.organization = Organization.objects.create(name="Example University")
        self.tag = Tag.objects.create(name="STEM")
        self.opportunity = Opportunity.objects.create(
            title="Example Scholarship",
            category=self.category,
            opportunity_type=Opportunity.OpportunityType.SCHOLARSHIP,
            country=self.country,
            organization=self.organization,
            funding_type=Opportunity.FundingType.FULLY_FUNDED,
            education_level=Opportunity.EducationLevel.ANY,
            deadline=timezone.localdate() + timedelta(days=30),
            short_description="A test scholarship for smoke testing.",
            overview="Detailed overview.",
            official_link="https://example.com/apply",
            is_featured=True,
            is_published=True,
        )
        self.opportunity.tags.add(self.tag)

    def test_opportunity_list_loads(self):
        response = self.client.get(reverse("opportunities:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.opportunity.title)

    def test_opportunity_detail_loads(self):
        response = self.client.get(self.opportunity.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Apply Officially")
        self.assertContains(response, '<link rel="canonical"', html=False)
        self.assertContains(response, 'property="og:title"', html=False)
        self.assertContains(response, 'name="twitter:title"', html=False)
        self.assertContains(response, 'type="application/ld+json"', html=False)

    def test_job_detail_includes_job_posting_schema(self):
        job = Opportunity.objects.create(
            title="Example Job",
            category=self.category,
            opportunity_type=Opportunity.OpportunityType.JOB,
            country=self.country,
            organization=self.organization,
            funding_type=Opportunity.FundingType.PAID,
            education_level=Opportunity.EducationLevel.ANY,
            short_description="A test job.",
            overview="Detailed job overview.",
            official_link="https://example.com/job",
            is_published=True,
        )

        response = self.client.get(job.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"@type": "JobPosting"')

    def test_category_page_loads(self):
        response = self.client.get(self.category.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.opportunity.title)

    def test_country_page_loads(self):
        response = self.client.get(self.country.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.opportunity.title)

    def test_search_results_load(self):
        response = self.client.get(reverse("opportunities:search"), {"q": "Example"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.opportunity.title)
