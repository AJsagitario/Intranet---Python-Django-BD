"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.conf import settings                     # ← importa settings
from django.conf.urls.static import static 

from chat import views as chat_views
from accounts import views as accounts_views

urlpatterns = [
    path("djadmin/", admin.site.urls),

    path('admin/', accounts_views.admin_home, name='admin_home'),
    
    # auth
    path("login/",  auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    # ver punto 2 para logout (dejamos el nombre igual)
    path('logout/', accounts_views.logout_view, name='logout'),

    # redirección legacy
    path("accounts/login/", RedirectView.as_view(url="/login/", permanent=False)),

    path("cuenta/", include("accounts.urls")),

    path("tareas/", include("tasks.urls")),


    path("", chat_views.home, name="home"),
    path("c/<str:room_name>/", chat_views.room, name="room"),
    path("dm/<int:user_id>/", chat_views.dm, name="dm"),
    
    path("channel/<str:room_name>/members/", chat_views.channel_members, name="channel_members"),
    path("channel/<str:room_name>/members/add/", chat_views.add_member, name="add_member"),
    path("channel/<str:room_name>/members/remove/<int:user_id>/", chat_views.remove_member, name="remove_member"),
    path("channel/<str:room_name>/leave/", chat_views.leave_channel, name="leave_channel"),
    path("channel/create/", chat_views.create_channel, name="create_channel"),
    path("channel/<str:room_name>/clear/", chat_views.clear_channel, name="clear_channel"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)