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

    return Response("Have a great day")


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

    return Response(f"Elapsed Time: {str(attendance[0].elapsed)}")


@api_view(['POST'])
def elapsed(request):
    user = User.objects.get(global_id=request.data.get('user_id'))
    attendance = user.attendance.all()

    return Response(f"{attendance[0].elapsed}")
