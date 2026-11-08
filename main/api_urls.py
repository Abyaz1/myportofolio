from django.urls import path
from main import api_views

app_name = "api"

urlpatterns = [
    # Experience endpoints
    path("experiences/", api_views.experience_list, name="experience-list"),
    path("experiences/<uuid:experience_id>/", api_views.experience_detail, name="experience-detail"),
    path("experiences/<uuid:experience_id>/star/", api_views.experience_star, name="experience-star"),

    # Education endpoints
    path("educations/", api_views.education_list, name="education-list"),
    path("educations/<uuid:education_id>/", api_views.education_detail, name="education-detail"),
    path("educations/<uuid:education_id>/star/", api_views.education_star, name="education-star"),

    # Singular aliases for education
    path("education/", api_views.education_list),
    path("education/<uuid:education_id>/", api_views.education_detail),
    path("education/<uuid:education_id>/star/", api_views.education_star),
]
