from django.contrib.auth.models import AbstractUser
from django.db import models


def get_default_theme():
    """
    used to set the default theme when a new profile is created
    """
    theme, _ = Theme.objects.get_or_create(name="default")
    return theme


class CustomUser(AbstractUser):

    def get_theme_name(self):
        """
        used to have access to profile's selected theme in templates
        """
        if hasattr(self, "preferences") and self.preferences and self.preferences.preferred_theme:
            return self.preferences.preferred_theme.name
        return "default"

    pass


class Theme(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class UserPreferences(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='preferences')
    preferred_theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True, blank=True,
                                        default=get_default_theme)

    def __str__(self):
        return f"Preferences for {self.user.username}"
