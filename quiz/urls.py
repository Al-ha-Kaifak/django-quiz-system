from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('logout/', views.logout_view, name='logout'),
    
    # נתיבי מנהל
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/users/', views.manage_users, name='manage_users'),
    path('manager/users/create/', views.create_user, name='create_user'),
    path('manager/users/<int:user_id>/quizzes/', views.view_user_quizzes, name='view_user_quizzes'),
    path('manager/users/<int:user_id>/update-quizzes/', views.update_user_quizzes, name='update_user_quizzes'),  # חדש
    path('manager/quizzes/', views.manage_quizzes, name='manage_quizzes'),
    path('manager/quizzes/create/', views.create_quiz, name='create_quiz'),
    path('manager/quizzes/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('manager/quizzes/<int:quiz_id>/visibility/', views.update_quiz_visibility, name='update_quiz_visibility'),
    path('manager/users/<int:user_id>/quiz/<int:quiz_id>/answers/', views.view_quiz_answers, name='view_quiz_answers'),
    path('manager/users/<int:user_id>/edit/', views.edit_user, name='edit_user'),




]