from django.urls import path

from . import views


app_name = "opportunities"

urlpatterns = [
    path("opportunities/", views.opportunity_list, name="list"),
    path("opportunities/<slug:slug>/", views.opportunity_detail, name="detail"),
    path("category/<slug:slug>/", views.category_detail, name="category"),
    path("country/<slug:slug>/", views.country_detail, name="country"),
    path("search/", views.search_results, name="search"),
]
