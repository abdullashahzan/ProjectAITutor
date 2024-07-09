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
import json, random

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
        user = request.user.username
        file = request.FILES['file']
        subject_id = request.POST['subject_id']
        name = request.POST['name']
        note = Note(username=user, file=file, subject_id=subject_id, name=name)
        note.save()
        notes = ai.extract_text_from_file(note.file.path)[:4000]
        note.note = notes
        content = ai.AI_notes_detail_extractor_prompt + " These are the notes of the student: " + notes
        answer = ai.respond(content)
        print(answer)
        answer = answer.strip('][').split(",")
        new_answer = []
        for element in answer:
            element = element.strip().replace("\"", "")
            if str(element) == "no":
                new_answer.append(False)
            else:
                new_answer.append(True)
        note.research_required = new_answer[0]
        note.practical_required = new_answer[1]
        note.group_practical_required = new_answer[2]
        content = ai.AI_important_questions_prompt + " These are the notes of the student: " + notes
        note.important_questions = ai.respond(content)
        note.save()
        subject = Subject.objects.get(id=subject_id)
        subject.num_notes += 1
        subject.save()
    referrer = request.META.get('HTTP_REFERER')
    return redirect(referrer or reverse('web:index'))

def remove_note(request, note_id):
    note = Note.objects.get(id=note_id)
    subject = Subject.objects.get(id=note.subject_id)
    subject.num_notes -= 1
    subject.save()
    os.remove(note.file.path)
    note.delete()
    referrer = request.META.get('HTTP_REFERER')
    return redirect(referrer or reverse('web:index'))

def open_note(request, note_id):
    return render(request, 'web/note.html', {
        "note":Note.objects.get(id=note_id)
    })

def add_subject(request):
    if request.method == "POST":
        subject = request.POST['subject_name']
        Subject(username=request.user.username, subject_name=subject).save()
    referrer = request.META.get('HTTP_REFERER')
    return redirect(referrer or reverse('web:index'))

def remove_subject(request, id):
    Subject.objects.get(id=id).delete()
    referrer = request.META.get('HTTP_REFERER')
    return redirect(referrer or reverse('web:index'))

def open_subject(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    notes = Note.objects.filter(subject_id=subject_id)
    return render(request, 'web/subject.html', {"subject":subject, "notes":notes})

def index(request):
    try:
        userprofile = UserProfile.objects.get(user=request.user)
        subjects = Subject.objects.filter(username=request.user.username)[:5]
        return render(request, 'web/index.html', {
            "userprofile":userprofile,
            "subjects":subjects,
        })
    except:
        return render(request, 'web/index.html')

def ai_tutor(request, note_id):
    if int(note_id) != 0:
        note = Note.objects.get(id=note_id)
        if request.method == 'POST':
            data = json.loads(request.body)
            question = data.get('question')
            content = ai.AI_tutor_prompt + " These are the notes of the student: " + note.note + " This is student's question: " + question
            response = f'{ai.respond(content)}'
            return JsonResponse({'message': response})
        return render(request, 'web/ai_tutor.html', {'note':note, 'is_note': 'yes'})
    else:
        if request.method == 'POST':
            data = json.loads(request.body)
            question = data.get('question')
            content = ai.AI_tutor_prompt + " This is student's question: " + question
            response = f'{ai.respond(content)}'
            return JsonResponse({'message': response})
        return render(request, 'web/ai_tutor.html', {'is_note':'no'})        

def ai_evaluator(request, note_id, exam_type):
    note = Note.objects.get(id=note_id)
    if str(exam_type) == 'mcq':
        quiz_type = "MCQ"
        content = ai.AI_evaluator_prompt + " These are the notes of the student: " + note.note
    elif str(exam_type) == 'written':
        quiz_type = "Written"
        content = ai.AI_written_evaluator_prompt + " These are the notes of the student: " + note.note
    while True:
        try:
            response = ai.respond(content)
            print("test generated!")
            test = json.loads(response)
            questions, answers = '', ''
            for question in test['test']:
                questions += question + "!--!"
            for answer in test['answers']:
                answers += answer + "!--!"
            break
        except:
            print("Invalid test, generating another test.")
            pass
    quiz_data = Quiz(username=request.user.username, questions=questions, answers=answers, quiz_type=quiz_type)
    quiz_data.save()
    return render(request, 'web/quiz.html', {'test': test, 'quiz': quiz_data, 'note':note})

def evaluate_student(request):
    if request.method == 'POST':
        quiz = Quiz.objects.get(id=request.POST['quiz_id'])
        note = Note.objects.get(id=request.POST['note_id'])
        questions = quiz.questions.split("!--!")[:-1]
        answers = quiz.answers.split("!--!")[-1]
        user_answers = ""
        print(questions)
        for question in questions:
            user_answer = request.POST.get(question)
            print(user_answer)
            user_answers += str(user_answer) + "!--!"
            quiz.user_answers = user_answers
            quiz.save()
        user_answers = quiz.user_answers.split("!--!")[:-1]
        data = ""
        json_data = {}
        for question, answer, user_answer in zip(questions, answers, user_answers):
            data += f"Answer that student should have answered: {answer} but instead answered: {user_answer}, "
            json_data[question] = {"correct_answer": answer, "student_answer": user_answer}
            if quiz.total_score == 0:
                if quiz.quiz_type == "MCQ":
                    if answer == user_answer:
                        quiz.score += 1
                elif quiz.quiz_type == "Written":
                    print("comparing question")
                    content = ai.AI_compare_answers_prompt + "This is student's answer: " + str(user_answer) + " This is the correct answer: " + answer
                    output = ai.respond(content)
                    print('Finished comparing, comparing another one if exists.')
                    if output == 'c':
                        quiz.score += 1
        quiz.total_score = len(questions)
        quiz.save()
        content = ai.AI_suggester_prompt + " These are the notes of the student: " + note.note + " This is the quiz data of the student: " + json.dumps(data)
        response = ai.respond(content)
        return render(request, 'web/results.html', {'quiz': quiz, 'suggestion': response, 'quiz_data': json_data})

def ai_researcher(request, note_id):
    note = Note.objects.get(id=note_id)
    try:
        research = Research.objects.get(username=request.user.username, note_id=note_id)
        research_topic = research.research
    except:
        content = ai.AI_researcher_prompt + " these are the notes of the students: " + note.note
        research_topic = ai.respond(content)
        Research(username=request.user.username, research=research_topic, note_id=note_id).save()
    if request.method == "POST":
        return render(request, 'web/ai_researcher.html', {'research':research_topic})
    return render(request, 'web/ai_researcher.html', {'research':research_topic})

def ai_project_manager(request, note_id):
    note = Note.objects.get(id=note_id)
    try:
        data = Project.objects.get(username=request.user.username, note_id=note_id)
    except:
        content = ai.AI_project_prompt + " these are the notes of the students: " + note.note
        project = ai.respond(content)
        data = Project(username=request.user.username, project=project, note_id=note_id)
        data.save()
    if request.method == "POST":
        return render(request, 'web/ai_researcher.html', {'project':data})
    return render(request, 'web/ai_practical.html', {'project':data})

def important_questions(request, note_id):
    note = Note.objects.get(id=note_id)
    return render(request, "web/important_questions.html", {"note": note})
