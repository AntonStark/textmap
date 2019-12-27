from django.urls import path

from core import api_views
from core import views

urlpatterns = [
    path('', views.user_home, name='user_home'),
    path('text/<str:text_id>', views.text_info, name='text_info'),
    path('text/<str:text_id>/action/', views.register_action, name='register_action'),
    path('section/<str:section_uid>', views.section_view, name='section_view'),

    path('parse_text/<str:text_uid>', api_views.parse_text, name='parse_text'),
    path('add_section/<str:section_uid>', api_views.add_section, name='add_section'),
    path('paragraph_concat/<str:paragraph_uid>', api_views.paragraph_concat, name='paragraph_concat'),

    path('text_sections/<str:text_uid>', api_views.text_sections, name='text_sections'),
    path('sub_sections/<str:section_uid>', api_views.sub_sections, name='sub_sections'),
]
