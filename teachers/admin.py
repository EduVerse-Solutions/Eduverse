from django.contrib import admin

from teachers.models import Class, Subject, Teacher

admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(Class)
