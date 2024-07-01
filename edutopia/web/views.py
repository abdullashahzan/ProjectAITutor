from django.shortcuts import render, redirect
from . import AI_model as ai
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import os
from .models import *
import json

def login_user(request):
    message = ""
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'web:index')
            return redirect(next_url)
        else:
            get_user = User.objects.get(email=username)
            user = authenticate(username=get_user.username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'web:index')
                return redirect(next_url)
        message = "Invalid credentials"
    return render(request, "web/login.html", {"message": message})

def signup_user(request):
    message = ""
    if request.method == "POST":
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        if email is not None and username is not None and password is not None:
            try:
                user = User.objects.create_user(username=username, password=password)
                user.email = email
                user.save()
                UserProfile(user=user).save()
                login(request, user)
                return redirect(reverse('web:index'))
            except IntegrityError:
                message = "Username or email is already taken"
            except:
                message = "Please make sure all the data is filled correctly"
        else:
            message = "Please fill all the fields"
    return render(request, "web/signup.html", {"message": message})

def logout_user(request):
    logout(request)
    return redirect('web:login_user')

def upload_note(request):
    if request.method == 'POST' and request.FILES.get('file'):
        user = request.user
        file = request.FILES['file']
        note = Note(user=user, file=file)
        note.save()
    referrer = request.META.get('HTTP_REFERER')
    return redirect(referrer or reverse('web:index'))

def remove_note(request, note_id):
    note = Note.objects.get(id=note_id)
    os.remove(note.file.path)
    note.delete()
    referrer = request.META.get('HTTP_REFERER')
    return redirect(referrer or reverse('web:index'))

def index(request):
    return render(request, 'web/index.html')

def ai_tutor(request):
    try:
        note = Note.objects.get(user=request.user)
    except:
        note = ""
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question')
        if note != "":
            student_notes = ai.extract_text_from_file(note.file.path)
            content = ai.AI_tutor_prompt + " These are the notes of the student: " + student_notes + " This is student's question: " + question
        else:
            content = ai.AI_tutor_prompt + " From here on all of this will be user input: " + question
        response = f'{ai.respond(content)}'
        return JsonResponse({'message': response})
    return render(request, 'web/ai_tutor.html', {'note':note})

def ai_evaluator(request):
    return render(request, "web/ai_evaluator.html")

