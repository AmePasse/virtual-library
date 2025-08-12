# In library/book_scraper.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, quote_plus
import re # Importiamo il modulo per le espressioni regolari

# --- NUOVA FUNZIONE PER LO SCRAPING DI GOOGLE IMMAGINI ---
def find_cover_on_google_images(book_title):
    """
    Esegue una ricerca su Google Immagini e tenta di estrarre l'URL della prima immagine VALIDA.
    """
    try:
        search_query = f"{book_title} libro copertina"
        encoded_query = quote_plus(search_query)
        search_url = f"https://www.google.com/search?tbm=isch&q={encoded_query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        print(f"DEBUG (Google Images): Cerco copertina per '{search_query}'...")
        page = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        images = soup.find_all('img')
        
        for img in images:
            src = img.get('src')
            
            # --- NUOVE REGOLE DI FILTRAGGIO PIÙ SELETTIVE ---
            if (src and 
                src.startswith('https://') and 
                'gstatic.com' not in src and    # Ignora i loghi e le icone di Google
                not src.endswith('.svg')):      # Ignora le immagini vettoriali (spesso loghi)
                
                print(f"DEBUG (Google Images): Trovato URL VALIDO: {src}")
                return src
                
    except Exception as e:
        print(f"ERRORE durante lo scraping di Google Immagini: {e}")
        return None
    
    print("DEBUG (Google Images): Nessun URL di copertina valido trovato.")
    return None


# --- FUNZIONE PRINCIPALE MODIFICATA CON LA LOGICA DI FALLBACK ---
def get_book_details_from_google_api(book_id=None, query=None):
    """
    Funzione potenziata. Se l'API di Google Books non restituisce una copertina,
    tenta di cercarne una su Google Immagini come piano B.
    """
    if not book_id and not query:
        return None

    books_api_url = "https://www.googleapis.com/books/v1/volumes"
    
    if book_id:
        response = requests.get(f"{books_api_url}/{book_id}")
    else:
        params = {'q': query, 'langRestrict': 'it,en', 'maxResults': 1}
        response = requests.get(books_api_url, params=params)

    if response.status_code == 200 and ('id' in response.json() or response.json().get('totalItems', 0) > 0):
        data = response.json()
        item = data if book_id else data.get('items', [{}])[0]
        
        book_data = item.get('volumeInfo', {})
        authors_list = book_data.get('authors', ['Unknown Author'])
        
        # Estrai i dati come prima
        result = {
            'title': book_data.get('title', 'N/A'),
            'author': ", ".join(authors_list),
            'summary': book_data.get('description', ''),
            'published_date': book_data.get('publishedDate', ''),
            'google_books_id': item.get('id', ''),
            'cover_url': book_data.get('imageLinks', {}).get('thumbnail', '')
        }

        # --- LOGICA DI FALLBACK ---
        # Se, e solo se, l'URL della copertina è vuoto...
        if not result['cover_url'] and result['title'] != 'N/A':
            print(f"INFO: Copertina non trovata per '{result['title']}' su Google Books. Tento il fallback su Google Immagini.")
            # ...chiama la nostra nuova funzione di scraping!
            image_url = find_cover_on_google_images(result['title'])
            if image_url:
                result['cover_url'] = image_url # Aggiorna il risultato con la copertina trovata

        return result
        
    return None

def scrape_book_data_from_url(url):
    """
    Analizza un URL, estrae i dati e li usa per chiamare l'API di Google Books.
    Versione migliorata per Amazon.
    """
    
    # --- Caso 1: Google Books (invariato) ---
    if 'books.google' in url:
        try:
            parsed_url = urlparse(url)
            book_id = parse_qs(parsed_url.query)['id'][0]
            print(f"DEBUG: Trovato Google Books ID: {book_id}")
            return get_book_details_from_google_api(book_id=book_id)
        except Exception as e:
            print(f"Errore nell'analisi dell'URL di Google Books: {e}")
            return None

    # --- Caso 2: Amazon (Logica Robusta) ---
    elif 'amazon' in url:
        try:
            # L'ISBN è spesso nell'URL (es. /dp/881802731X/)
            # Usiamo un'espressione regolare per trovarlo. È un codice di 10 o 13 cifre.
            isbn_match = re.search(r'/(dp|gp/product)/(\w{10}|\d{13})', url)
            if isbn_match:
                isbn = isbn_match.group(2)
                print(f"DEBUG: Trovato ISBN dall'URL di Amazon: {isbn}")
                # La ricerca per ISBN è la più precisa possibile!
                return get_book_details_from_google_api(query=f"isbn:{isbn}")

            # Se non c'è l'ISBN, proviamo a leggere il titolo dalla pagina
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, 'html.parser')
            
            title = soup.find('span', {'id': 'productTitle'})
            if title:
                title_text = title.text.strip()
                print(f"DEBUG: Trovato Titolo dalla pagina Amazon: '{title_text}'")
                return get_book_details_from_google_api(query=title_text)

        except Exception as e:
            print(f"Errore nello scraping di Amazon: {e}")
            return None
    
    return None