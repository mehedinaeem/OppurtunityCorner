from django.urls import path

from . import views


app_name = "guides"

urlpatterns = [
    path("guides/", views.guide_list, name="list"),
    path("guides/<slug:slug>/", views.guide_detail, name="detail"),
    path("guides/category/<slug:slug>/", views.guide_category, name="category"),
]
