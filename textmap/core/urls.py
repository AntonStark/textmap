from django.urls import path

from core import views

urlpatterns = [
    path('text_paragraphs/<str:text_id>', views.get_paragraphs),
]
