from django.urls import path
from .views import analyze_post, all_post_analysis

urlpatterns = [
    path("analyze/", analyze_post),
    path("all-posts/", all_post_analysis),  
]
