from django import forms
from .models import User

class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username",
                  "area", "is_staff", "avatar"]
