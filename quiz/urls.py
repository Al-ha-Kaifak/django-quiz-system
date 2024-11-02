

from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user-answers/<int:user_id>/<int:quiz_id>/', views.user_answers, name='user_answers'),
]