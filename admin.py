from django.contrib import admin
from .models import (
    Department, ClassRoom, Student, Subject, ClassSubject,
    Attendance, Grade, ReportCard, Fee, Timetable,
)

admin.site.register(Department)
admin.site.register(ClassRoom)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(ClassSubject)
admin.site.register(Attendance)
admin.site.register(Grade)
admin.site.register(ReportCard)
admin.site.register(Fee)
admin.site.register(Timetable)