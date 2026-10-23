"""
models.py — Data model for AttendanceChimp.

AttendanceChimp is an electronic class attendance tool.  Instructors create
courses and lectures; each lecture is assigned a random QR code.  Students
photograph the QR code and upload the image.  The system decodes the QR code,
matches it to a lecture, and records the attendance.

Entities
--------
- CourseProfile   : extends Django User → instructor-specific data
- StudentProfile  : extends Django User → student-specific data
- Course          : a course taught by one instructor
- Enrollment      : junction table linking students to courses
- Lecture         : a single class meeting (has a QR-code identifier)
- QRCodeUpload    : a student's uploaded QR-code photograph
"""

from django.db import models
from django.contrib.auth.models import User

import logging
import string
import random

logger = logging.getLogger(__name__) # set up tracking, auditing, and debugging
                                                               # allows using logger.warning(), logger.error(), 
                                                               # logger.info(), etc. Better than print() for debuggin... 


# ---------------------------------------------------------------------------
# User profiles
# ---------------------------------------------------------------------------

class InstructorProfile(models.Model):
    """
    Stores instructor-specific information.
    Linked one-to-one with Django's built-in User model.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class StudentProfile(models.Model):
    """
    Stores student-specific information.
    Linked one-to-one with Django's built-in User model.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.user.username


# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------

class Course(models.Model):
    """
    Represents a course taught by one instructor.
    """

    name = models.CharField(max_length=200)
    instructor = models.ForeignKey(
        InstructorProfile,
        on_delete=models.CASCADE
    )
    meeting_schedule = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# Enrollment
# ---------------------------------------------------------------------------

class Enrollment(models.Model):
    """
    Links students and courses.
    """

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.student} - {self.course}"


# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------


class Lecture(models.Model):
    """
    Represents a lecture session for a course.
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    date = models.DateTimeField()

    qr_identifier = models.CharField(
        max_length=32,
        unique=True
    )

    def __str__(self):
        return f"{self.course.name} ({self.date})"

# ---------------------------------------------------------------------------
# QR Code Upload
# ---------------------------------------------------------------------------

class QRCodeUpload(models.Model):
    """
    Stores QR code images uploaded by students.
    """

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE
    )

    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    image_file = models.ImageField(upload_to="qr_uploads/")

    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Upload by {self.student}"


# ---------------------------------------------------------------------------
# Helper / API functions
# ---------------------------------------------------------------------------



