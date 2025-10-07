from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.db.models import Q, Max
from django.contrib.auth import get_user_model
from .models import Channel, ChannelMember, Message
from django.contrib import messages as djmsg
from django.views.decorators.http import require_POST

User = get_user_model()

def _sidebar_context(user):
    # Canales visibles en el sidebar
    if user.is_staff or user.is_superuser:
        my_channels = Channel.objects.all().order_by("name")
    else:
        my_channels = (
            Channel.objects
            .filter(members__user=user)
            .order_by("name")
            .distinct()
        )

    # DMs: si quieres "recientes", usa partner_ids (ver abajo); si no, deja todos activos
    dm_pairs = (
        Message.objects
        .filter(Q(sender=user) | Q(receiver=user), channel__isnull=True)
        .values("sender", "receiver")
    )
    partner_ids = set()
    for row in dm_pairs:
        a, b = row["sender"], row["receiver"]
        if a and b:
            partner_ids.add(a if b == user.id else b)

    dm_users = (
        User.objects
        .filter(is_active=True)  # <- usa solo con quienes hubo DM
        .exclude(id=user.id)
        .order_by("username")
    )

    return {"sidebar_channels": my_channels, "sidebar_dm_users": dm_users}

@login_required
def home(request):
    # entra directo a #general si existe
    try:
        Channel.objects.get(name="general")
        return redirect("room", room_name="general")
    except Channel.DoesNotExist:
        ctx = _sidebar_context(request.user)
        return render(request, "chat/index_empty.html", ctx)

@login_required
def room(request, room_name):
    ch = get_object_or_404(Channel, name=room_name)
    ChannelMember.objects.get_or_create(channel=ch, user=request.user)
    messages = ch.messages.select_related("sender").order_by("created_at")[:500]

    # <-- calcula aquí si el usuario puede limpiar el canal
    is_channel_admin = ChannelMember.objects.filter(
        channel=ch, user=request.user, is_admin=True
    ).exists()
    can_clear = is_channel_admin or (ch.created_by_id == request.user.id)

    ctx = {
        "room": room_name,
        "messages": messages,
        "is_channel": True,
        "channel": ch,
        "can_clear": can_clear,          # <-- pásalo al template
    }
    ctx.update(_sidebar_context(request.user))
    return render(request, "chat/room.html", ctx)

@login_required
def dm(request, user_id):
    other = get_user_or_404 = get_object_or_404(User, id=user_id)
    # conversación entre ambos
    msgs = (Message.objects
            .filter(channel__isnull=True)
            .filter(
                (Q(sender=request.user) & Q(receiver=other)) |
                (Q(sender=other) & Q(receiver=request.user))
            )
            .select_related("sender")
            .order_by("created_at")[:500])

    # nombre de sala WebSocket "dm-<id>"
    room_name = f"dm-{other.id}"
    ctx = {"room": room_name, "messages": msgs, "is_channel": False, "dm_user": other, "current_dm_id": other.id,}
    ctx.update(_sidebar_context(request.user))
    return render(request, "chat/room.html", ctx)

@login_required
def leave_channel(request, room_name):
    if request.method != "POST":
        return HttpResponseForbidden()
    ch = get_object_or_404(Channel, name=room_name)
    ChannelMember.objects.filter(channel=ch, user=request.user).delete()
    # Si ya no es miembro, redirige al home
    return redirect("home")

@login_required
def clear_channel(request, room_name):
    # Solo admin del canal puede limpiar
    ch = get_object_or_404(Channel, name=room_name)
    is_admin = ChannelMember.objects.filter(channel=ch, user=request.user, is_admin=True).exists() \
               or ch.created_by_id == request.user.id
    if not is_admin:
        return HttpResponseForbidden()
    Message.objects.filter(channel=ch).delete()
    return redirect("room", room_name=room_name)

@login_required
def create_channel(request):
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip().lower().replace(" ", "-")
        if not name:
            return redirect("home")
        ch, created = Channel.objects.get_or_create(name=name, defaults={"created_by": request.user})
        ChannelMember.objects.get_or_create(channel=ch, user=request.user, defaults={"is_admin": True})
        return redirect("room", room_name=name)
    # GET simple: mini form en index (podrías hacer una página aparte)
    ctx = _sidebar_context(request.user)
    return render(request, "chat/create_channel.html", ctx)

@login_required
def channel_members(request, room_name):
    ch = get_object_or_404(Channel, name=room_name)
    # permisos: creador o admin del canal
    is_admin = ChannelMember.objects.filter(channel=ch, user=request.user, is_admin=True).exists() \
               or ch.created_by_id == request.user.id
    if not is_admin:
        return HttpResponseForbidden()

    current = User.objects.filter(channelmember__channel=ch).order_by("username")
    # sugerencias: todos menos los que ya están
    suggested = User.objects.exclude(channelmember__channel=ch).exclude(id=request.user.id).order_by("username")

    ctx = {"channel": ch, "current": current, "suggested": suggested}
    ctx.update(_sidebar_context(request.user))
    return render(request, "chat/members.html", ctx)

@require_POST
@login_required
def add_member(request, room_name):
    ch = get_object_or_404(Channel, name=room_name)
    # permisos
    is_admin = ChannelMember.objects.filter(channel=ch, user=request.user, is_admin=True).exists() \
               or ch.created_by_id == request.user.id
    if not is_admin:
        return HttpResponseForbidden()

    user_id = request.POST.get("user_id")
    if user_id and User.objects.filter(id=user_id, is_active=True).exists():
        u = User.objects.get(id=user_id)
        ChannelMember.objects.get_or_create(channel=ch, user=u)
        djmsg.success(request, f"Se agregó a {u.username} a #{ch.name}.")
    return redirect("channel_members", room_name=room_name)

@login_required
def remove_member(request, room_name, user_id):
    ch = get_object_or_404(Channel, name=room_name)
    # permisos
    is_admin = ChannelMember.objects.filter(channel=ch, user=request.user, is_admin=True).exists() \
               or ch.created_by_id == request.user.id
    if not is_admin:
        return HttpResponseForbidden()
    # no permitir quitar al creador
    if user_id == ch.created_by_id:
        djmsg.error(request, "No puedes quitar al creador del canal.")
        return redirect("channel_members", room_name=room_name)

    ChannelMember.objects.filter(channel=ch, user_id=user_id).delete()
    djmsg.success(request, "Miembro removido.")
    return redirect("channel_members", room_name=room_name)
