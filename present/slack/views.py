import os
import requests

from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

from present.users.models import User, Attendance


token = os.getenv('SLACK_TOKEN')


@csrf_exempt
@api_view(['POST'])
def challenge(request):
    print(request.data)
    return Response(request.data.get('challenge'))


@api_view(['POST'])
def clock_in(request):
    # get the current time before any execution happens
    now = timezone.now()

    user, _ = User.objects.get_or_create(
        global_id=request.data.get('user_id'),
        defaults={
            'username': request.data.get('user_name'),
            'password': request.data.get('user_id'),
        }
    )

    # check if user has an existing clockin that has no clockout
    if len(user.attendance.filter(clock_out=None)) > 0:
        return Response("may existing clockin ka pa man")
    
    data = {
        'clock_in': now,
        'clock_out': None,
    }

    user.attendance.create(**data)

    response = {
        "response_type": "ephemeral",
        "text": "You have clocked-in for today.",
        "attachments": [
            {
                "text": "to clock-out type `/clock-out`"
            },
            {
                "text": "to check elapsed time type `/elapsed`"
            }
        ]
    }

    return Response(response)


@api_view(['POST'])
def clock_out(request):
    # get the current time before any execution happens
    now = timezone.now()

    user = User.objects.get(global_id=request.data.get('user_id'))

    attendance = user.attendance.filter(clock_out=None)

    if not attendance:
        return Response("wala kang existing na clockin")

    attendance[0].clock_out = now
    attendance[0].save()

    hours, minutes, seconds = convert_timedelta(attendance[0].elapsed)

    response = {
        "response_type": "ephemeral",
        "text": "You have clocked-out for today. See you soon!",
        "attachments": [
            {
                "text": f"Total Time: {hours} hours {minutes} minutes {seconds} seconds"
            }
        ]
    }

    return Response(response)


@api_view(['POST'])
def elapsed(request):
    user = User.objects.get(global_id=request.data.get('user_id'))
    attendance = user.attendance.order_by('-id')

    hours, minutes, seconds = convert_timedelta(attendance[0].elapsed)

    response = {
        "response_type": "ephemeral",
        "text": f"Elapsed Time: {hours} hours {minutes} minutes {seconds} seconds",
    }

    return Response(response)


def convert_timedelta(duration):
    seconds = duration.total_seconds()
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return hours, minutes, seconds
