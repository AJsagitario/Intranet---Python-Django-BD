from django.contrib import admin
from .models import User, Area
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (("Info", {"fields": ("area","is_admin")}),)

admin.site.register(Area)

