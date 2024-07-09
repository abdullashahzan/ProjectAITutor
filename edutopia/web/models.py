from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s profile"
    
class Note(models.Model):
    username = models.CharField(max_length=256, default="")
    subject_id = models.CharField(max_length=10)
    file = models.FileField(upload_to='web/Storage/')
    name = models.CharField(max_length=256, default="unnamed note")
    note_progress = models.FloatField(default=0)
    note = models.CharField(max_length=4000, default="")
    research_required = models.BooleanField(default=False)
    practical_required = models.BooleanField(default=False)
    group_practical_required = models.BooleanField(default=False)
    important_questions = models.CharField(default="", max_length=10000)

    def __str__(self):
        return self.username + "'s note"

class Research(models.Model):
    username = models.CharField(max_length=256)
    research = models.CharField(max_length=4000)
    submitted_research = models.CharField(max_length=2000, default="")
    score = models.FloatField(default=0)
    note_id = models.CharField(default='0', max_length=256)

    def __str__(self):
        return f"{self.username}'s research"

class Project(models.Model):
    username = models.CharField(max_length=256)
    project = models.CharField(max_length=4000)
    submitted_project = models.CharField(max_length=2000, default="")
    score = models.FloatField(default=0)
    note_id = models.CharField(default='0', max_length=256)

    def __str__(self):
        return f"{self.username}'s research"
    
class Quiz(models.Model):
    username = models.CharField(max_length=256, default="")
    questions = models.CharField(max_length=30000)
    answers = models.CharField(max_length=30000)
    user_answers = models.CharField(max_length=30000)
    score = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    quiz_type = models.CharField(max_length=100, default="")

    def __str__(self):
        return self.username + "'s quiz"
    
class Subject(models.Model):
    username = models.CharField(max_length=256, default="")
    subject_name = models.CharField(max_length=100)
    num_notes = models.IntegerField(default=0)
    progress = models.FloatField(default=0)
    
    def __str__(self):
        return self.username + "'s subject"