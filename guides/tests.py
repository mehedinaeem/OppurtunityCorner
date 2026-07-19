from django.test import TestCase
from django.urls import reverse

from .models import GuideCategory, GuidePost


class GuidePublicPageTests(TestCase):
    def setUp(self):
        self.category = GuideCategory.objects.create(name="Applications")
        self.post = GuidePost.objects.create(
            title="How to Apply for Scholarships",
            category=self.category,
            short_description="A practical scholarship application guide.",
            content="Prepare your documents and submit before the deadline.",
            author_name="OpportunityHub Team",
            is_published=True,
        )

    def test_guide_list_loads(self):
        response = self.client.get(reverse("guides:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_guide_detail_loads(self):
        response = self.client.get(self.post.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_guide_category_loads(self):
        response = self.client.get(self.category.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
