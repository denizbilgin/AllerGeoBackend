from django.urls import path
from . import views

urlpatterns = [
    path("allergen-types", views.AllergenTypeView.as_view({
        "get": "list",
        "post": "create"
    })),
    path("allergen-types/<int:pk>", views.AllergenTypeView.as_view({
        "get": "retrieve",
        "patch": "partial_update",
        "delete": "destroy"
    })),
    path("allergen-types/<int:pk>/allergens", views.AllergenTypeView.as_view({
        "get": "retrieve_allergens_by_type"
    })),

    path("allergens", views.AllergenView.as_view({
        "get": "list",
        "post": "create"
    })),
    path("allergens/<int:pk>", views.AllergenView.as_view({
        "get": "retrieve",
        "patch": "partial_update",
        "delete": "destroy"
    })),
    path("allergens/<str:name>", views.AllergenView.as_view({
        "get": "retrieve_by_name"
    })),
    path("allergens/<int:pk>/regions", views.AllergenRegionView.as_view({
        "get": "retrieve_by_allergen",
        "post": "create",
        "delete": "destroy"
    })),

    path("common-regions", views.CommonRegionView.as_view({
        "get": "list",
        "post": "create"
    })),
    path("common-regions/<int:pk>", views.CommonRegionView.as_view({
        "get": "retrieve",
        "patch": "partial_update",
        "delete": "destroy"
    })),
    path("common-regions/<int:pk>/allergens", views.AllergenRegionView.as_view({
        "get": "retrieve_by_region"
    })),
]
