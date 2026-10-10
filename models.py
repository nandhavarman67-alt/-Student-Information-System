from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ClassRoom(models.Model):
    name = models.CharField(max_length=50)
    section = models.CharField(max_length=10)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='classes')
    academic_year = models.CharField(max_length=20)
    class_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='class_teacher')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.section}"


class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=20, unique=True)
    admission_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=15)
    parent_email = models.EmailField(blank=True)
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='students')
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.roll_number})"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    credits = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ClassSubject(models.Model):
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='class_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='teaching_subjects')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['class_room', 'subject']

    def __str__(self):
        return f"{self.class_room} - {self.subject}"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    remarks = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'class_subject', 'date']
        ordering = ['-date']

    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.student} - {self.date} - {status}"


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=100)  # Mid-term, Final, Quiz, etc.
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    grade = models.CharField(max_length=5, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.marks_obtained is not None and self.total_marks:
            self.percentage = (self.marks_obtained / self.total_marks) * 100
            if self.percentage >= 90:
                self.grade = 'A+'
            elif self.percentage >= 80:
                self.grade = 'A'
            elif self.percentage >= 70:
                self.grade = 'B'
            elif self.percentage >= 60:
                self.grade = 'C'
            elif self.percentage >= 50:
                self.grade = 'D'
            else:
                self.grade = 'F'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.exam_name} - {self.grade}"


class ReportCard(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='report_cards')
    term = models.CharField(max_length=50)
    academic_year = models.CharField(max_length=20)
    generated_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='report_cards/', blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.first_name} - {self.term}"


class Fee(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    receipt_number = models.CharField(max_length=50, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} - {self.amount}"


class Timetable(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ]

    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='timetables')
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    period = models.IntegerField()
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['class_room', 'day', 'period']

    def __str__(self):
        return f"{self.class_room} - {self.day} - Period {self.period}"
