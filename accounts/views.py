import pprint
from datetime import date, datetime, timedelta
from . import forms
from django.core.mail import EmailMessage
from . tokens import generate_token
from miniproject import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.contrib.auth.decorators import login_required
from .models import Subject, TimeTable, AcademicCalendar, ImportantDates, Student
import csv


# Create your views here.
def home(request):
    return render(request, 'accounts/index.html')

def signup(request):
    if request.method == "POST":
        pprint.pprint(vars(request))
        username = request.POST.get('username')
        fname = request.POST['fname']
        lname = request.POST.get('lname')
        email = request.POST['email']
        pass1 = request.POST.get('pass1')
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exists! Please try some other username")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request, "Email already exists! Please try some other Email")
            return redirect('home')
        
        if len(username)>10:
            messages.error(request, "Username must be under 10 characters!")
            return redirect('home')
        
        if pass1!=pass2:
            messages.error(request, "Passwords didn't match!")
            return redirect('home')

        if not username.isalnum():
            messages.error(request, "Username must be alphanumeric!")
            return redirect('home')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = True
        myuser.save()

        # Create Student profile
        Student.objects.create(user=myuser, total_attendance=0.0)

        messages.success(request, "Your Account has been successfully created.")
        return redirect('signin')

    return render(request, 'accounts/signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass1')
        print("Username:", username)
        print("Password:", pass1)

        user = authenticate(request, username=username, password=pass1)
        print("User object:", user)

        # form = forms.InputTimeTable()

        if user is not None:
            login(request, user)
            # return render(request, "accounts/dashboard.html", {'fname': user.first_name, 'form':form})
            return render(request, "accounts/homepage.html", {'fname': user.first_name})
        else:
            return HttpResponse("Invalid credentials")
    
    return render(request, 'accounts/signin.html')


def signout(request):
    logout(request)
    messages.success(request, "Logged Out successfully")
    return redirect('home')

# def activate(request, uidb64, token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         myuser = User.objects.get(pk=uid)
#     except(TypeError, ValueError, OverflowError, User.DoesNotExist):
#         myuser = None

#     if myuser is not None and generate_token.check_token(myuser, token):
#         myuser.is_active = True
#         myuser.save()
#         login(request, myuser)
#         return redirect('home')
#     else:
#         return render(request, 'activation_failed.html')
    
# def user_input(request):
#     if request.method == 'POST':
#         pass
#     return render(request, 'accounts/dashboard.html')



@login_required 
def upload_acdcalendar(request):
    if request.method == "POST" and request.FILES.get("file"):
        csv_file = request.FILES["file"]

        # Check if it’s a CSV
        if not csv_file.name.endswith('.csv'):
            return render(request, "accounts/dashboard2.html", {"error": "Please upload a CSV file"})
        
        file_data = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(file_data)


        for row in reader:
            date_str = row.get('date', '')
            # Convert '30-08-2025' to a Python date object
            date_obj = datetime.strptime(date_str, '%d-%m-%Y').date() if date_str else None
            AcademicCalendar.objects.create(
                user=request.user,
                date=date_obj,
                context=row.get('context', '')
            )

        messages.success(request,"Successfully entered Academic Calendar in the database.")

        return redirect('insights')

    return render(request, "accounts/dashboard2.html")

def userprofile(request):
    return render(request,"accounts/userprofile.html")

# Test
@login_required 
def homepage(request):
    return render(request,"accounts/homepage.html")

@login_required 
def userinput(request):
    if request.method == "POST":
        if request.POST.get('totalSubjects') is not None:
            # Step 1: show form for subjects
            return render(request, "accounts/db1.html", {
                'totalSubjects': range(1, int(request.POST.get('totalSubjects')) + 1)
            })
        else:
            total_subjects = len([k for k in request.POST.keys() if k.startswith("subject") and not k.endswith("Faculty")])

            for index in range(1, total_subjects + 1):
                subject_name = request.POST.get(f"subject{index}")
                faculty_name = request.POST.get(f"subject{index}Faculty")
                total_hours = int(request.POST.get(f"total_hours{index}"))
                hours_attended = int(request.POST.get(f"hours_attended{index}"))
                attendance = round((hours_attended/total_hours)*100,2)

                if subject_name and faculty_name:
                    Subject.objects.create(
                        subjectName=subject_name,
                        facultyName=faculty_name,
                        total_hours=total_hours,
                        hours_attended=hours_attended,
                        attendance=attendance,
                        user=request.user
                    )

            return render(request, "accounts/db2.html")

    return render(request, "accounts/db1.html", {'totalSubjects': None})

@login_required  # ensures only signed-in users can access
def upload_timetable(request):
    if request.method == "POST" and request.FILES.get("file"):
        csv_file = request.FILES["file"]

        # Check if it’s a CSV
        if not csv_file.name.endswith('.csv'):
            return render(request, "accounts/db2.html")

        # Read CSV file
        file_data = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(file_data)

        # Loop through rows and create Timetable entries
        for row in reader:

            subject_name = row['Subject']  # string from CSV
            subject_instance = Subject.objects.get(subjectName=subject_name)
            TimeTable.objects.create(
                user=request.user, # link to logged-in user
                day=row['Day'],
                startTime=row['StartTime'],
                endTime=row['EndTime'],
                subject=subject_instance 
                        
                # time=row['Time'],           # ensure CSV has column 'time'
                # monday=row.get('Monday', ''),
                # tuesday=row.get('Tuesday', ''),
                # wednesday=row.get('Wednesday', ''),
                # thursday=row.get('Thursday', ''),
                # friday=row.get('Friday', '')
            )

        messages.success(request,"Successfully entered the timetable in the database. Upload Academic Calendar!")

        return render(request, "accounts/db3.html") 
    return render(request, "accounts/db2.html")


@login_required  # ensures only signed-in users can access
def upload_academiccalendar(request):
    if request.method == "POST" and request.FILES.get("file"):
        csv_file = request.FILES["file"]

        # Check if it’s a CSV
        if not csv_file.name.endswith('.csv'):
            return render(request, "accounts/db3.html")

        # Read CSV file
        file_data = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(file_data)

        # Loop through rows and create Timetable entries
        for row in reader:
            AcademicCalendar.objects.create(
                user=request.user, # link to logged-in user
                date=row['date'],
                context=row['context'])

        messages.success(request,"Successfully entered the Academic Calendar in the database!")
        return redirect('db4') 
        # semStart = AcademicCalendar.objects.filter(user=request.user,context__iexact = 'semStart').first()
        # semEnd = AcademicCalendar.objects.filter(user=request.user,context__iexact = 'semEnd').first()

        # current = semStart.date
        # enddate = semEnd.date
        # count = 0

        # while current<=enddate:
        #     while current <= enddate:
        #         # if current == datetime(2025,10,5):
        #         #     current = current + timedelta(days=1)
        #         #     continue
        #         print(current)
        #         current = current + timedelta(days=1)
        #         count = count + 1

        # if semStart is not None or semEnd is not None:
        #     return render(request, "accounts/db4.html",{'semStart': semStart, 'semEnd': semEnd, 'count':count}) 
    return render(request, "accounts/db3.html")


@login_required
def continue_tracking(request):
    user = AcademicCalendar.objects.filter(user=request.user).exists()
    if user == True:
        return calculations(request)
    else:
        messages.error(request, "No Entries Found!")
        return render(request, "accounts/homepage.html")


@login_required # Calculate total lectures from start to end of semester
def calculations(request):
    semStart = AcademicCalendar.objects.filter(user=request.user,context__iexact = 'semStart').first()
    semEnd = AcademicCalendar.objects.filter(user=request.user,context__iexact = 'semEnd').first()

    print("semStart:", semStart)
    print("semEnd:", semEnd)

    current = semStart.date
    enddate = semEnd.date
    count = 2 # Count starts from two because We are considering Semester start date and end date as well

    while current<=enddate:
        flag = AcademicCalendar.objects.filter(date=current).exists()
        if flag == False:
            count = count + 1
        current = current + timedelta(days=1)

    user = request.user
    sub = Subject.objects.filter(user=user)
# HArd way 
    # subjects = []
    
    # for i in sub:
    #     subjects.append(i)

# Easy way
    subjects = list(Subject.objects.filter(user=request.user))

    total_hrs = 0 # total Hours of all subject
    total_attended_hrs = 0 # total hours attended in all subjects
    for s in sub:
        total_hrs += s.total_hours
        total_attended_hrs += s.hours_attended

    total_attendance = round((total_attended_hrs/total_hrs)*100,2)
    
    Student.objects.filter(user=request.user).update(total_attendance = total_attendance)
    
    remaining_hours = []
    temp = []

    for s in subjects:
        today = date.today()
        current_id = s.id
        subject_count = 0
        while today<=enddate:
            exists = AcademicCalendar.objects.filter(user=request.user, date=today).exists()
            if exists == False:
                if today.weekday()==0:
                    subject_count += TimeTable.objects.filter(user=request.user, day__iexact='monday', subject_id=current_id).count()
                elif today.weekday()==1:
                    subject_count += TimeTable.objects.filter(user=request.user, day__iexact='tuesday', subject_id=current_id).count()
                elif today.weekday()==2:
                    subject_count += TimeTable.objects.filter(user=request.user, day__iexact='wednesday', subject_id=current_id).count()
                elif today.weekday()==3:
                    subject_count += TimeTable.objects.filter(user=request.user, day__iexact='thursday', subject_id=current_id).count()
                elif today.weekday()==4:
                    subject_count += TimeTable.objects.filter(user=request.user, day__iexact='friday', subject_id=current_id).count()
            today = today + timedelta(days=1)
        remaining_hours.append((subject_count,s.subjectName))
        temp.append(subject_count)

    status = []

    for index,s in enumerate(subjects):
        if s.attendance < 75:
            # x = round(((0.75 * (s.total_hours+temp[index]))-s.hours_attended),2)
            x = round(((0.75*s.total_hours-s.hours_attended)/0.25),2)
            if x<=temp[index]:
                status.append((int(x),"must attend",s.subjectName))
            else:
                status.append((-1,"never",s.subjectName))
        else:
            # x = round(((s.hours_attended+temp[index])-(0.75*(s.total_hours+temp[index]))),2)
            x = round(((s.hours_attended-0.75*s.total_hours)/0.75),2)
            status.append((int(x),"can miss",s.subjectName))



    today = date.today()
    if today.weekday()==0:
        todaysubjects = list(TimeTable.objects.filter(user=request.user, day__iexact='monday'))
    elif today.weekday()==1:
        todaysubjects = list(TimeTable.objects.filter(user=request.user, day__iexact='tuesday'))
    elif today.weekday()==2:
        todaysubjects = list(TimeTable.objects.filter(user=request.user, day__iexact='wednesday'))
    elif today.weekday()==3:
        todaysubjects = list(TimeTable.objects.filter(user=request.user, day__iexact='thursday'))
    elif today.weekday()==4:
        todaysubjects = list(TimeTable.objects.filter(user=request.user, day__iexact='friday'))

    session_key = f"attendance_updated_{today.isoformat()}"
    flag = request.session.get(session_key, False)  # True if already updated today

    # Get upcoming events (next 4 weeks)
    today = date.today()
    four_weeks_later = today + timedelta(weeks=4)
    
    upcoming_events_query = ImportantDates.objects.filter(
        user=request.user,
        date__gte=today,
        date__lte=four_weeks_later
    ).order_by('date')
    
    upcoming_events = []
    for event in upcoming_events_query:
        days_left = (event.date - today).days
        upcoming_events.append({
            'date': event.date.strftime('%b %d, %Y'),
            'event': event.context,
            'days_left': days_left
        })
    
    return render(request, "accounts/db4.html",
                  {'semStart': semStart,
                    'semEnd': semEnd, 
                    'count':count,
                    'subjects':subjects,
                    'total_attendance':total_attendance,
                    'total_hrs':total_hrs,
                    'total_attended_hrs':total_attended_hrs,
                    'remaining_hours':remaining_hours,
                    'status':status,
                    'todaysubjects':todaysubjects,
                    'flag':flag,
                    'upcoming_events':upcoming_events,
                    })
                
    
    # return render(request, "accounts/db4.html",
    #               {'semStart': semStart,
    #                 'semEnd': semEnd, 
    #                 'count':count,
    #                 'subjects':subjects,
    #                 'total_attendance':total_attendance,
    #                 'total_hrs':total_hrs,
    #                 'total_attended_hrs':total_attended_hrs,
    #                 'remaining_hours':remaining_hours,
    #                 'status':status,
    #                 'todaysubjects':todaysubjects,
    #                 'flag':flag,
    #                 })

@login_required
def update_attendance(request):
    user = request.user
    today = date.today()
    today_key = f"attendance_updated_{today.isoformat()}"  # session key

    if today.weekday()==0:
        todaysubjects = list(TimeTable.objects.filter(user=user, day__iexact='monday'))
    elif today.weekday()==1:
        todaysubjects = list(TimeTable.objects.filter(user=user, day__iexact='tuesday'))
    elif today.weekday()==2:
        todaysubjects = list(TimeTable.objects.filter(user=user, day__iexact='wednesday'))
    elif today.weekday()==3:
        todaysubjects = list(TimeTable.objects.filter(user=user, day__iexact='thursday'))
    elif today.weekday()==4:
        todaysubjects = list(TimeTable.objects.filter(user=user, day__iexact='friday'))

    if request.method == "POST":
        if request.session.get(today_key):
            messages.info(request, "Already updated today's attendance")
            return redirect('db4')

        for value in todaysubjects:
            if str(value.subject) in request.POST:
                # sub = TimeTable.objects.get(subject=value.subject,user=user,startTime=value.startTime,day=value.day)
                temp = Subject.objects.get(subjectName=value.subject,user=user)
                temp.total_hours += 1
                temp.hours_attended += 1
                temp.attendance = round((temp.hours_attended/temp.total_hours)*100,2)
                temp.save()
            else:
                # sub = TimeTable.objects.get(subject=value.subject,user=user,startTime=value.startTime,day=value.day)
                temp = Subject.objects.get(subjectName=value.subject,user=user)
                temp.total_hours += 1
                temp.attendance = round((temp.hours_attended/temp.total_hours)*100,2)
                temp.save()
            
        request.session[today_key] = True
        messages.success(request, "Successfully updated today's attendance")
        return redirect('db4')

    return render(request,"accounts/markattendance.html",{'todaysubjects':todaysubjects})

@login_required
def updateattendance(request):
    sub = list(Subject.objects.filter(user=request.user))
    if request.method == "POST":
        for s in sub:
            var1 = int(request.POST.get(f"{s.subjectName}_total_hrs"))
            var2 = int(request.POST.get(f"{s.subjectName}_attended_hrs"))
            Subject.objects.filter(user=request.user, subjectName=s.subjectName).update(total_hours=var1, hours_attended=var2, attendance=round((var2/var1)*100,2))

        return calculations(request)

    return render(request, "accounts/updateattendance.html",{'sub':sub})

@login_required
def updatecalendar(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        context = request.POST.get('context')
        AcademicCalendar.objects.create(user=request.user,
                                        date=date,
                                        context=context)
        
        messages.success(request,"Successfully updated Academic Calendar!")
        return render(request, "accounts/updatecalendar.html")
    return render(request, "accounts/updatecalendar.html")
    

@login_required
def important_events(request):
    if request.method == 'POST':
        date = request.POST.get('impdate')
        event = request.POST.get('event')
        ImportantDates.objects.create(user=request.user,
                                        date=date,
                                        context=event)
        
        messages.success(request,"Successfully updated Important Dates!")
        return render(request, "accounts/updatecalendar.html")
    return render(request, "accounts/updatecalendar.html")