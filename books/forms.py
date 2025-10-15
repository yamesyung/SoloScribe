from django.forms import Form, FileField, ModelForm

from .models import Review, Book, Author

"""
forms tied to Import data page
"""


class BookIdForm(ModelForm):
    class Meta:
        model = Book
        fields = ['goodreads_id']


class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = '__all__'


class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = '__all__'

