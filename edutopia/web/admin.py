from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Note)
admin.site.register(Quiz)
admin.site.register(Subject)
admin.site.register(Research)
admin.site.register(Project)