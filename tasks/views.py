from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import get_user_model

from .models import Task
User = get_user_model()

@login_required
def index(request):
    q = (request.GET.get("q") or "").strip()
    mine    = Task.objects.filter(assigned_to=request.user)
    created = Task.objects.filter(created_by=request.user)
    if q:
        mine = mine.filter(Q(title__icontains=q) | Q(description__icontains=q))
        created = created.filter(Q(title__icontains=q) | Q(description__icontains=q))
    users = User.objects.filter(is_active=True).order_by("username")
    return render(request, "tasks/index.html", {
        "q": q, "users": users,
        "tasks_for_me": mine.select_related("assigned_to", "created_by"),
        "tasks_by_me": created.select_related("assigned_to", "created_by"),
    })

@login_required
def create(request):
    if request.method != "POST":
        return redirect("tasks:index")
    title = (request.POST.get("title") or "").strip()
    desc  = (request.POST.get("description") or "").strip()
    assg  = request.POST.get("assigned_to") or None
    due   = request.POST.get("due_date") or None
    if not title:
        messages.error(request, "El título es obligatorio.")
        return redirect("tasks:index")
    assigned_to = User.objects.filter(id=assg, is_active=True).first() if assg and assg.isdigit() else None
    Task.objects.create(
        title=title, description=desc, created_by=request.user,
        assigned_to=assigned_to, due_date=due or None
    )
    messages.success(request, "Tarea creada.")
    return redirect("tasks:index")

@login_required
def toggle_done(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if not (task.created_by_id == request.user.id or task.assigned_to_id == request.user.id or request.user.is_staff):
        return redirect("tasks:index")
    task.status = "done" if task.status != "done" else "open"
    task.save(update_fields=["status", "updated_at"])
    return redirect("tasks:index")

@login_required
def delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if not (task.created_by_id == request.user.id or request.user.is_staff):
        messages.error(request, "No tienes permiso para borrar esta tarea.")
        return redirect("tasks:index")
    task.delete()
    messages.success(request, "Tarea eliminada.")
    return redirect("tasks:index")

