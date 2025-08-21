# Virtual Library AI

> Bring your physical library to life in the digital world. Snap a photo, and let AI do the rest.

A web application built with Python and Django that allows you to digitize and organize your personal book collection. The core idea is simple: take a picture of a bookshelf, and the application, powered by Google Gemini, will automatically identify the books, retrieve their information, and add them to your virtual library.

The application allows you to organize your collection into virtual "rooms" and "bookshelves," replicating the physical layout of your home.

## Key Features

-   **Virtual Organization:** Create custom rooms and bookshelves to map out your home library.
-   **AI-Powered Digitization:** Upload an image of a shelf, and the AI (Google Gemini) will recognize the books present.
-   **Data Enrichment:** Every recognized book is enriched with detailed information (cover art, summary, author, publication date) via the Google Books API.
-   **Simple Interface:** A clean web interface, built with Django templates, to browse your rooms, bookshelves, and books.
-   **Admin Panel:** Leverage Django's powerful built-in admin panel to manually manage all your data.

## Built With

-   **Backend:** [Django](https://www.djangoproject.com/)
-   **Language:** [Python](https://www.python.org/)
-   **Artificial Intelligence:** [Google Gemini API (gemini-1.5-flash)](https://ai.google.dev/)
-   **Book Database:** [Google Books API](https://developers.google.com/books)
-   **Local Database:** SQLite (default configuration)

## Getting Started

Follow these steps to get a copy of the project up and running on your local machine.

### Prerequisites

Ensure you have Python 3.8+ and pip installed on your system.
-   [Python & pip](https://www.python.org/downloads/)

### Installation

1.  **Get a Google API Key**
    -   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    -   Create a new project.
    -   Enable the following APIs: **"Vertex AI API"** and **"Google Books API"**.
    -   Set up a billing account (this is required to unlock the free tier limits, but you will not be charged for the usage levels in this project).
    -   Create an API Key from the "Credentials" section.

2.  **Clone the Repository**
    ```sh
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
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
    -   In the `library_project/settings.py` file, find the `GOOGLE_API_KEY` line and paste your key.
    ```python
    # In library_project/settings.py
    GOOGLE_API_KEY = "YOUR_SECRET_API_KEY_HERE"
    ```

6.  **Prepare the Database**
    -   Run the migrations to create the database schema.
    ```sh
    python manage.py migrate
    ```

7.  **Create a Superuser**
    -   This account will be used to access the admin panel (`/admin/`).
    ```sh
    python manage.py createsuperuser
    ```
    -   Follow the prompts to create your admin user.

8.  **Run the Server**
    ```sh
    python manage.py runserver
    ```
    -   Open your browser and navigate to `http://127.0.0.1:8000/`.

## How the Magic Works

The core of the project is the digitization process, which happens in three steps:

1.  **Upload & AI Analysis:** When an image is uploaded, it is sent to the Google Gemini API with a detailed prompt instructing it to act as an expert librarian and return a clean JSON list of titles and authors.
2.  **Data Enrichment:** For each book identified by Gemini, the system queries the Google Books API using the title and author. This allows for the retrieval of rich and reliable metadata like the cover art, summary, a unique ID, etc. A fallback logic is implemented to search by title only if the title+author combination yields no results.
3.  **Database Saving:** The enriched book data is finally saved to the local database and associated with the user's chosen bookshelf.

## Roadmap

-   [ ] **Multi-User Support:** Implement a full authentication system to allow multiple users to manage their own private libraries.
-   [ ] **Personal Ratings:** Add the ability for users to give a rating (e.g., 1 to 5 stars) to each book.
-   [ ] **UI/UX Enhancements:** Develop a more modern frontend (e.g., with a JavaScript framework like React or Vue) for a smoother user experience.
-   [ ] **Manual Entry:** Create a form to manually add a book that the AI might have missed.
-   [ ] **Book Detail Page:** Create a dedicated page for each book to display all its information (summary, publication date, etc.).

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

## Acknowledgements

-   Initial inspiration drawn from the [Bookshelf-digitization](https://github.com/sanchitgl/Bookshelf-digitization) project by sanchitgl.
