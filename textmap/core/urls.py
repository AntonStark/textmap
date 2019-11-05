from django.urls import path

from core import api_views
from core import views

urlpatterns = [
    path('', views.user_home, name='user_home'),

    path('text_paragraphs/<str:text_id>', api_views.get_paragraphs),
    path('text/<str:text_id>', views.get_text),
]
