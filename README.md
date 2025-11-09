# Student Portal

A Django-based web application for students to manage their academic activities.

## Features

-   **Notes**: Create, view, and delete notes.
-   **Homework**: Track homework assignments, mark them as complete, and delete them.
-   **YouTube Downloader**: Download YouTube videos.
-   **To-do List**: Manage a personal to-do list.
-   **Books**: Search for books using the Google Books API.
-   **Dictionary**: Look up word definitions.
-   **Wikipedia**: Search for articles on Wikipedia.
-   **Conversion**: Convert between different units.
-   **User Management**: Register, login, logout, and view user profile.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/studyPortal.git
    cd studyPortal
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv portal
    source portal/bin/activate  # On Windows, use `portal\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt

4.  **Apply migrations:**
    ```bash
    python manage.py migrate
    ```

## Usage

1.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

2.  Open your web browser and go to `http://127.0.0.1:8000/`.

