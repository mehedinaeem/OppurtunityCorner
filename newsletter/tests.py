from django.test import TestCase
from django.urls import reverse

from .models import NewsletterSubscriber


class NewsletterSubscribeTests(TestCase):
    def test_subscribe_creates_active_subscriber(self):
        response = self.client.post(
            reverse("newsletter:subscribe"),
            {"email": "Reader@Example.com", "name": "Reader"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        subscriber = NewsletterSubscriber.objects.get()
        self.assertEqual(subscriber.email, "reader@example.com")
        self.assertEqual(subscriber.name, "Reader")
        self.assertTrue(subscriber.is_active)

    def test_duplicate_active_subscription_is_not_created(self):
        NewsletterSubscriber.objects.create(email="reader@example.com")

        response = self.client.post(
            reverse("newsletter:subscribe"),
            {"email": "reader@example.com"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)

    def test_inactive_subscription_is_reactivated(self):
        subscriber = NewsletterSubscriber.objects.create(
            email="reader@example.com",
            is_active=False,
        )

        response = self.client.post(
            reverse("newsletter:subscribe"),
            {"email": "reader@example.com", "name": "Reader"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        subscriber.refresh_from_db()
        self.assertTrue(subscriber.is_active)
        self.assertEqual(subscriber.name, "Reader")
