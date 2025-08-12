from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Bookshelf(models.Model):
    SHAPE_CHOICES = [
        ('rectangle', 'Rettangolo'),
        ('square', 'Quadrato'),
        ('triangle', 'Triangolo'),
    ]

    name = models.CharField(max_length=100)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookshelves')
    shelf_count = models.IntegerField(default=1)

    # Campi di posizione esistenti
    pos_x = models.IntegerField(default=50)
    pos_y = models.IntegerField(default=50)
    width = models.IntegerField(default=150)
    height = models.IntegerField(default=50)

    # --- NUOVI CAMPI PER FORMA E ROTAZIONE ---
    shape_type = models.CharField(max_length=20, choices=SHAPE_CHOICES, default='rectangle')
    rotation = models.IntegerField(default=0) # Gradi: 0, 90, 180, 270

    def __str__(self):
        return f"{self.name} in {self.room.name}"

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True)
    summary = models.TextField(blank=True)
    google_books_id = models.CharField(max_length=50, blank=True, null=True)
    cover_url = models.URLField(blank=True, null=True)
    published_date = models.CharField(max_length=20, blank=True, null=True)
    average_rating = models.FloatField(null=True, blank=True)
    # Your personal data
    bookshelf = models.ForeignKey(Bookshelf, on_delete=models.CASCADE, related_name='books')
    shelf_number = models.IntegerField()
    user_rating = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title