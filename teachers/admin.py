from django.contrib import admin

from teachers.models import Class, Subject, Teacher


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("name", "institution", "teacher", "class_fee")


admin.site.register(Teacher)
admin.site.register(Subject)
