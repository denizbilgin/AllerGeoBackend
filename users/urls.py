from django.urls import path
from allergies.views import UserAllergyView, AllergyAttackView
from .views import TravelView
from . import views
from predictors.views import AIAllergyAttackPredictionView

urlpatterns = [
    path("", views.UserView.as_view({
        "get": "list"
    })),
    path("<int:pk>/allergies", UserAllergyView.as_view({
        "get": "retrieve_user_allergies",
        "post": "create",
        "delete": "destroy"
    })),
    path("<int:pk>/allergy-attacks", AllergyAttackView.as_view({
        "get": "retrieve_user_allergy_attacks",
        "post": "create"
    })),
    path("<int:pk>/allergy-attacks/<int:allergy_attack_id>", AllergyAttackView.as_view({
        "patch": "partial_update",
        "delete": "destroy"
    })),
    path("<int:pk>/travels", TravelView.as_view({
        "get": "retrieve_user_travels",
        "post": "create"
    })),
    path("<int:pk>/travels/<int:travel_id>", TravelView.as_view({
        "patch": "partial_update",
        "delete": "destroy",
    })),
    path("<int:pk>/travels/<int:travel_id>/waypoints", AIAllergyAttackPredictionView.as_view({
        "get": "retrieve_user_travel_waypoints",
        "post": "create_travel_waypoints"
    })),
    path("<int:pk>/travels/<int:travel_id>/waypoints/<int:waypoint_id>", AIAllergyAttackPredictionView.as_view({
        "get": "retrieve_waypoint",
        "patch": "partial_update_waypoint",
        "delete": "destroy_waypoint"
    })),
]
