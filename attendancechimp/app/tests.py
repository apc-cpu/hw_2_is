from django.contrib.auth.models import User
from django.test import Client, TestCase
from .models import InstructorProfile, StudentProfile


class RegistrationTests(TestCase):
    def signup(self, name='boris', role='1', email='boris@school.edu'):
        return self.client.post('/app/createUser', {
            'user_name': name, 'password': 'sk3j5n.k',
            'is_student': role, 'email': email,
        })

    def test_student_signup_and_authenticated_home(self):
        self.assertEqual(self.signup().status_code, 200)
        user = User.objects.get(username='boris')
        self.assertTrue(user.check_password('sk3j5n.k'))
        self.assertTrue(StudentProfile.objects.filter(user=user).exists())
        self.assertContains(self.client.get('/app/'), '<strong>boris</strong>')
        self.assertEqual(self.signup('other', email='BORIS@school.edu').status_code, 400)
        self.assertEqual(User.objects.count(), 1)

    def test_multiple_students_and_instructor(self):
        self.assertEqual(self.signup().status_code, 200)
        self.assertEqual(self.signup('anna', email='anna@school.edu').status_code, 200)
        self.assertEqual(self.signup('teacher', '0', 'teacher@school.edu').status_code, 200)
        self.assertEqual(StudentProfile.objects.count(), 2)
        self.assertEqual(InstructorProfile.objects.count(), 1)

    def test_methods_and_invalid_input(self):
        self.assertEqual(self.client.get('/app/createUser').status_code, 405)
        self.assertEqual(self.client.post('/app/new').status_code, 405)
        self.assertContains(self.client.get('/app/new'), 'name="is_student"')
        self.assertContains(self.client.get('/app/'), 'Not logged in.')
        self.assertEqual(self.client.post('/app/createUser', {}).status_code, 400)

    def test_plain_curl_and_csrf_protected_login(self):
        self.client = Client(enforce_csrf_checks=True)
        self.assertEqual(self.signup().status_code, 200)
        self.client.logout()
        self.assertEqual(self.client.get('/accounts/login/').status_code, 200)
        token = self.client.cookies['csrftoken'].value
        response = self.client.post('/accounts/login/', {
            'username': 'boris', 'password': 'sk3j5n.k',
            'csrfmiddlewaretoken': token, 'next': '/app/',
        })
        self.assertRedirects(response, '/app/')
        self.assertContains(self.client.get('/app/index.html'), '<strong>boris</strong>')
