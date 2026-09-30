from django.urls import path
from main.views import (
    create_education,
    create_education_ajax,
    create_experience,
    create_experience_ajax,
    create_mading,
    decrease_mading,
    delete_education,
    delete_experience,
    delete_mading,
    edit_education,
    edit_experience,
    edit_mading,
    get_education_json,
    get_experience_json,
    increase_mading,
    login_user,
    logout_user,
    register,
    show_education,
    show_experience,
    show_main,
    toggle_star,
    toggle_star_education,
)

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('experience/', show_experience, name='show_experience'),
    path('experience/create/', create_experience, name='create_experience'),
    path('experience/create-ajax/', create_experience_ajax, name='create_experience_ajax'),
    path('experience/<uuid:experience_id>/edit/', edit_experience, name='edit_experience'),
    path('experience/<uuid:experience_id>/delete/', delete_experience, name='delete_experience'),
    path('experience/<uuid:experience_id>/star/', toggle_star, name='toggle_star'),
    path('education/', show_education, name='show_education'),
    path('education/create/', create_education, name='create_education'),
    path('education/create-ajax/', create_education_ajax, name='create_education_ajax'),
    path('education/<uuid:education_id>/edit/', edit_education, name='edit_education'),
    path('education/<uuid:education_id>/delete/', delete_education, name='delete_education'),
    path('education/<uuid:education_id>/star/', toggle_star_education, name='toggle_star_education'),
    path('api/experiences/', get_experience_json, name='get_experience_json'),
    path('api/educations/', get_education_json, name='get_education_json'),
    path('mading/create/', create_mading, name='create_mading'),
    path('mading/<uuid:mading_id>/increase/', increase_mading, name='increase_mading'),
    path('mading/<uuid:mading_id>/decrease/', decrease_mading, name='decrease_mading'),
    path('mading/<uuid:mading_id>/edit/', edit_mading, name='edit_mading'),
    path('mading/<uuid:mading_id>/delete/', delete_mading, name='delete_mading'),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
]



