import csv
from io import StringIO

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
                    hours, minutes, seconds = convert_timedelta(attendance.elapsed)
                    writer.writerow([
                        s.username, attendance.clock_in, attendance.clock_out,
                        f"{hours} hours {minutes} minutes {seconds} seconds"
                    ])

        f.seek(0)
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=stat-info.csv'
        return response
