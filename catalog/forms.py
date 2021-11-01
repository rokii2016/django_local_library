import datetime

from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import Genre,Book,BookInstance,Author

class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Check if a date is not in the past.
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Check if a date is in the allowed range (+4 weeks from today).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data
class GenreForm(forms.Form):
    
    genres = Genre.objects.all()
    CHOICES =[]
    for a_genre in genres:
        CHOICES.append((a_genre,a_genre))
    choice = forms.ChoiceField(choices=CHOICES)
class BookSearchForm(forms.Form):
    
    CHOICES =[('Genre','Genre'),('Title','Title'),('Author','Author')]
    choice = forms.ChoiceField(choices=CHOICES)
    title_search = forms.CharField(required=False,initial=" ")
    
    genres = Genre.objects.all()
    CHOICES1 =[]
    for a_genre in genres:
        CHOICES1.append((a_genre.name,a_genre.name))
    genre = forms.ChoiceField(choices=CHOICES1)
    authors = Author.objects.all()
    CHOICES2 =[]
    for a_author in authors:
        CHOICES2.append((a_author,a_author))
    author = forms.ChoiceField(choices=CHOICES2)
class BookForm(forms.Form):
    
    books = Book.objects.all()
    CHOICES =[]
    for a_book in books:
        CHOICES.append((a_book.title,a_book.title))
    choice = forms.ChoiceField(choices=CHOICES)
class BookInstanceForm(forms.Form):
    bookinstances = BookInstance.objects.all()
    CHOICES =[]
    for a_bookinstance in bookinstances:
        CHOICES.append((a_bookinstance.book.title,a_bookinstance.book.title))
    choice = forms.ChoiceField(choices=CHOICES)
    
