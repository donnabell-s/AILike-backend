from django.urls import path
from .views import analyze_post

urlpatterns = [
    path("analyze/", analyze_post),
]