from django.urls import path
from . import views

urlpatterns = [
    path('crud/', views.crud_operations, name='crud_operations'),
    path('create_member/', views.create_member, name='create_member'),
    path('view_members/', views.view_members, name='view_members'),
    path('update_member/', views.update_member, name='update_member'),  # Update this pattern
    path('delete_member/', views.delete_member, name='delete_member'),  # Update this pattern
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home, name='home'),
      path('crud/', views.crud_operations, name='crud_operations'),
    path('delete_member/<str:email>/', views.delete_member, name='delete_member'),
    path('update_member/<str:email>/', views.update_member, name='update_member'),
   
]