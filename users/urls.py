from django.urls import path
from allergies.views import UserAllergyView
from .views import TravelView
from . import views
from predictors.views import AIAllergyAttackPredictionView

urlpatterns = [
    path("", views.UserView.as_view({
        "get": "list"
    })),
    path("<int:user_id>", views.UserView.as_view({
        "get": "retrieve",
        "patch": 'update'
    })),
    path("login", views.UserView.as_view({
        "post": "login"
    })),
    path("register", views.UserView.as_view({
        "post": "register"
    })),
    path("refresh-token", views.UserView.as_view({
        "post": "refresh_token"
    })),
    path("logout", views.UserView.as_view({
        "post": "logout"
    })),
    path("<int:user_id>/allergies", UserAllergyView.as_view({
        "get": "retrieve_user_allergies",
        "post": "create",
    })),
    path("<int:user_id>/allergies/<int:user_allergy_id>", UserAllergyView.as_view({
        "get": "retrieve_user_allergy",
        "patch": "partial_update",
        "delete": "destroy"
    })),
    path("<int:user_id>/travels", TravelView.as_view({
        "get": "retrieve_user_travels",
        "post": "create"
    })),
    path("<int:user_id>/travels/<int:travel_id>", TravelView.as_view({
        "get": "retrieve_travel",
        "patch": "partial_update",
        "delete": "destroy",
    })),

    path("<int:user_id>/travels/<int:travel_id>/waypoints", AIAllergyAttackPredictionView.as_view({
        "get": "retrieve_user_travel_waypoints",
        "post": "create_travel_waypoints"
    })),
    path("<int:user_id>/travels/<int:travel_id>/waypoints/<int:waypoint_id>", AIAllergyAttackPredictionView.as_view({
        "get": "retrieve_waypoint",
        "patch": "partial_update_waypoint",
        "delete": "destroy_waypoint"
    })),
    path("<int:user_id>/allergy-attacks", AIAllergyAttackPredictionView.as_view({
        "get": "retrieve_user_allergy_attacks",
        "post": "create_user_allergy_attack"
    })),
    path("<int:user_id>/allergy-attacks/<int:allergy_attack_id>", AIAllergyAttackPredictionView.as_view({
        "get": "retrieve_allergy_attack",
        "patch": "partial_update_user_allergy_attack",
        "delete": "destroy_user_allergy_attack"
    })),
]
