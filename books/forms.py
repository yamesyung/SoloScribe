from django.forms import Form, FileField, ModelForm

from .models import Review, Book, Author


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = '__all__'


class BookIdForm(ModelForm):
    class Meta:
        model = Book
        fields = ['goodreads_id']


class ImportForm(Form):
    goodreads_file = FileField()


class ImportAuthorsForm(Form):
    authors_file = FileField()


class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = '__all__'
