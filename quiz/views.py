from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Quiz, Question, Answer, UserQuizStatus
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # אם המשתמש הוא מנהל, הפנה לדף הניהול
            if user.is_staff:
                return redirect('manager_dashboard')
            # אחרת, הפנה לדשבורד הרגיל
            return redirect('dashboard')
    return render(request, 'quiz/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    all_quizzes = Quiz.objects.all()
    quiz_status = []
    has_incomplete_quizzes = False
    
    for quiz in all_quizzes:
        # בדוק אם המשתמש מורשה לראות את השאלון
        if quiz.is_public or request.user in quiz.assigned_users.all():
            status, created = UserQuizStatus.objects.get_or_create(
                user=request.user,
                quiz=quiz,
                defaults={'completed': False}
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

@login_required
def manager_dashboard(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    users = User.objects.filter(is_staff=False)
    quizzes = Quiz.objects.all()
    
    # סטטיסטיקות בסיסיות
    total_answers = Answer.objects.count()
    completed_quizzes = UserQuizStatus.objects.filter(completed=True).count()
    
    return render(request, 'quiz/manager/dashboard.html', {
        'users': users,
        'quizzes': quizzes,
        'total_answers': total_answers,
        'completed_quizzes': completed_quizzes
    })

@login_required
def manage_users(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    if request.method == 'POST' and 'delete_user' in request.POST:
        user_id = request.POST.get('delete_user')
        User.objects.filter(id=user_id).delete()
        messages.success(request, 'המשתמש נמחק בהצלחה')
        
    users = User.objects.filter(is_staff=False)
    return render(request, 'quiz/manager/users.html', {'users': users})

@login_required
def create_user(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email', '')
        
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(username=username, password=password, email=email)
            messages.success(request, 'המשתמש נוצר בהצלחה')
            return redirect('manage_users')
        else:
            messages.error(request, 'שם המשתמש כבר קיים במערכת')
    
    return render(request, 'quiz/manager/create_user.html')

@login_required
def manage_quizzes(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    if request.method == 'POST' and 'delete_quiz' in request.POST:
        quiz_id = request.POST.get('delete_quiz')
        Quiz.objects.filter(id=quiz_id).delete()
        messages.success(request, 'השאלון נמחק בהצלחה')
    
    quizzes = Quiz.objects.all()
    regular_users = User.objects.filter(is_staff=False)
    
    for quiz in quizzes:
        completed_count = UserQuizStatus.objects.filter(quiz=quiz, completed=True).count()
        quiz.completed_count = completed_count
        quiz.user_statuses = []
        
        for user in regular_users:
            status = UserQuizStatus.objects.filter(quiz=quiz, user=user).first()
            quiz.user_statuses.append({
                'user': user,
                'completed': status.completed if status else False
            })
    
    return render(request, 'quiz/manager/quizzes.html', {
        'quizzes': quizzes
    })
    
@login_required
def create_quiz(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        questions = request.POST.getlist('questions[]')
        visibility = request.POST.get('visibility')
        
        if title and questions:
            quiz = Quiz.objects.create(
                title=title,
                is_public=(visibility == 'public')
            )
            
            # יצירת שאלות
            for question_text in questions:
                if question_text.strip():
                    Question.objects.create(quiz=quiz, text=question_text)
            
            # הגדרת הרשאות משתמשים
            if visibility == 'specific':
                selected_users = request.POST.getlist('users')
                quiz.assigned_users.set(User.objects.filter(id__in=selected_users))
            
            messages.success(request, 'השאלון נוצר בהצלחה')
            return redirect('manage_quizzes')
        else:
            messages.error(request, 'נא למלא את כל השדות הנדרשים')
    
    return render(request, 'quiz/manager/create_quiz.html', {
        'all_users': User.objects.filter(is_staff=False)
    })

@login_required
def edit_quiz(request, quiz_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        questions = request.POST.getlist('questions[]')
        
        if title:
            quiz.title = title
            quiz.save()
            
            # מחיקת כל השאלות הישנות
            quiz.questions.all().delete()
            
            # יצירת שאלות חדשות
            for question_text in questions:
                if question_text.strip():
                    Question.objects.create(quiz=quiz, text=question_text)
            
            # איפוס סטטוס ההשלמה של כל המשתמשים
            UserQuizStatus.objects.filter(quiz=quiz).update(completed=False)
                    
            messages.success(request, 'השאלון עודכן בהצלחה. כל המשתמשים יצטרכו לענות עליו מחדש.')
            return redirect('manage_quizzes')
            
    return render(request, 'quiz/manager/edit_quiz.html', {'quiz': quiz})

@login_required
def view_user_quizzes(request, user_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    all_quizzes = Quiz.objects.all()
    user_quiz_statuses = UserQuizStatus.objects.filter(user=user)
    
    completed_quizzes = []
    pending_quizzes = []
    unavailable_quizzes = []
    
    for quiz in all_quizzes:
        status = user_quiz_statuses.filter(quiz=quiz).first()
        
        if status and status.completed:
            completed_quizzes.append({
                'quiz': quiz,
                'is_public': quiz.is_public
            })
        elif quiz.is_public or user in quiz.assigned_users.all():
            pending_quizzes.append({
                'quiz': quiz,
                'is_public': quiz.is_public
            })
        else:
            unavailable_quizzes.append({
                'quiz': quiz,
                'is_public': quiz.is_public
            })
    
    return render(request, 'quiz/manager/user_quizzes.html', {
        'viewed_user': user,
        'completed_quizzes': completed_quizzes,
        'pending_quizzes': pending_quizzes,
        'unavailable_quizzes': unavailable_quizzes
    })

@login_required
@csrf_protect
def update_user_quizzes(request, user_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        action = request.POST.get('action')
        quiz_id = request.POST.get('quiz_id')
        
        if quiz_id:
            quiz = get_object_or_404(Quiz, id=quiz_id)
            
            if action == 'remove':
                if quiz.is_public:
                    quiz.assigned_users.add(user)
                    quiz.is_public = False
                    quiz.save()
                else:
                    quiz.assigned_users.remove(user)
                    
            elif action == 'add':
                quiz.assigned_users.add(user)
    
    return redirect('view_user_quizzes', user_id=user_id)

@login_required
@csrf_protect
def update_quiz_visibility(request, quiz_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        try:
            visibility = request.POST.get('visibility')
            quiz.is_public = (visibility == 'public')
            quiz.save()
            
            if not quiz.is_public:
                selected_users = request.POST.getlist('users')
                quiz.assigned_users.set(User.objects.filter(id__in=selected_users))
            else:
                quiz.assigned_users.clear()
                
            messages.success(request, 'הגדרות השאלון עודכנו בהצלחה')
        except Exception as e:
            messages.error(request, f'שגיאה בעדכון ההגדרות: {str(e)}')
    
    return redirect('manage_quizzes')

@login_required
def view_quiz_answers(request, user_id, quiz_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    quiz = get_object_or_404(Quiz, id=quiz_id)
    answers = Answer.objects.filter(user=user, question__quiz=quiz)
    
    return render(request, 'quiz/manager/quiz_answers.html', {
        'viewed_user': user,
        'quiz': quiz,
        'answers': answers
    })

@login_required
def edit_user(request, user_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    user_to_edit = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        notes = request.POST.get('notes')
        
        if username and username != user_to_edit.username:
            if not User.objects.filter(username=username).exists():
                user_to_edit.username = username
            else:
                messages.error(request, 'שם משתמש זה כבר קיים במערכת')
                return redirect('edit_user', user_id=user_id)
        
        if email:
            user_to_edit.email = email
            
        if new_password:
            user_to_edit.set_password(new_password)
        
        # עדכון פתקים
        notes_obj, created = UserNotes.objects.get_or_create(user=user_to_edit)
        notes_obj.notes = notes
        notes_obj.save()
            
        user_to_edit.save()
        return redirect('manage_users')
        
    return render(request, 'quiz/manager/edit_user.html', {
        'edited_user': user_to_edit
    })



