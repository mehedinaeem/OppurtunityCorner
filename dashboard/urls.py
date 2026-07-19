from django.urls import path

from . import views


app_name = "dashboard"

urlpatterns = [
    path("dashboard/", views.home, name="home"),
    path("dashboard/opportunities/", views.opportunities_list, name="opportunities"),
    path("dashboard/opportunities/add/", views.add_opportunity, name="add_opportunity"),
    path("dashboard/opportunities/create/", views.create_opportunity, name="create_opportunity"),
    path("dashboard/opportunities/<int:pk>/preview/", views.preview_opportunity, name="preview_opportunity"),
    path("dashboard/opportunities/<int:pk>/edit/", views.edit_opportunity, name="edit_opportunity"),
    path("dashboard/opportunities/<int:pk>/delete/", views.delete_opportunity, name="delete_opportunity"),
    path("dashboard/opportunities/<int:pk>/publish/", views.publish_opportunity, name="publish_opportunity"),
    path("dashboard/opportunities/<int:pk>/unpublish/", views.unpublish_opportunity, name="unpublish_opportunity"),
    path("dashboard/opportunities/<int:pk>/feature/", views.feature_opportunity, name="feature_opportunity"),
    path("dashboard/opportunities/<int:pk>/expire/", views.expire_opportunity, name="expire_opportunity"),
    path("dashboard/opportunities/drafts/", views.draft_opportunities, name="draft_opportunities"),
    path("dashboard/opportunities/published/", views.published_opportunities, name="published_opportunities"),
    path("dashboard/opportunities/expired/", views.expired_opportunities, name="expired_opportunities"),
    path("dashboard/guides/", views.guides_list, name="guides"),
    path("dashboard/guides/create/", views.create_guide, name="create_guide"),
    path("dashboard/guides/<int:pk>/preview/", views.preview_guide, name="preview_guide"),
    path("dashboard/guides/<int:pk>/edit/", views.edit_guide, name="edit_guide"),
    path("dashboard/guides/<int:pk>/delete/", views.delete_guide, name="delete_guide"),
    path("dashboard/categories/", views.categories, name="categories"),
    path("dashboard/countries/", views.countries, name="countries"),
    path("dashboard/organizations/", views.organizations, name="organizations"),
    path("dashboard/newsletter-subscribers/", views.newsletter_subscribers, name="newsletter_subscribers"),
]
