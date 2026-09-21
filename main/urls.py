from django.urls import path
from main.views import (
    create_education,
    create_experience,
    create_mading,
    decrease_mading,
    delete_education,
    delete_experience,
    delete_mading,
    edit_education,
    edit_experience,
    get_experience_json,
    increase_mading,
    show_education,
    show_experience,
    show_main,
)

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('experience/', show_experience, name='show_experience'),
    path('experience/create/', create_experience, name='create_experience'),
    path('experience/<uuid:experience_id>/edit/', edit_experience, name='edit_experience'),
    path('experience/<uuid:experience_id>/delete/', delete_experience, name='delete_experience'),
    path('education/', show_education, name='show_education'),
    path('education/create/', create_education, name='create_education'),
    path('education/<uuid:education_id>/edit/', edit_education, name='edit_education'),
    path('education/<uuid:education_id>/delete/', delete_education, name='delete_education'),
    path('api/experiences/', get_experience_json, name='get_experience_json'),
    path('mading/create/', create_mading, name='create_mading'),
    path('mading/<uuid:mading_id>/increase/', increase_mading, name='increase_mading'),
    path('mading/<uuid:mading_id>/decrease/', decrease_mading, name='decrease_mading'),
    path('mading/<uuid:mading_id>/delete/', delete_mading, name='delete_mading'),
]



