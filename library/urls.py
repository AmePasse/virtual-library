from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='library-home'),
    path('room/<int:room_id>/', views.bookshelf_list, name='bookshelf-list'),
    path('bookshelf/<int:bookshelf_id>/', views.book_list, name='book-list'),
     # --- AGGIUNGI QUESTO NUOVO PATH ---
    path('book/<int:book_id>/', views.book_detail, name='book-detail'),
    path('room/<int:room_id>/editor/', views.room_editor, name='room-editor'),
    path('upload/', views.upload_shelf_image, name='upload-image'),
    path('api/bookshelf/', views.bookshelf_api_dispatcher, name='bookshelf-api-dispatcher'),
    path('search/', views.book_search, name='book-search'),
    path('add-by-url/', views.add_book_by_url, name='add-book-by-url'),
    path('bookshelf/<int:bookshelf_id>/update-count/', views.update_shelf_count, name='update-shelf-count'),
    path('book/<int:book_id>/edit/', views.book_edit, name='book-edit'),
    path('book/<int:book_id>/delete/', views.book_delete, name='book-delete'),
    path('api/get-bookshelves-for-room/<int:room_id>/', views.get_bookshelves_for_room, name='api-get-bookshelves'),
]
