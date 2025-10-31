from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Theme, UserPreferences

CustomUser = get_user_model()


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "username",
        "is_superuser",
    ]


admin.site.register(CustomUser, CustomUserAdmin)


class ThemeAdmin(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(Theme, ThemeAdmin)


class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ("user", "preferred_theme",)


admin.site.register(UserPreferences, UserPreferencesAdmin)
