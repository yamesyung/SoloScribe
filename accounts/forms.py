from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import Form, FileField, ModelForm

from books.models import Review


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        label="Password (optional)"
    )
    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
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


class ImportForm(Form):
    goodreads_file = FileField(
        label="Select CSV file",
        widget=forms.ClearableFileInput(attrs={'accept': '.csv'})
    )


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = '__all__'
