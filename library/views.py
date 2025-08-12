from django.shortcuts import render
# Assicurati che tutti e tre i modelli siano importati
from .models import Room, Bookshelf, Book
from django.shortcuts import render, redirect, get_object_or_404
import os
from django.core.files.storage import FileSystemStorage 
# Importa la funzione che abbiamo appena creato
from . import book_detector
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q
from . import book_scraper # Importa il nostro nuovo modulo
from .forms import BookForm

# ... home e bookshelf_list views restano invariate ...
def home(request):
    rooms = Room.objects.all()
    context = {'rooms': rooms}
    return render(request, 'library/home.html', context)

def bookshelf_list(request, room_id):
    room = Room.objects.get(pk=room_id)
    bookshelves = room.bookshelves.all()
    context = {
        'room': room,
        'bookshelves': bookshelves
    }
    return render(request, 'library/bookshelf_list.html', context)

# In library/views.py

def book_list(request, bookshelf_id):
    bookshelf = get_object_or_404(Bookshelf, pk=bookshelf_id)
    
    # --- NUOVA LOGICA DI RAGGRUPPAMENTO ---
    # Prendiamo tutti i libri di questa libreria, ordinati per titolo
    all_books_on_shelf = bookshelf.books.all().order_by('title')
    
    # Creiamo un dizionario per contenere i nostri ripiani
    # La chiave sarà il numero del ripiano, il valore sarà la lista dei libri su quel ripiano
    shelves_with_books = {}
    
    # Iteriamo per ogni ripiano che la libreria dovrebbe avere (da 1 fino a shelf_count)
    for i in range(1, bookshelf.shelf_count + 1):
        # Filtriamo i libri che appartengono a questo specifico ripiano
        books_on_this_shelf = [book for book in all_books_on_shelf if book.shelf_number == i]
        # Aggiungiamo la lista (anche se vuota) al nostro dizionario
        shelves_with_books[i] = books_on_this_shelf
        
    context = {
        'bookshelf': bookshelf,
        # Passiamo al template la nostra nuova struttura dati raggruppata
        'shelves_with_books': shelves_with_books, 
        # Passiamo anche la lista completa per le card a sinistra
        'all_books': all_books_on_shelf 
    }
    return render(request, 'library/book_list.html', context)

# In library/views.py

def upload_shelf_image(request):
    bookshelves = Bookshelf.objects.all()

    if request.method == 'POST' and request.FILES.getlist('image'):
        image_files = request.FILES.getlist('image')
        bookshelf_id = request.POST.get('bookshelf')
        
        try:
            shelf_number = int(request.POST.get('shelf_number', 1))
        except (ValueError, TypeError):
            shelf_number = 1
        
        target_bookshelf = get_object_or_404(Bookshelf, pk=bookshelf_id)
        
        if shelf_number > target_bookshelf.shelf_count:
            target_bookshelf.shelf_count = shelf_number
            target_bookshelf.save()
        
        # Inizia il ciclo per ogni file caricato
        for image_file in image_files:
            # --- INIZIA IL BLOCCO DI SICUREZZA ---
            try: 
                # Questo è il tuo codice corretto, ora protetto
                print(f"DEBUG: Processo l'immagine: {image_file.name}")
                
                fs = FileSystemStorage()
                filename = fs.save(image_file.name, image_file)
                uploaded_file_path = fs.path(filename)

                found_books_data = book_detector.process_shelf_image(uploaded_file_path)
                
                fs.delete(filename)

                for book_data in found_books_data:
                    google_id = book_data.get('google_books_id')
                    if google_id and not Book.objects.filter(google_books_id=google_id, bookshelf=target_bookshelf).exists():
                        Book.objects.create(
                            title=book_data.get('title', 'No Title Provided'),
                            author=book_data.get('author', 'Unknown Author'),
                            bookshelf=target_bookshelf,
                            shelf_number=shelf_number,
                            summary=book_data.get('summary', ''),
                            google_books_id=google_id,
                            cover_url=book_data.get('cover_url', ''),
                            published_date=book_data.get('published_date', '')
                        )
            
            except Exception as e:
                # Se qualcosa va storto con questa immagine, lo registriamo e andiamo avanti
                print(f"ERRORE: Impossibile processare il file {image_file.name}. Causa: {e}")
                continue # Salta alla prossima immagine
            # --- FINISCE IL BLOCCO DI SICUREZZA ---
        
        # Questa riga viene eseguita solo dopo che il ciclo è finito (o tutte le immagini sono state processate)
        return redirect('book-list', bookshelf_id=target_bookshelf.id)

    context = { 'bookshelves': bookshelves }
    return render(request, 'library/upload_form.html', context)

# In library/views.py

# In library/views.py

# In library/views.py

def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    if request.method == 'POST':
        rating = request.POST.get('user_rating')
        if rating:
            book.user_rating = int(rating)
            book.save()
            return redirect('book-detail', book_id=book.id)

    # Prendiamo la stanza e tutte le librerie al suo interno
    room = book.bookshelf.room
    bookshelves_in_room = room.bookshelves.all()
    
    # --- RI-AGGIUNGIAMO QUESTA LOGICA FONDAMENTALE ---
    # Creiamo una lista di numeri per i ripiani della libreria specifica del libro
    shelf_range = range(1, book.bookshelf.shelf_count + 1)
    
    context = {
        'book': book,
        'bookshelves_in_room': bookshelves_in_room,
        'shelf_range': shelf_range, # Passiamo di nuovo la lista dei ripiani al template
    }
    return render(request, 'library/book_detail.html', context)

def room_editor(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    # Passiamo sia la stanza che le sue librerie al template
    context = {
        'room': room,
        'bookshelves': room.bookshelves.all()
    }
    return render(request, 'library/room_editor.html', context)

# --- LA NUOVA SUPER-VIEW PER L'API ---

# In library/views.py

@csrf_exempt
@require_http_methods(["POST", "PUT", "DELETE"])
def bookshelf_api_dispatcher(request):
    try:
        # --- BLOCCO POST (CREAZIONE) ORA COMPLETO ---
        if request.method == 'POST':
            data = json.loads(request.body)
            # Trova la stanza a cui appartiene la nuova libreria
            room = get_object_or_404(Room, pk=data['room_id'])
            # Crea la nuova libreria nel database
            new_shelf = Bookshelf.objects.create(
                name=data['name'],
                shape_type=data['shape_type'],
                room=room
            )
            # Restituisce i dati del nuovo oggetto a JavaScript, incluso il nuovo ID!
            return JsonResponse({
                'id': new_shelf.id, 
                'name': new_shelf.name, 
                'shape_type': new_shelf.shape_type,
                'x': new_shelf.pos_x, 
                'y': new_shelf.pos_y, 
                'width': new_shelf.width,
                'height': new_shelf.height, 
                'rotation': new_shelf.rotation
            })

        # --- BLOCCO PUT (AGGIORNAMENTO) ---
        elif request.method == 'PUT':
            data = json.loads(request.body)
            updated_ids = []
            for shelf_data in data:
                shelf = get_object_or_404(Bookshelf, pk=shelf_data['id'])
                
                # --- AGGIUNGIAMO LA MODIFICA DEL NOME QUI ---
                shelf.name = shelf_data.get('name', shelf.name)
                
                shelf.pos_x = shelf_data.get('x', shelf.pos_x)
                shelf.pos_y = shelf_data.get('y', shelf.pos_y)
                shelf.width = shelf_data.get('width', shelf.width)
                shelf.height = shelf_data.get('height', shelf.height)
                shelf.shape_type = shelf_data.get('shape_type', shelf.shape_type)
                shelf.rotation = shelf_data.get('rotation', shelf.rotation)
                
                shelf.save()
                updated_ids.append(shelf.id)
            return JsonResponse({'status': 'success', 'message': f'Librerie {updated_ids} aggiornate'})

        # --- BLOCCO DELETE (CANCELLAZIONE) ---
        elif request.method == 'DELETE':
            data = json.loads(request.body)
            shelf = get_object_or_404(Bookshelf, pk=data['id'])
            shelf.delete()
            return JsonResponse({'status': 'success', 'message': 'Libreria cancellata'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return HttpResponseBadRequest()

# In library/views.py

def book_search(request):
    # Iniziamo con una queryset che contiene tutti i libri
    queryset = Book.objects.all()
    
    # Prendiamo i parametri dall'URL (es. ?q=...&rating=...)
    query = request.GET.get('q')
    rating_filter = request.GET.get('rating')

    # Se è stata fornita una query di testo...
    if query:
        # Filtriamo cercando la query sia nel titolo CHE nell'autore.
        # Q() è uno strumento potente per creare query complesse con OR.
        # __icontains significa "contiene, ignorando maiuscole/minuscole".
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
        
    # Se è stato fornito un filtro per il rating...
    if rating_filter:
        # __gte significa "greater than or equal to" (maggiore o uguale a).
        queryset = queryset.filter(user_rating__gte=rating_filter)

    context = {
        'books': queryset,
        'query': query,
        'rating_filter': rating_filter,
    }
    return render(request, 'library/search_results.html', context)


def add_book_by_url(request):
    found_book = None
    
    # --- FASE 2: GESTIONE DEL SALVATAGGIO ---
    # Questo codice viene eseguito quando l'utente clicca "Aggiungi alla Libreria"
    if request.method == 'POST' and 'confirm_add' in request.POST:
        bookshelf_id = request.POST.get('bookshelf')
        shelf_number = request.POST.get('shelf_number')
        
        # Prende i dati del libro salvati nella sessione
        book_data = request.session.get('found_book_data')
        
        if book_data and bookshelf_id:
            target_bookshelf = get_object_or_404(Bookshelf, pk=bookshelf_id)
            if not Book.objects.filter(google_books_id=book_data.get('google_books_id')).exists():
                Book.objects.create(
                    title=book_data.get('title'),
                    author=book_data.get('author'),
                    summary=book_data.get('summary', ''),
                    google_books_id=book_data.get('google_books_id', ''),
                    cover_url=book_data.get('cover_url', ''),
                    published_date=book_data.get('published_date', ''),
                    bookshelf=target_bookshelf,
                    shelf_number=shelf_number
                )
            # Reindirizza alla libreria dove è stato aggiunto il libro
            return redirect('book-list', bookshelf_id=bookshelf_id)

    # --- FASE 1: GESTIONE DELLA RICERCA URL ---
    # Questo codice viene eseguito quando l'utente incolla un URL e clicca "Cerca"
    if request.method == 'POST' and 'fetch_url' in request.POST:
        url = request.POST.get('url')
        if url:
            found_book = book_scraper.scrape_book_data_from_url(url)
            # Salva il risultato nella sessione per il prossimo passo
            request.session['found_book_data'] = found_book

    context = {
        'found_book': found_book,
        'bookshelves': Bookshelf.objects.all()
    }
    return render(request, 'library/add_by_url.html', context)


# --- NUOVA VIEW PER MODIFICARE UN LIBRO ---
def book_edit(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book-detail', book_id=book.id)
    else:
        form = BookForm(instance=book)

    context = {
        'form': form,
        'book': book
    }
    return render(request, 'library/book_edit.html', context)

# --- NUOVA VIEW PER ELIMINARE UN LIBRO ---
@require_http_methods(["POST"]) # Accetta solo richieste POST per sicurezza
def book_delete(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    bookshelf_id = book.bookshelf.id # Salviamo l'id per il redirect
    book.delete()
    return redirect('book-list', bookshelf_id=bookshelf_id)


# --- NUOVA API VIEW PER I MENU A TENDINA DINAMICI ---
def get_bookshelves_for_room(request, room_id):
    bookshelves = Bookshelf.objects.filter(room_id=room_id).values('id', 'name')
    return JsonResponse(list(bookshelves), safe=False)

# --- NUOVA VIEW PER AGGIORNARE IL NUMERO DI RIPIANI ---
@require_http_methods(["POST"]) # Per sicurezza, accettiamo solo richieste POST
def update_shelf_count(request, bookshelf_id):
    # Trova la libreria che stiamo modificando
    bookshelf = get_object_or_404(Bookshelf, pk=bookshelf_id)
    
    try:
        # Prendi il nuovo numero di ripiani dal form che abbiamo inviato
        new_count = int(request.POST.get('new_shelf_count'))
        
        # Assicurati che il numero sia valido (almeno 1)
        if new_count >= 1:
            bookshelf.shelf_count = new_count
            bookshelf.save() # Salva la modifica nel database
            
    except (ValueError, TypeError):
        # Se l'input non è un numero valido, non facciamo nulla
        pass

    # In ogni caso, reindirizza l'utente alla pagina da cui proveniva
    return redirect('book-list', bookshelf_id=bookshelf_id)