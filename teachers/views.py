from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from accounts.models import Subject, Student, AcademicCalendar, TimeTable, ImportantDates
from .models import Teacher

def teacher_home(request):
    """Landing page for teachers"""
    return render(request, 'teachers/index.html')

def teacher_signup(request):
    """Teacher registration"""
    if request.method == "POST":
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        employee_id = request.POST.get('employee_id')
        department = request.POST.get('department')
        phone = request.POST.get('phone', '')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('teacher_signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('teacher_signup')
        
        if Teacher.objects.filter(employee_id=employee_id).exists():
            messages.error(request, "Employee ID already exists!")
            return redirect('teacher_signup')
        
        if len(username) > 10:
            messages.error(request, "Username must be under 10 characters!")
            return redirect('teacher_signup')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't match!")
            return redirect('teacher_signup')

        if not username.isalnum():
            messages.error(request, "Username must be alphanumeric!")
            return redirect('teacher_signup')

        # Create user
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = True
        myuser.save()

        # Create teacher profile
        Teacher.objects.create(
            user=myuser,
            employee_id=employee_id,
            department=department,
            phone=phone
        )

        messages.success(request, "Teacher account created successfully!")
        return redirect('teacher_signin')

    return render(request, 'teachers/signup.html')

def teacher_signin(request):
    """Teacher login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass1')

        user = authenticate(request, username=username, password=pass1)

        if user is not None:
            # Check if user is a teacher
            try:
                teacher = Teacher.objects.get(user=user)
                login(request, user)
                return redirect('teacher_dashboard')
            except Teacher.DoesNotExist:
                messages.error(request, "You are not registered as a teacher!")
                return redirect('teacher_signin')
        else:
            messages.error(request, "Invalid credentials!")
            return redirect('teacher_signin')
    
    return render(request, 'teachers/signin.html')

@login_required
def teacher_dashboard(request):
    """Dashboard showing all students"""
    # Check if logged-in user is a teacher
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, "Access denied. Teachers only.")
        return redirect('home')
    
    # Get all users who have student profiles and subjects
    students_data = []
    
    # Get all users who have subjects (meaning they are students using the system)
    users_with_subjects = User.objects.filter(subjects__isnull=False).distinct()
    
    for user in users_with_subjects:
        subjects = Subject.objects.filter(user=user)
        if subjects.exists():
            total_hrs = sum(s.total_hours for s in subjects)
            total_attended = sum(s.hours_attended for s in subjects)
            overall_attendance = round((total_attended / total_hrs * 100), 2) if total_hrs > 0 else 0
            
            # Get or create student profile
            student_profile, created = Student.objects.get_or_create(
                user=user,
                defaults={'total_attendance': overall_attendance}
            )
            
            # Update attendance if not created
            if not created:
                student_profile.total_attendance = overall_attendance
                student_profile.save()
            
            students_data.append({
                'user': user,
                'student': student_profile,
                'overall_attendance': overall_attendance,
                'subject_count': subjects.count(),
                'total_hours': total_hrs,
                'attended_hours': total_attended
            })
    
    # Sort by attendance (lowest first to identify at-risk students)
    students_data.sort(key=lambda x: x['overall_attendance'])
    
    return render(request, 'teachers/dashboard.html', {
        'teacher': teacher,
        'students': students_data,
        'total_students': len(students_data)
    })

@login_required
def student_detail(request, student_id):
    """Detailed view of individual student"""
    # Check if logged-in user is a teacher
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, "Access denied. Teachers only.")
        return redirect('home')
    
    student_user = get_object_or_404(User, id=student_id)
    subjects = Subject.objects.filter(user=student_user).order_by('attendance')
    
    total_hrs = sum(s.total_hours for s in subjects) if subjects.exists() else 0
    total_attended = sum(s.hours_attended for s in subjects) if subjects.exists() else 0
    overall_attendance = round((total_attended / total_hrs * 100), 2) if total_hrs > 0 else 0
    
    # Get academic calendar info
    sem_start = AcademicCalendar.objects.filter(user=student_user, context__iexact='semStart').first()
    sem_end = AcademicCalendar.objects.filter(user=student_user, context__iexact='semEnd').first()
    
    # Get timetable
    timetable = {}
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    for day in days:
        timetable[day] = TimeTable.objects.filter(user=student_user, day__iexact=day).order_by('startTime')
    
    # Calculate subjects at risk (below 75%)
    at_risk_subjects = subjects.filter(attendance__lt=75)
    good_subjects = subjects.filter(attendance__gte=75)
    
    # Get upcoming important dates
    today = date.today()
    four_weeks_later = today + timedelta(weeks=4)
    upcoming_events = ImportantDates.objects.filter(
        user=student_user,
        date__gte=today,
        date__lte=four_weeks_later
    ).order_by('date')
    
    # Calculate status for each subject
    subject_status = []
    for s in subjects:
        if sem_end:
            # Calculate remaining classes
            current = date.today()
            enddate = sem_end.date
            subject_count = 0
            
            while current <= enddate:
                exists = AcademicCalendar.objects.filter(user=student_user, date=current).exists()
                weekday = current.weekday()
                # Only process weekdays (Monday-Friday)
                if not exists and weekday < 5:  # weekday < 5 means Monday-Friday
                    day_name = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'][weekday]
                    subject_count += TimeTable.objects.filter(
                        user=student_user, 
                        day__iexact=day_name, 
                        subject_id=s.id
                    ).count()
                current = current + timedelta(days=1)
            
            if s.attendance < 75:
                classes_needed = round(((0.75 * s.total_hours - s.hours_attended) / 0.25), 2)
                if classes_needed <= subject_count:
                    status = f"Must attend {int(classes_needed)} more classes"
                    status_type = "danger"
                else:
                    status = "Cannot reach 75% - Too many missed"
                    status_type = "critical"
            else:
                can_miss = round(((s.hours_attended - 0.75 * s.total_hours) / 0.75), 2)
                status = f"Can miss {int(can_miss)} more classes"
                status_type = "safe"
            
            subject_status.append({
                'subject': s,
                'remaining_classes': subject_count,
                'status': status,
                'status_type': status_type
            })
        else:
            subject_status.append({
                'subject': s,
                'remaining_classes': 0,
                'status': 'No semester end date set',
                'status_type': 'warning'
            })
    
    return render(request, 'teachers/student_detail.html', {
        'teacher': teacher,
        'student_user': student_user,
        'subjects': subjects,
        'overall_attendance': overall_attendance,
        'total_hrs': total_hrs,
        'total_attended': total_attended,
        'sem_start': sem_start,
        'sem_end': sem_end,
        'timetable': timetable,
        'at_risk_subjects': at_risk_subjects,
        'good_subjects': good_subjects,
        'upcoming_events': upcoming_events,
        'subject_status': subject_status
    })

@login_required
def teacher_signout(request):
    """Teacher logout"""
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('teacher_home')