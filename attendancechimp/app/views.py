"""
views.py — HTTP request handlers for AttendanceChimp.

Each view corresponds to one URL endpoint.  Views receive an HTTP request,
interact with the database via models.py, and return an HTTP response.
"""

from django.shortcuts import render, redirect
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseBadRequest, JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db import IntegrityError, transaction
from django.views.decorators.http import require_GET, require_POST
from .models import InstructorProfile, StudentProfile
from datetime import datetime
import zoneinfo
import json
import io

# from .models import (InstructorProfile, StudentProfile, Course, Enrollment,
#                      Lecture, QRCodeUpload, is_instructor, is_student,
#                      getUploadsForCourse)

CDT = zoneinfo.ZoneInfo("America/Chicago")


# ---------------------------------------------------------------------------
# HW2  — index, time, sum
# ---------------------------------------------------------------------------

def index(request):
    """Render the home page (index.html)."""

    context = {current_time': datetime.now(CDT).strftime('%H:%M'),
               'user': request.user}
    return render(request, 'app/index.html', context)


def time_view(request):
    now = datetime.now(CDT)
    return HttpResponse(now.strftime("%H:%M"))


def sum_view(request):
    n1 = float(request.GET.get("n1"))
    n2 = float(request.GET.get("n2"))

    total = n1 + n2

    return HttpResponse(str(total))


# ---------------------------------------------------------------------------
# HW4  — user creation
# ---------------------------------------------------------------------------

@require_GET
def new(request):
    return render(request, 'app/new.html')


@csrf_exempt
@require_POST
def createUser(request):
    email = request.POST.get('email', '').strip()
    user_name = request.POST.get('user_name', '').strip()
    password = request.POST.get('password', '')
    is_student = request.POST.get('is_student')

    if not email or not user_name or not password or is_student not in ('0', '1'):
        return JsonResponse({'error': 'All fields and a valid role are required.'}, status=400)
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({'error': 'Email already registered.'}, status=400)
    if User.objects.filter(username=user_name).exists():
        return JsonResponse({'error': 'Username already registered.'}, status=400)

    try:
        with transaction.atomic():
            user = User.objects.create_user(username=user_name, email=email, password=password)
            if is_student == '1':
                StudentProfile.objects.create(user=user, student_id=str(user.pk))
            else:
                InstructorProfile.objects.create(user=user, department='')
    except IntegrityError:
        return JsonResponse({'error': 'User could not be created.'}, status=400)

    login(request, user)
    return JsonResponse({'success': True, 'user_name': user.username})


# ---------------------------------------------------------------------------
# HW5  — courses, lectures, QR uploads, dump
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------



