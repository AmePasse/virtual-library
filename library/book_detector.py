# In library/book_detector.py
import requests
import google.generativeai as genai
import json
from django.conf import settings
from . import book_scraper
genai.configure(api_key=settings.GOOGLE_API_KEY)

# --- LA FUNZIONE DI RICERCA CON LOGICA DI FALLBACK ---
def find_book_details(title, author):
    """
    Cerca un libro. Prima tenta con titolo+autore, se fallisce, riprova solo con il titolo.
    """
    books_api_url = "https://www.googleapis.com/books/v1/volumes"
    
    # --- Tentativo 1: Ricerca ad alta precisione (Titolo + Autore) ---
    query1 = f"intitle:{title}+inauthor:{author}"
    params1 = {'q': query1, 'key': settings.GOOGLE_API_KEY, 'langRestrict': 'it,en', 'maxResults': 1}
    response = requests.get(books_api_url, params=params1)
    
    # Se la ricerca precisa fallisce, proviamo una più generica
    if response.status_code != 200 or response.json().get('totalItems', 0) == 0:
        print(f"DEBUG: Ricerca precisa fallita per '{title}' di '{author}'. Tento con il solo titolo...")
        # --- Tentativo 2: Fallback con il solo titolo ---
        query2 = f"intitle:{title}"
        params2 = {'q': query2, 'key': settings.GOOGLE_API_KEY, 'langRestrict': 'it,en', 'maxResults': 1}
        response = requests.get(books_api_url, params=params2)

    # Ora processiamo la risposta (che sia del primo o del secondo tentativo)
    if response.status_code == 200 and response.json().get('totalItems', 0) > 0:
        item = response.json()['items'][0]
        book_data = item['volumeInfo']
        
        authors_list = book_data.get('authors', [author])
        
        return {
            'title': book_data.get('title', title),
            'author': ", ".join(authors_list),
            'summary': book_data.get('description', ''),
            'published_date': book_data.get('publishedDate', ''),
            'google_books_id': item.get('id', ''),
            'cover_url': book_data.get('imageLinks', {}).get('thumbnail', '')
        }
    return None

# Il resto del file rimane identico
def process_shelf_image(image_path):
    print("DEBUG: Avvio analisi immagine con Gemini (Prompt Professionale)...")
    
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    try:
        with open(image_path, 'rb') as f:
            image_file = {'mime_type': 'image/jpeg', 'data': f.read()}
    except IOError as e:
        print(f"Errore nell'apertura del file immagine: {e}")
        return []

    prompt = """
    Sei un assistente bibliotecario virtuale, specializzato nel digitalizzare collezioni di libri da immagini. Il tuo compito è analizzare l'immagine fornita con la massima precisione.

    Le tue istruzioni sono:
    1.  **IDENTIFICA SOLO LIBRI:** Analizza l'immagine e identifica solo le coste dei libri. Ignora completamente loghi di case editrici (es. "Feltrinelli", "Mondadori"), numeri di collana (es. "1062", "444"), e qualsiasi altro testo che non sia chiaramente un titolo o un autore.
    2.  **ESTRAI TITOLO E AUTORE:** Per ogni libro identificato, estrai il suo titolo completo e il nome completo dell'autore.
    3.  **GESTISCI CASI INCERTI:**
        - Se riesci a leggere chiaramente solo il nome di un autore (es. "YOURCENAR") ma non il titolo, formatta l'output con il titolo "Unknown" e l'autore che hai letto.
        - Se riesci a leggere chiaramente solo un titolo ma non l'autore, formatta l'output con il titolo che hai letto e l'autore "Unknown".
        - Se un libro è illeggibile o non sei sicuro, **non includerlo nell'output**. È meglio omettere un libro che inventarne uno.
    4.  **FORMATO DI OUTPUT RIGIDO:** Restituisci il risultato **esclusivamente** come un array JSON valido. Ogni elemento dell'array deve essere un oggetto con due chiavi obbligatorie: "title" e "author". Non aggiungere nessun commento o testo prima o dopo l'array JSON.

    Esempio di output perfetto:
    [
        { "title": "Memorie di Adriano", "author": "Marguerite Yourcenar" },
        { "title": "Il Piccolo Principe", "author": "Antoine de Saint-Exupéry" },
        { "title": "Unknown", "author": "Colette" }
    ]
    """
    
    try:
        response = model.generate_content([prompt, image_file])
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        print(f"DEBUG: Risposta testuale pulita da Gemini ->\n{cleaned_response_text}")
        identified_books = json.loads(cleaned_response_text)
    except Exception as e:
        print(f"ERRORE: Impossibile chiamare Gemini o analizzare la sua risposta JSON. Errore: {e}")
        return []

    final_book_list = []
    processed_ids = set()
    
    for book in identified_books:
        title = book.get("title")
        author = book.get("author")
        
        if title and author and title != "Unknown":
            print(f"DEBUG: Cerco dettagli per '{title}' di '{author}'...")
            # --- ECCO LA MODIFICA ---
            # Chiamiamo la funzione potenziata dal nostro scraper!
            details = book_scraper.get_book_details_from_google_api(query=f"intitle:{title}+inauthor:{author}")
            
            if details and details['google_books_id'] not in processed_ids:
                final_book_list.append(details)
                processed_ids.add(details['google_books_id'])
                print(f"DEBUG: Dettagli trovati e aggiunti per '{details['title']}'")

    return final_book_list