from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name='register'),  # Event registration page
    path('search', views.search_attendee, name='search_attendee'),
    path('print/<str:qr>/', views.print_name_tag, name='print_name_tag'),
    path('print/<int:qr>/', views.print_name_tag, name='print_name_tags'),
     path('print2/', views.print_name_tags, name='print_name_tags'),
    path('upload/', views.upload_name_tag_template, name='upload_template'),  # Correct function name
    path('success/', views.success, name='success'),  # Add this line

]
