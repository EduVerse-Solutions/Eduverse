from django.contrib import admin

from students.models import Guardian, Student

admin.site.register(Student)
admin.site.register(Guardian)
