from django.contrib import admin
from .models import Channel, ChannelMember, Message

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    search_fields = ["name"]                     # <- necesario para autocomplete en inlines
    list_display = ("name", "created_by", "created_at")
    ordering = ("name",)
    autocomplete_fields = ("created_by",)        # opcional

@admin.register(ChannelMember)
class ChannelMemberAdmin(admin.ModelAdmin):
    search_fields = ("channel__name", "user__username")
    list_display = ("channel", "user", "is_admin")
    autocomplete_fields = ("channel", "user")    # opcional

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ("id", "channel", "sender", "receiver", "created_at")
    search_fields = ("channel__name", "sender__username", "receiver__username", "body")
    list_filter   = ("channel",)
