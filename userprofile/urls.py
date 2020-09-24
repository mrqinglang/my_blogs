from django.urls import path, re_path, include
from userprofile import views
app_name = 'userprofile'
urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('delete/<int:id>', views.user_delete, name='delete'),
    path('reset/', views.user_reset, name='reset'),
    path('forget/<str:token>', views.user_forget, name='forget'),
    path('forget1/', views.user_forget1, name='forget1'),
    path('edit/<int:id>/', views.profile_edit, name='edit'),

]
