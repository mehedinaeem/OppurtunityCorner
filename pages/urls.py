from django.urls import path

from . import views


app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("terms-and-conditions/", views.terms_and_conditions, name="terms_and_conditions"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),
    path("advertise/", views.advertise, name="advertise"),
    path("submit-opportunity/", views.submit_opportunity, name="submit_opportunity"),
]
