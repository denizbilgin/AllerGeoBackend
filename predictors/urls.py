from django.urls import path
from . import views

urlpatterns = [
    path("ai-models", views.AIModelView.as_view({
        "get": "list",
        "post": "create"
    })),
    path("ai-models/<int:pk>", views.AIModelView.as_view({
        "get": "retrieve",
        "patch": "partial_update",
        #"delete": "destroy"
    })),
    path("ai-models/predict/<int:district_id>/<str:target_date>", views.AIModelView.as_view({
        "get": "predict",
    })),
    path("ai-allergy-attack-predictions", views.AIAllergyAttackPredictionView.as_view({
        "get": "list",
        "post": "create"
    })),
    path("ai-allergy-attack-predictions/<int:pk>", views.AIAllergyAttackPredictionView.as_view({
        "get": "retrieve",
        "patch": "partial_update",
        "delete": "destroy"
    })),
]
