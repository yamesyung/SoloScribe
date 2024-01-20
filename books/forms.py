from django.forms import Form, FileField, ModelForm

from .models import Review


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = '__all__'


class ImportForm(Form):
    review_file = FileField()
