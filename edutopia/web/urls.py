from django.urls import path
from . import views

app_name = 'web'
urlpatterns = [
    path("login", views.login_user, name="login_user"),
    path("signup", views.signup_user, name="signup_user"),
    path("logout", views.logout_user, name="logout_user"),

    path("", views.index, name="index"),
    path("ai_tutor/", views.ai_tutor, name="ai_tutor"),
    path("ai_evaluator/", views.ai_evaluator, name="ai_evaluator"),


    path('upload_note/', views.upload_note, name='upload_note'),
    path('remove_note/<str:note_id>/', views.remove_note, name='remove_note'),

]