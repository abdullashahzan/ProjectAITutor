from django.urls import path
from . import views

app_name = 'web'
urlpatterns = [
    path("login", views.login_user, name="login_user"),
    path("signup", views.signup_user, name="signup_user"),
    path("logout", views.logout_user, name="logout_user"),
    

    path("", views.index, name="index"),
    path("Home/", views.landing, name='landing'),

    path("ai_tutor/<str:note_id>", views.ai_tutor, name="ai_tutor"),
    path("ai_evaluator/<str:note_id>/<str:exam_type>", views.ai_evaluator, name="ai_evaluator"),
    path("evaluate_student/", views.evaluate_student, name="evaluate_student"),
    path("important_questions/<str:note_id>", views.important_questions, name='important_questions'),

    path("ai_research/<str:note_id>", views.ai_researcher, name='ai_research'),
    path("ai_research_evaluator", views.ai_research_evaluator, name='ai_research_evaluator'),

    path("ai_project_manager/<str:note_id>", views.ai_project_manager, name='ai_project_manager'),
    path("ai_project_evaluator", views.ai_project_evaluator, name='ai_project_evaluator'),

    path("upload_project/", views.upload_project, name='upload_project'),
    path("add_collaborator/", views.add_collaborator, name='add_collaborator'),

    path('upload_note/', views.upload_note, name='upload_note'),
    path('remove_note/<str:note_id>/', views.remove_note, name='remove_note'),
    path('open_note/<str:note_id>', views.open_note, name='open_note'),

    path('add_subject/', views.add_subject, name='add_subject'),
    path('remove_subject/<str:id>', views.remove_subject, name='remove_subject'),
    path('open_subject/<str:subject_id>', views.open_subject, name='open_subject'),

]