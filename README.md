# מערכת שאלונים - Django Quiz System

מערכת לניהול והצגת שאלונים המאפשרת למשתמשים לענות על שאלונים ולמנהלים לנהל אותם.

## יכולות המערכת

### משתמש מנהל יכול:
- ליצור, לערוך ולמחוק שאלונים
- לנהל משתמשים
- לצפות בתשובות המשתמשים
- לראות סטטיסטיקות על השלמת השאלונים

### משתמש רגיל יכול:
- לראות רשימת שאלונים זמינים
- לענות על שאלונים
- לראות אילו שאלונים השלים

## התקנה והרצה

1. התקן את הדרישות:
```bash
pip install -r requirements.txt

הרץ migrations:

bashCopypython manage.py migrate

צור משתמש מנהל:

bashCopypython manage.py createsuperuser

הרץ את השרת:

bashCopypython manage.py runserver

גש לכתובות:


ממשק מנהל: http://127.0.0.1:8000/admin
ממשק משתמשים: http://127.0.0.1:8000

טכנולוגיות

Python
Django
HTML/CSS

תהנו!