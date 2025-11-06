from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    total_attendance = models.DecimalField(null=True, max_digits=5, decimal_places=2)
    enrollment_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.total_attendance}%"
    
    class Meta:
        db_table = "Student"


# class Timetable(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="timetables")
#     slot = models.AutoField(primary_key=True)
#     time = models.TimeField()
#     monday = models.CharField(max_length=20, blank=True, null=True)
#     tuesday = models.CharField(max_length=20, blank=True, null=True)
#     wednesday = models.CharField(max_length=20, blank=True, null=True)
#     thursday = models.CharField(max_length=20, blank=True, null=True)
#     friday = models.CharField(max_length=20, blank=True, null=True)

#     class Meta:
#         db_table = "timetable"

class AcademicCalendar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="AcademicCalendars")
    date = models.DateField()
    context = models.CharField(max_length=50)

    class Meta:
        db_table = "AcademicCalendar"


class Subject(models.Model):
    subjectName = models.CharField(max_length=30, null=False)
    facultyName = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subjects")
    total_hours = models.IntegerField(null=True)
    hours_attended = models.IntegerField(null=True)
    attendance = models.DecimalField(null=True,max_digits=5,decimal_places=2)

    def __str__(self):
        return self.subjectName
    
    class Meta:
        db_table = "Subject"

class TimeTable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="timetables")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="timetables")
    day = models.CharField(max_length=10,null=False)
    startTime = models.TimeField(null=False)
    endTime = models.TimeField(null=False)

    def __str__(self):
        return f"{self.subject.subjectName} on {self.day} at {self.startTime}" 
    
    class Meta:
        db_table = "TimeTable"

class ImportantDates(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="importantdates")
    date = models.DateField()
    context = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.context} on {self.date}" 
    class Meta:
        db_table = "ImportantDates"