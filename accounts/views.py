from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.db.models import Q
from accounts.models import Area
from chat.models import Channel, ChannelMember

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import UserChangeForm  # lo creamos abajo

User = get_user_model()
# Solo staff o superuser pueden entrar al panel
is_admin = user_passes_test(lambda u: u.is_staff or u.is_superuser)
@is_admin
def admin_home(request):
    # Métricas rápidas
    users_total   = User.objects.count()
    users_activos = User.objects.filter(is_active=True).count()
    canales_total = Channel.objects.count()
    areas_total   = Area.objects.count()

    # Listas cortas para el dashboard
    recientes = User.objects.order_by('-date_joined')[:8]
    canales   = Channel.objects.order_by('name')[:12]

    # Búsqueda simple de usuarios (filtro instantáneo también lo haremos en la plantilla con JS)
    q = (request.GET.get('q') or '').strip()
    if q:
        users = (User.objects
                 .filter(Q(username__icontains=q) |
                         Q(first_name__icontains=q) |
                         Q(last_name__icontains=q) |
                         Q(email__icontains=q))
                 .order_by('username')[:50])
    else:
        users = User.objects.order_by('username')[:50]

    ctx = {
        "users_total": users_total,
        "users_activos": users_activos,
        "canales_total": canales_total,
        "areas_total": areas_total,
        "users_recientes": recientes,
        "canales": canales,
        "users": users,
    }
    return render(request, "admin/home.html", ctx)

@login_required
def profile(request):
    return render(request, "accounts/profile.html", {"user_obj": request.user})

@login_required
def profile_edit(request):
    if request.method == "POST":
        form = UserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado.")
            return redirect("profile")
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, "accounts/profile_edit.html", {"form": form})
@login_required
def avatar_upload(request):
    # Placeholder opcional por si ya lo enlazaste en la UI
    return render(request, "accounts/avatar_upload.html")

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
