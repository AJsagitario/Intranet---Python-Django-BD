from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Area
from chat.models import ChannelMember #nuevo channel



class ChannelMemberInline(admin.TabularInline):
    model = ChannelMember
    fk_name = "user"                     # el inline cuelga del usuario
    extra = 0
    fields = ["channel", "is_admin"]
    autocomplete_fields = ["channel"]    # usa ChannelAdmin de chat (con search_fields)
    verbose_name = "Membresía de canal"
    verbose_name_plural = "Canales donde participa"

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    list_display = ["name", "slug"]
    ordering = ["name"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # columnas de la lista
    def avatar_tag(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="height:32px;width:32px;object-fit:cover;border-radius:50%;">', obj.avatar.url)
        return "—"
    avatar_tag.short_description = "Foto"

    list_display  = ("avatar_tag", "username", "first_name", "last_name", "email", "area", "is_staff", "is_active")
    list_filter   = ("is_staff", "is_superuser", "is_active", "area")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering      = ("username",)
    autocomplete_fields = ("area",)

    fieldsets = (
        ("Cuenta", {"fields": ("username", "password")}),
        ("Datos personales", {"fields": ("first_name", "last_name", "email", "area", "avatar")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",),
                "fields": ("username", "password1", "password2", "first_name", "last_name", "email", "area", "avatar", "is_staff", "is_active")}),
    )

    inlines = [ChannelMemberInline]

    # acciones rápidas
    actions = ["hacer_admin", "quitar_admin", "resetear_password_temporal"]

    @admin.action(description="Conceder rol admin (is_staff)")
    def hacer_admin(self, request, queryset):
        updated = queryset.update(is_staff=True)
        self.message_user(request, f"{updated} usuarios ahora son admin.")

    @admin.action(description="Quitar rol admin (is_staff)")
    def quitar_admin(self, request, queryset):
        updated = queryset.update(is_staff=False)
        self.message_user(request, f"{updated} usuarios ya no son admin.")

    @admin.action(description="Poner password temporal 'GoVision2025!'")
    def resetear_password_temporal(self, request, queryset):
        for u in queryset:
            u.set_password("GoVision2025!")
            u.save()
        self.message_user(request, "Se asignó password temporal a los seleccionados.")

