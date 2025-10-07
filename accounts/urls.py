from django.urls import path
from . import views

urlpatterns = [
    path("", views.profile, name="profile"),                 # /cuenta/
    path("editar/", views.profile_edit, name="profile_edit") # /cuenta/editar/
]
