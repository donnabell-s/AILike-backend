from django.urls import path
from .views import all_post_analysis

urlpatterns = [
    path("all-posts/", all_post_analysis),  
]
