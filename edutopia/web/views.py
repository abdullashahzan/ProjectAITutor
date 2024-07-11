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

def landing(request):
    return render(request, "web/landing.html")

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
        print("Extracting text from file")
        notes = ai.extract_text_from_file(note.file.path)[:4000]
        note.note = notes
        print("Extracting details from notes")
        content = ai.AI_notes_detail_extractor_prompt + " These are the notes of the student: " + notes
        answer = ai.respond(content)
        print(answer)
        print("Generating brief summary of the chapter")
        content = "Generate a brief summary of what this chapter talks about and the skills student will gain from it. The output must be in beautiful html format so it is easier for student to understand. Keep it short and simple. Do not add h1 tags use anything else. These are the notes of the student: " + notes
        note.note_brief = ai.respond(content) 
        while True:
            try:
                answer = answer.strip('][').split(",")
                new_answer = []
                for element in answer:
                    new_element = element.strip().replace("\"", "")
                    if str(new_element).lower() == "no":
                        new_answer.append(False)
                    else:
                        try:
                            score = int(new_element)
                        except:
                            new_answer.append(True)
                note.research_required = new_answer[0]
                note.practical_required = new_answer[1]
                note.group_practical_required = new_answer[2]
                note.quality_score = score
                break
            except:
                print("Failed to correctly extract data from notes, trying again.")
                pass
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
    quality_score= Note.objects.get(id=note_id).quality_score
    if quality_score >= 70:
        quality_score_good = True
    else:
        quality_score_good = False
    return render(request, 'web/note.html', {
        "note":Note.objects.get(id=note_id),
        "quality_score_good": quality_score_good
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
        subjects = Subject.objects.filter(username=request.user.username)[:6]
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
        quiz.total_score = len(questions)
        quiz.save()
        content = ai.AI_quiz_evaluator_prompt + " These are the notes of the student: " + note.note + " This is the quiz data of the student: " + json.dumps(data)
        response = ai.respond(content)
        marks = f"{quiz.score} / {quiz.total_score}"
        return render(request, 'web/evaluation.html', {'marks': marks, 'evaluation': response})

def ai_researcher(request, note_id):
    note = Note.objects.get(id=note_id)
    try:
        research = Research.objects.get(username=request.user.username, note_id=note_id)
        research_topic = research.research
    except:
        content = ai.AI_researcher_prompt + " these are the notes of the students: " + note.note
        research_topic = ai.respond(content)
        Research(username=request.user.username, research=research_topic, note_id=note_id).save()
    return render(request, 'web/ai_researcher.html', {'research':research_topic, 'note':note})

def ai_research_evaluator(request):
    if request.method == "POST" and request.FILES.get('file'):
        note_id = request.POST['note_id']
        research = Research.objects.get(username=request.user.username, note_id=note_id)
        research_topic = research.research
        file = request.FILES['file']
        research = Research.objects.get(username=request.user.username, note_id=note_id)
        research.file = file
        research.save()
        text = ai.extract_text_from_file(research.file.path)[:2000]
        content = ai.AI_research_evaluator_prompt + " This is the research topic that the student was asked to research: " + research_topic + " This is the research report submitted by the student: " + text
        response = ai.respond(content)
        return render(request, 'web/evaluation.html', {'evaluation':response})

def ai_project_manager(request, note_id):
    note = Note.objects.get(id=note_id)
    try:
        data = Project.objects.get(username=request.user.username, note_id=note_id)
    except:
        content = ai.AI_project_prompt + " these are the notes of the students: " + note.note
        project = ai.respond(content)
        data = Project(username=request.user.username, project=project, note_id=note_id)
        data.save()
    collaborators = data.collaborators.split(",")[:-1]
    return render(request, 'web/ai_practical.html', {'project':data, "collaborators":collaborators, 'note':note})

def ai_project_evaluator(request):
    if request.method == "POST" and request.FILES.get('file'):
        note_id = request.POST['note_id']
        project = Project.objects.get(username=request.user.username, note_id=note_id)
        project_topic = project.project
        file = request.FILES['file']
        project.file = file
        project.save()
        text = ai.extract_text_from_file(project.file.path)[:2000]
        content = ai.AI_research_evaluator_prompt + " This is the research topic that the student was asked to research: " + project_topic + " This is the research report submitted by the student: " + text
        response = ai.respond(content)
        return render(request, 'web/evaluation.html', {'evaluation':response})

def upload_project(request):
    if request.method == "POST":
        file = request.FILES['file']
        project_id = request.POST['project_id']
        data = Project.objects.get(id=project_id)
        data.file = file
        data.save()
        text = ai.extract_text_from_file(data.file.path)
        content = ai.AI_project_evaluator_prompt + " This is the project that the student was asked to do: " + data.project + " This is the project report submitted by the student: " + text + "And the people who did this project are " + data.collaborators
        response = ai.respond(content)
        data.evaluation = response
        data.save()
    return render(request, "web/project_evaluation.html", {"project":data, "response":response})

def add_collaborator(request):
    if request.method == "POST":
        project_id = request.POST['project_id']
        username = request.POST['username']
        project = Project.objects.get(id=project_id)
        project.collaborators += f"{username},"
        project.save()
    referrer = request.META.get('HTTP_REFERER')
    return redirect(referrer or reverse('web:index'))

def important_questions(request, note_id):
    note = Note.objects.get(id=note_id)
    return render(request, "web/important_questions.html", {"note": note})
