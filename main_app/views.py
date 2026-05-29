import json
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt

from .EmailBackend import EmailBackend
# from .models import Attendance, Session, Subject
from .models import (
    CustomUser,
    Student,
    Staff,
    Course,
    Session,
    StudentMaster
)
# Create your views here.
def home(request):
    return render(request, 'main_app/home.html')

def faculty(request):
    return render(request, 'main_app/faculty.html')

def login_page(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("admin_home"))
        elif request.user.user_type == '2':
            return redirect(reverse("staff_home"))
        else:
            return redirect(reverse("student_home"))
    return render(request, 'main_app/login.html')


def register(request):
    from django.core.files.storage import FileSystemStorage

    if request.method == 'POST':

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        email = request.POST.get('email')
        password = request.POST.get('password')

        gender = request.POST.get('gender')
        address = request.POST.get('address')

        user_type = request.POST.get('user_type')

        course_id = request.POST.get('course') or None
        session_id = request.POST.get('session') or None

        roll_no = request.POST.get('roll_no')

        # CHECK ONLY FOR STUDENTS
        if user_type == '3':

            student_master = StudentMaster.objects.filter(
                roll_no=roll_no,
                email=email,
                is_registered=False
            ).first()

            if not student_master:
                messages.error(
                    request,
                    "You are not authorized to register"
                )
                return redirect(reverse('register'))

        # HANDLE PROFILE PIC
        profile_pic = request.FILES.get('profile_pic')

        try:

            if profile_pic:
                fs = FileSystemStorage()

                filename = fs.save(
                    profile_pic.name,
                    profile_pic
                )

                profile_pic_url = fs.url(filename)

            else:
                profile_pic_url = None

            extra = {
                'first_name': first_name or '',
                'last_name': last_name or '',
                'gender': gender or 'M',
                'address': address or '',
                'user_type': user_type or '3'
            }

            if profile_pic_url:
                extra['profile_pic'] = profile_pic_url

            # CREATE USER
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                **extra
            )

            # STUDENT
            if user.user_type == '3':

                student = Student.objects.get(admin=user)

                student.course = student_master.course
                student.session = student_master.session
                student.roll_no = student_master.roll_no

                student.save()

                # MARK AS REGISTERED
                student_master.is_registered = True
                student_master.save()

            # STAFF
            elif user.user_type == '2':

                if course_id:

                    staff = Staff.objects.get(admin=user)

                    staff.course = Course.objects.get(
                        id=course_id
                    )

                    staff.save()

            # AUTO LOGIN
            login(request, user)

            if user.user_type == '2':
                return redirect(reverse('staff_home'))

            else:
                return redirect(reverse('student_home'))

        except Exception as e:

            messages.error(
                request,
                f"Registration failed: {e}"
            )

            return redirect(reverse('home'))

    courses = Course.objects.all()

    sessions = Session.objects.all()

    return render(
        request,
        'main_app/register.html',
        {
            'courses': courses,
            'sessions': sessions
        }
    )

def doLogin(request, **kwargs):
    if request.method != 'POST':
        return HttpResponse("<h4>Denied</h4>")
    else:
        #Google recaptcha
        captcha_token = request.POST.get('g-recaptcha-response')
        captcha_url = "https://www.google.com/recaptcha/api/siteverify"
        captcha_key = "6LfswtgZAAAAABX9gbLqe-d97qE2g1JP8oUYritJ"
        data = {
            'secret': captcha_key,
            'response': captcha_token
        }
        # Make request
        try:
            captcha_server = requests.post(url=captcha_url, data=data)
            response = json.loads(captcha_server.text)
            if response['success'] == False:
                messages.error(request, 'Invalid Captcha. Try Again')
                return redirect('/')
        except:
            messages.error(request, 'Captcha could not be verified. Try Again')
            return redirect('/')
        
        #Authenticate
        user = EmailBackend.authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
        if user != None:
            login(request, user)
            if user.user_type == '1':
                return redirect(reverse("admin_home"))
            elif user.user_type == '2':
                return redirect(reverse("staff_home"))
            else:
                return redirect(reverse("student_home"))
        else:
            messages.error(request, "Invalid details")
            return redirect("/")



def logout_user(request):
    if request.user != None:
        logout(request)
    return redirect("/")


@csrf_exempt
def get_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = Attendance.objects.filter(subject=subject, session=session)
        attendance_list = []
        for attd in attendance:
            data = {
                    "id": attd.id,
                    "attendance_date": str(attd.date),
                    "session": attd.session.id
                    }
            attendance_list.append(data)
        return JsonResponse(json.dumps(attendance_list), safe=False)
    except Exception as e:
        return None


def showFirebaseJS(request):
    data = """
    // Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here, other Firebase libraries
// are not available in the service worker.
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-messaging.js');

// Initialize the Firebase app in the service worker by passing in
// your app's Firebase config object.
// https://firebase.google.com/docs/web/setup#config-object
firebase.initializeApp({
    apiKey: "AIzaSyBarDWWHTfTMSrtc5Lj3Cdw5dEvjAkFwtM",
    authDomain: "sms-with-django.firebaseapp.com",
    databaseURL: "https://sms-with-django.firebaseio.com",
    projectId: "sms-with-django",
    storageBucket: "sms-with-django.appspot.com",
    messagingSenderId: "945324593139",
    appId: "1:945324593139:web:03fa99a8854bbd38420c86",
    measurementId: "G-2F2RXTL9GT"
});

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function (payload) {
    const notification = JSON.parse(payload);
    const notificationOption = {
        body: notification.body,
        icon: notification.icon
    }
    return self.registration.showNotification(payload.notification.title, notificationOption);
});
    """
    return HttpResponse(data, content_type='application/javascript')
