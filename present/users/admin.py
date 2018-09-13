import csv
from io import StringIO
from datetime import timedelta

from django.http import HttpResponse
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Attendance
from present.slack.views import convert_timedelta


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 1


@admin.register(User)
class UserAdmin(UserAdmin):
    actions = ['download_csv']
    inlines = [AttendanceInline]

    def download_csv(self, request, queryset):
        f = StringIO()
        writer = csv.writer(f)
        writer.writerow(["username", "clockin", "clockout", "elapsed"])

        for s in queryset:
            attendances = s.attendance.order_by('-id')
            if attendances:
                for attendance in attendances:
                    if attendance.clock_in and attendance.clock_out:
                        hours, minutes, seconds = convert_timedelta(attendance.elapsed)
                        clock_in = attendance.clock_in + timedelta(hours=8)
                        clock_out = attendance.clock_out + timedelta(hours=8)
                        writer.writerow([
                            s.username, clock_in, clock_out,
                            f"{hours} hours {minutes} minutes {seconds} seconds"
                        ])

        f.seek(0)
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=attendance.csv'
        return response
