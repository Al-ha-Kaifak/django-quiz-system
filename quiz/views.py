

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .models import Quiz, Question, Answer, UserQuizStatus
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'quiz/login.html')

@login_required
def dashboard(request):
    # קבל את כל השאלונים ומצבם עבור המשתמש
    all_quizzes = Quiz.objects.all()
    quiz_status = []
    has_incomplete_quizzes = False
    
    for quiz in all_quizzes:
        status, created = UserQuizStatus.objects.get_or_create(
            user=request.user,
            quiz=quiz
        )
        if not status.completed:
            has_incomplete_quizzes = True
        quiz_status.append({
            'quiz': quiz,
            'completed': status.completed
        })
    
    return render(request, 'quiz/dashboard.html', {
        'quiz_status': quiz_status,
        'has_incomplete_quizzes': has_incomplete_quizzes
    })

@login_required
def take_quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    
    if request.method == 'POST':
        # שמור את התשובות
        for question in quiz.questions.all():
            answer_text = request.POST.get(f'question_{question.id}')
            if answer_text:
                Answer.objects.create(
                    user=request.user,
                    question=question,
                    answer_text=answer_text
                )
        
        # סמן את השאלון כהושלם
        status = UserQuizStatus.objects.get(user=request.user, quiz=quiz)
        status.completed = True
        status.save()
        
        return redirect('dashboard')
    
    return render(request, 'quiz/take_quiz.html', {
        'quiz': quiz
    })
    

def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.filter(is_staff=False)  # רק משתמשים רגילים
    user_data = []
    
    for user in users:
        quizzes_data = []
        for quiz in Quiz.objects.all():
            status = UserQuizStatus.objects.filter(user=user, quiz=quiz).first()
            answers = Answer.objects.filter(user=user, question__quiz=quiz)
            
            quizzes_data.append({
                'quiz': quiz,
                'completed': status.completed if status else False,
                'answers': answers
            })
            
        user_data.append({
            'user': user,
            'quizzes': quizzes_data
        })
    
    return render(request, 'quiz/admin_dashboard.html', {
        'user_data': user_data
    })

@user_passes_test(is_admin)
def user_answers(request, user_id, quiz_id):
    user = User.objects.get(id=user_id)
    quiz = Quiz.objects.get(id=quiz_id)
    answers = Answer.objects.filter(user=user, question__quiz=quiz)
    
    return render(request, 'quiz/user_answers.html', {
        'user': user,
        'quiz': quiz,
        'answers': answers
    })
    
    
    