from django.contrib import admin
from .models import Room, Bookshelf, Book

admin.site.register(Room)
admin.site.register(Bookshelf)
admin.site.register(Book)