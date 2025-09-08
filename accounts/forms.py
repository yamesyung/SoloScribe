from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.forms import ModelForm


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password (optional)'}),
        label="Password"
    )
    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password (optional)'}),
        label="Confirm Password"
    )

    class Meta:
        model = get_user_model()
        fields = ("username",)


class CustomUserChangeForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "password"
        )
