from django.forms import Form, FileField, ModelForm

from .models import Review, Book


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = '__all__'


class BookIdForm(ModelForm):
    class Meta:
        model = Book
        fields = ['goodreads_id']


class ImportForm(Form):
    review_file = FileField()
