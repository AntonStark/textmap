from django.urls import path

from core import api_views
from core import views

urlpatterns = [
    path('', views.user_home, name='user_home'),
    path('text/<str:text_id>', views.text_info, name='text_info'),

    path('parse_text/<str:text_id>', api_views.parse_text, name='parse_text'),

    path('text_parts/<str:text_uid>', api_views.text_parts, name='text_parts'),
    path('sub_parts/<int:part_id>', api_views.sub_parts, name='sub_parts'),
]
