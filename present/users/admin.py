from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Attendance


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 1


@admin.register(User)
class UserAdmin(UserAdmin):
    inlines = [AttendanceInline]
