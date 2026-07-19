from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage, OpportunitySubmission


class HomePageTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("pages:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OpportunityHub")

    def test_robots_txt_loads(self):
        response = self.client.get(reverse("robots_txt"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sitemap:")

    def test_sitemap_xml_loads(self):
        response = self.client.get(reverse("sitemap"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "urlset")


class StaticPageTests(TestCase):
    def test_static_pages_load(self):
        names = [
            "pages:about",
            "pages:contact",
            "pages:privacy_policy",
            "pages:terms_and_conditions",
            "pages:disclaimer",
            "pages:advertise",
            "pages:submit_opportunity",
        ]

        for name in names:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_contact_form_saves_message(self):
        response = self.client.post(
            reverse("pages:contact"),
            {
                "name": "Test User",
                "email": "test@example.com",
                "subject": "Hello",
                "message": "This is a test message.",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_submit_opportunity_saves_for_review(self):
        response = self.client.post(
            reverse("pages:submit_opportunity"),
            {
                "submitter_name": "Test User",
                "submitter_email": "test@example.com",
                "title": "New Fellowship",
                "organization": "Example Org",
                "opportunity_type": OpportunitySubmission.OpportunityType.FELLOWSHIP,
                "official_link": "https://example.com/fellowship",
                "description": "A useful fellowship opportunity.",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        submission = OpportunitySubmission.objects.get()
        self.assertFalse(submission.is_reviewed)
