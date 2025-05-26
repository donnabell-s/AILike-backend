from django.urls import path
from .views import analyze_post_content

urlpatterns = [
    path("all-posts/", analyze_post_content),  
]
