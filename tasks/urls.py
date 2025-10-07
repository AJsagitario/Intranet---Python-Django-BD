from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.index, name="index"),
    path("crear/", views.create, name="create"),
    path("<int:task_id>/toggle/", views.toggle_done, name="toggle"),
    path("<int:task_id>/eliminar/", views.delete, name="delete"),
]
