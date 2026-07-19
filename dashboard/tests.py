from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from guides.models import GuideCategory, GuidePost
from opportunities.models import Category, Country, Opportunity, Organization


class DashboardAccessTests(TestCase):
    route_names = [
        "dashboard:home",
        "dashboard:opportunities",
        "dashboard:add_opportunity",
        "dashboard:create_opportunity",
        "dashboard:draft_opportunities",
        "dashboard:published_opportunities",
        "dashboard:expired_opportunities",
        "dashboard:guides",
        "dashboard:create_guide",
        "dashboard:categories",
        "dashboard:countries",
        "dashboard:organizations",
        "dashboard:newsletter_subscribers",
    ]

    def test_dashboard_redirects_anonymous_users(self):
        for route_name in self.route_names:
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))

                self.assertEqual(response.status_code, 302)
                self.assertIn("/admin/login/", response["Location"])

    def test_dashboard_allows_staff_users(self):
        user = get_user_model().objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password",
            is_staff=True,
        )
        self.client.login(username="staff", password="password")

        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard Home")

    def test_dashboard_list_pages_allow_staff_users(self):
        get_user_model().objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password",
            is_staff=True,
        )
        self.client.login(username="staff", password="password")

        for route_name in self.route_names:
            if route_name == "dashboard:add_opportunity":
                continue
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))

                self.assertEqual(response.status_code, 200)


class DashboardOpportunityCreateTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password",
            is_staff=True,
        )
        self.client.login(username="staff", password="password")
        self.category = Category.objects.create(name="Scholarships")
        self.country = Country.objects.create(name="United States")
        self.organization = Organization.objects.create(name="Example University")

    def form_data(self, **overrides):
        data = {
            "title": "Dashboard Created Opportunity",
            "category": self.category.pk,
            "opportunity_type": Opportunity.OpportunityType.SCHOLARSHIP,
            "country": self.country.pk,
            "organization": self.organization.pk,
            "funding_type": Opportunity.FundingType.FULLY_FUNDED,
            "education_level": Opportunity.EducationLevel.ANY,
            "deadline": "2026-12-31",
            "short_description": "A dashboard-created opportunity.",
            "overview": "Overview content.",
            "benefits": "Benefits content.",
            "eligibility": "Eligibility content.",
            "required_documents": "Required documents content.",
            "application_process": "Application process content.",
            "official_link": "https://example.com/apply",
            "source_name": "Example Source",
            "source_url": "https://example.com/source",
            "tags": [],
            "is_featured": "",
        }
        data.update(overrides)
        return data

    def test_create_opportunity_defaults_to_unpublished(self):
        response = self.client.post(
            reverse("dashboard:create_opportunity"),
            self.form_data(),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        opportunity = Opportunity.objects.get(title="Dashboard Created Opportunity")
        self.assertFalse(opportunity.is_published)
        self.assertContains(response, "Opportunity created successfully.")

    def test_create_opportunity_can_publish_now(self):
        response = self.client.post(
            reverse("dashboard:create_opportunity"),
            self.form_data(publish_now="on"),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        opportunity = Opportunity.objects.get(title="Dashboard Created Opportunity")
        self.assertTrue(opportunity.is_published)


class DashboardOpportunityManagementTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password",
            is_staff=True,
        )
        self.client.login(username="staff", password="password")
        self.category = Category.objects.create(name="Scholarships")
        self.other_category = Category.objects.create(name="Jobs")
        self.country = Country.objects.create(name="United States")
        self.organization = Organization.objects.create(name="Example University")
        self.opportunity = Opportunity.objects.create(
            title="Editable Opportunity",
            category=self.category,
            opportunity_type=Opportunity.OpportunityType.SCHOLARSHIP,
            country=self.country,
            organization=self.organization,
            funding_type=Opportunity.FundingType.FULLY_FUNDED,
            education_level=Opportunity.EducationLevel.ANY,
            short_description="Original description.",
            overview="Original overview.",
            official_link="https://example.com/apply",
            is_published=False,
        )

    def form_data(self, **overrides):
        data = {
            "title": "Updated Opportunity",
            "category": self.category.pk,
            "opportunity_type": Opportunity.OpportunityType.INTERNSHIP,
            "country": self.country.pk,
            "organization": self.organization.pk,
            "funding_type": Opportunity.FundingType.PAID,
            "education_level": Opportunity.EducationLevel.ANY,
            "deadline": "2026-12-31",
            "short_description": "Updated description.",
            "overview": "Updated overview.",
            "benefits": "Updated benefits.",
            "eligibility": "Updated eligibility.",
            "required_documents": "Updated documents.",
            "application_process": "Updated process.",
            "official_link": "https://example.com/updated",
            "source_name": "Updated Source",
            "source_url": "https://example.com/source",
            "tags": [],
            "is_featured": "on",
            "is_published": "on",
        }
        data.update(overrides)
        return data

    def test_opportunity_list_supports_search_and_filters(self):
        other = Opportunity.objects.create(
            title="Hidden Job",
            category=self.other_category,
            opportunity_type=Opportunity.OpportunityType.JOB,
            country=self.country,
            organization=self.organization,
            funding_type=Opportunity.FundingType.PAID,
            education_level=Opportunity.EducationLevel.ANY,
        )

        response = self.client.get(
            reverse("dashboard:opportunities"),
            {
                "q": "Editable",
                "opportunity_type": Opportunity.OpportunityType.SCHOLARSHIP,
                "category": self.category.pk,
                "country": self.country.pk,
                "is_published": "false",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.opportunity.title)
        self.assertNotContains(response, other.title)

    def test_edit_opportunity_updates_existing_record(self):
        response = self.client.post(
            reverse("dashboard:edit_opportunity", args=[self.opportunity.pk]),
            self.form_data(),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.opportunity.refresh_from_db()
        self.assertEqual(self.opportunity.title, "Updated Opportunity")
        self.assertTrue(self.opportunity.is_published)
        self.assertTrue(self.opportunity.is_featured)
        self.assertContains(response, "Opportunity updated successfully.")

    def test_delete_opportunity_requires_confirmation(self):
        response = self.client.get(
            reverse("dashboard:delete_opportunity", args=[self.opportunity.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirm deletion")

    def test_delete_opportunity_removes_record(self):
        response = self.client.post(
            reverse("dashboard:delete_opportunity", args=[self.opportunity.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Opportunity.objects.filter(pk=self.opportunity.pk).exists())
        self.assertContains(response, "deleted successfully")

    def test_quick_action_publish_uses_post(self):
        response = self.client.post(
            reverse("dashboard:publish_opportunity", args=[self.opportunity.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.opportunity.refresh_from_db()
        self.assertTrue(self.opportunity.is_published)
        self.assertContains(response, "published successfully")

    def test_quick_action_unpublish_uses_post(self):
        self.opportunity.is_published = True
        self.opportunity.save(update_fields=["is_published"])

        response = self.client.post(
            reverse("dashboard:unpublish_opportunity", args=[self.opportunity.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.opportunity.refresh_from_db()
        self.assertFalse(self.opportunity.is_published)
        self.assertContains(response, "unpublished successfully")

    def test_quick_action_mark_featured_uses_post(self):
        response = self.client.post(
            reverse("dashboard:feature_opportunity", args=[self.opportunity.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.opportunity.refresh_from_db()
        self.assertTrue(self.opportunity.is_featured)
        self.assertContains(response, "marked as featured")

    def test_quick_action_mark_expired_uses_post(self):
        response = self.client.post(
            reverse("dashboard:expire_opportunity", args=[self.opportunity.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.opportunity.refresh_from_db()
        self.assertTrue(self.opportunity.is_expired)
        self.assertContains(response, "marked as expired")

    def test_quick_actions_reject_get_requests(self):
        response = self.client.get(
            reverse("dashboard:publish_opportunity", args=[self.opportunity.pk])
        )

        self.assertEqual(response.status_code, 405)

    def test_dashboard_preview_shows_unpublished_opportunity(self):
        response = self.client.get(
            reverse("dashboard:preview_opportunity", args=[self.opportunity.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard Preview")
        self.assertContains(response, self.opportunity.title)
        self.assertContains(response, "Publish")
        self.assertContains(response, "Back to Drafts")

    def test_dashboard_preview_publish_button_publishes(self):
        response = self.client.post(
            reverse("dashboard:publish_opportunity", args=[self.opportunity.pk]),
            {
                "next": reverse("dashboard:preview_opportunity", args=[self.opportunity.pk]),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.opportunity.refresh_from_db()
        self.assertTrue(self.opportunity.is_published)
        self.assertContains(response, "Published")

    def test_unpublished_opportunity_is_not_public(self):
        self.client.logout()
        response = self.client.get(self.opportunity.get_absolute_url())

        self.assertEqual(response.status_code, 404)


class DashboardGuidePostManagementTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password",
            is_staff=True,
        )
        self.client.login(username="staff", password="password")
        self.category = GuideCategory.objects.create(name="Applications")
        self.post = GuidePost.objects.create(
            title="Editable Guide",
            category=self.category,
            short_description="Original guide summary.",
            content="Original guide content.",
            author_name="OpportunityHub Team",
            is_published=False,
        )

    def form_data(self, **overrides):
        data = {
            "title": "Updated Guide",
            "category": self.category.pk,
            "short_description": "Updated guide summary.",
            "content": "Updated guide content.",
            "author_name": "Editor",
            "meta_title": "Updated Guide SEO",
            "meta_description": "Updated guide SEO description.",
        }
        data.update(overrides)
        return data

    def test_guides_list_loads(self):
        response = self.client.get(reverse("dashboard:guides"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
        self.assertContains(response, "Edit")

    def test_create_guide_can_save_as_draft(self):
        response = self.client.post(
            reverse("dashboard:create_guide"),
            self.form_data(title="Draft Guide", publish_action="draft"),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        post = GuidePost.objects.get(title="Draft Guide")
        self.assertFalse(post.is_published)
        self.assertContains(response, "saved as draft successfully")

    def test_create_guide_can_publish_now(self):
        response = self.client.post(
            reverse("dashboard:create_guide"),
            self.form_data(title="Published Guide", publish_action="publish"),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        post = GuidePost.objects.get(title="Published Guide")
        self.assertTrue(post.is_published)
        self.assertContains(response, "published successfully")

    def test_edit_guide_updates_and_publishes(self):
        response = self.client.post(
            reverse("dashboard:edit_guide", args=[self.post.pk]),
            self.form_data(publish_action="publish"),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Guide")
        self.assertTrue(self.post.is_published)

    def test_preview_guide_shows_draft(self):
        response = self.client.get(reverse("dashboard:preview_guide", args=[self.post.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard Preview")
        self.assertContains(response, self.post.title)

    def test_unpublished_guide_is_not_public(self):
        self.client.logout()
        response = self.client.get(self.post.get_absolute_url())

        self.assertEqual(response.status_code, 404)

    def test_delete_guide_requires_confirmation(self):
        response = self.client.get(reverse("dashboard:delete_guide", args=[self.post.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirm deletion")

    def test_delete_guide_removes_record(self):
        response = self.client.post(
            reverse("dashboard:delete_guide", args=[self.post.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(GuidePost.objects.filter(pk=self.post.pk).exists())
        self.assertContains(response, "deleted successfully")
