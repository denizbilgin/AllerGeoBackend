from django.urls import path
from . import views

urlpatterns = [
    path("cities", views.CityView.as_view({
        "get": "list",
        #"post": "create"
    })),
    path("cities/<int:pk>", views.CityView.as_view({
        "get": "retrieve",
        #"patch": "partial_update",
        #"delete": "destroy"
    })),
    path("cities/<str:name>", views.CityView.as_view({
        "get": "retrieve_by_name"
    })),
    path("cities/<int:pk>/vegetation", views.CityView.as_view({
        "get": "fetch_vegetation_data"
    })),
    path("districts", views.DistrictView.as_view({
        "get": "list",
        #"post": "create"
    })),
    path("districts/<int:pk>", views.DistrictView.as_view({
        "get": "retrieve",
        #"patch": "partial_update",
        #"delete": "destroy"
    })),
    path("districts/<str:name>", views.DistrictView.as_view({
        "get": "retrieve_by_name"
    })),
    path("districts/<int:pk>/vegetation", views.DistrictView.as_view({
        "get": "fetch_vegetation_data"
    })),
]
