from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required(login_url='/')
def alumni_home(request):
    context = {
        "page_title": "Alumni Dashboard"
    }
    return render(request, "alumni_template/alumni_home.html", context)


@login_required(login_url='/')
def alumni_profile(request):
    context = {
        "page_title": "Alumni Profile"
    }
    return render(request, "alumni_template/alumni_profile.html", context)


@login_required(login_url='/')
def alumni_jobs(request):
    context = {
        "page_title": "Job Opportunities"
    }
    return render(request, "alumni_template/alumni_jobs.html", context)


@login_required(login_url='/')
def alumni_events(request):
    context = {
        "page_title": "Alumni Events"
    }
    return render(request, "alumni_template/alumni_events.html", context)


@login_required(login_url='/')
def alumni_network(request):
    context = {
        "page_title": "Alumni Network"
    }
    return render(request, "alumni_template/alumni_network.html", context)


@login_required(login_url='/')
def alumni_donations(request):
    context = {
        "page_title": "Alumni Contributions"
    }
    return render(request, "alumni_template/alumni_donations.html", context)


@login_required(login_url='/')
def alumni_feedback(request):
    context = {
        "page_title": "Feedback"
    }
    return render(request, "alumni_template/alumni_feedback.html", context)