# Virtual Library AI

> A Django-powered web application to bring your physical library to life. Snap a photo of a bookshelf, and let AI catalog your collection.

This project allows you to digitize and organize your personal book collection by simply taking a picture. Powered by Google's Gemini model, the application identifies books from an image, fetches detailed information via the Google Books API, and adds them to a virtual library that mirrors your home's physical layout.

Organize your collection into virtual "rooms" and "bookshelves," search your entire catalog, and visually locate any book on its shelf.

<!-- TODO: Add a GIF or screenshot of the application in action. e.g., showing the room editor or the book list. -->

<img width="1723" height="1646" alt="immagine" src="https://github.com/user-attachments/assets/c1fc2328-2c3f-415d-8095-da24b06e1e5b" />

## Key Features

-   **AI-Powered Digitization:** Upload an image of a shelf, and Google's Gemini model will recognize the titles and authors.
-   **Rich Metadata:** Each recognized book is automatically enriched with cover art, a summary, publication date, and more from the Google Books API.
-   **Virtual Room Layout:** Design a virtual floor plan of your rooms using an interactive drag-and-drop editor. Create, resize, rotate, and position your bookshelves to match your home.
-   **Visual Book Location:** On each book's detail page, see a visual representation of the room, highlighting the exact bookshelf and shelf where the book is located.
-   **Add from URL:** Manually add books by simply pasting a URL from Google Books or Amazon.
-   **Full-Text Search:** A powerful search function to find books by title or author across your entire collection.
-   **Personal Ratings:** Rate your books on a 1-5 scale.
-   **Admin Panel:** Leverage Django's powerful built-in admin panel to manually manage rooms, bookshelves, and books.

## Tech Stack

-   **Backend:** 🐍 Django
-   **Language:** 💻 Python 3
-   **AI Vision:** ✨ Google Gemini API
-   **Book Database:** 📚 Google Books API
-   **Frontend:** 📄 HTML, CSS, JavaScript (with Konva.js for the editor)
-   **Database:** 📦 SQLite (default for development)

## Getting Started

Follow these steps to get a copy of the project up and running on your local machine for development and testing.

### Prerequisites

-   Python 3.8+ and pip
-   Git for cloning the repository

### Installation

1.  **Get a Google API Key**
    -   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    -   Create a new project and enable the **"Vertex AI API"** and **"Google Books API"**.
    -   Set up a billing account (required to use the APIs, but the free tier is sufficient for this project).
    -   Go to "Credentials" and create a new **API Key**. Copy it for the next steps.

2.  **Clone the Repository**
    ```sh
    git clone https://github.com/your-username/virtual-library-ai.git
    cd virtual-library-ai
    ```

3.  **Create and Activate a Virtual Environment**
    ```sh
    # Create the environment
    python -m venv venv

    # Activate on Windows
    .\venv\Scripts\activate

    # Activate on macOS/Linux
    source venv/bin/activate
    ```

4.  **Install Dependencies**
    ```sh
    pip install -r requirements.txt
    ```

5.  **Configure Environment Variables**
    -   Create a new file named `.env` in the root directory of the project (the same level as `manage.py`).
    -   Copy the contents of your `settings.py` `SECRET_KEY` and your Google API Key into this `.env` file like so:
    ```
    # .env
    SECRET_KEY=your_django_secret_key_here
    GOOGLE_API_KEY=your_google_api_key_here
    ```
    *(The `settings.py` file is already configured to read these values from the `.env` file.)*

6.  **Prepare the Database**
    -   Run the migrations to create the database schema.
    ```sh
    python manage.py migrate
    ```

7.  **Create a Superuser**
    -   This account is used to access the Django admin panel at `/admin/`.
    ```sh
    python manage.py createsuperuser
    ```
    -   Follow the prompts to set up your username and password.

8.  **Run the Development Server**
    ```sh
    python manage.py runserver
    ```
    -   Open your browser and navigate to `http://127.0.0.1:8000/`.

## How The Magic Works

The digitization process is a three-step pipeline:

1.  **AI Analysis:** An uploaded image is sent to the Google Gemini API with a detailed prompt instructing it to act as an expert librarian. It identifies book spines and returns a structured JSON list of titles and authors, carefully ignoring irrelevant text.
2.  **Data Enrichment:** For each book identified, the system queries the Google Books API. It first attempts a high-precision search with both title and author. If that fails, it falls back to searching by title alone. This retrieves rich, reliable metadata.
3.  **Database Persistence:** The enriched book data is finally saved to the database and associated with the user's chosen room, bookshelf, and shelf number.

## Roadmap

-   [ ] **Full Multi-User Support:** Implement a complete Django authentication system (registration, login, password reset) so multiple users can manage their own private libraries.
-   [ ] **Dockerization:** Create `Dockerfile` and `docker-compose.yml` files to make setup and deployment even easier.
-   [ ] **Advanced Search & Filtering:** Enhance the search page with filters for rating, room, or publication date.
-   [ ] **API Enhancement:** Refactor the internal APIs using Django REST Framework for better structure and scalability.
-   [ ] **Frontend Modernization:** Consider migrating parts of the frontend to a reactive JavaScript framework like Vue.js or React for a smoother, single-page application experience.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgements

-   Initial inspiration drawn from the [Bookshelf-digitization](https://github.com/sanchitgl/Bookshelf-digitization) project.
