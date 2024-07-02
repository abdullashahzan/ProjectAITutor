from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s profile"
    
class Note(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='web/Storage/')

    def __str__(self):
        return self.user.username + "'s note"
    
class Quiz(models.Model):
    username = models.CharField(max_length=100, default="")
    questions = models.CharField(max_length=30000)
    answers = models.CharField(max_length=30000)
    user_answers = models.CharField(max_length=30000)
    score = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    quiz_type = models.CharField(max_length=100, default="")

    def __str__(self):
        return self.username + "'s quiz"