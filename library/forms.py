# In library/forms.py
from django import forms
from .models import Book, Room, Bookshelf

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        # Elenchiamo tutti i campi che vogliamo poter modificare
        fields = ['title', 'author', 'summary', 'cover_url', 
                  'published_date', 'bookshelf', 'shelf_number', 'user_rating']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendiamo il campo 'bookshelf' più leggibile, mostrando anche la stanza
        self.fields['bookshelf'].queryset = Bookshelf.objects.select_related('room').all()
        self.fields['bookshelf'].label_from_instance = lambda obj: f"{obj.name} (in {obj.room.name})"