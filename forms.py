from django import forms
from django.contrib.auth.models import User
from .models import Student


class StudentForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    username = forms.CharField(max_length=150, required=False, help_text='Required for new students')
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text='Required for new students')

    field_order = [
        'first_name', 'last_name', 'username', 'password',
        'roll_number', 'admission_number', 'date_of_birth', 'gender',
        'address', 'phone', 'parent_name', 'parent_phone', 'parent_email',
        'class_room', 'is_active',
    ]

    class Meta:
        model = Student
        fields = [
            'roll_number', 'admission_number', 'date_of_birth', 'gender',
            'address', 'phone', 'parent_name', 'parent_phone', 'parent_email',
            'class_room', 'is_active',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            del self.fields['username']
            del self.fields['password']

    def clean(self):
        data = super().clean()
        if not self.instance.pk:
            username = data.get('username')
            if not username:
                self.add_error('username', 'Username is required for a new student.')
            elif User.objects.filter(username=username).exists():
                self.add_error('username', 'This username is already taken.')
            if not data.get('password'):
                self.add_error('password', 'Password is required for a new student.')
        return data

    def save(self, commit=True):
        student = super().save(commit=False)
        if student.pk:
            user = student.user
        else:
            user = User(username=self.cleaned_data['username'])
            user.set_password(self.cleaned_data['password'])
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data.get('last_name', '')
        user.save()
        student.user = user
        student.save()
        return student


from .models import Fee


class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ['student', 'amount', 'due_date', 'remarks']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }
