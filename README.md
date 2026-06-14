# Desktop PDF Reader

A desktop PDF reader built with Python, PyQt6, and PyMuPDF.

## Phase 1 Features

- Open PDF files
- Render PDF pages
- Navigate to the next page
- Navigate to the previous page
- Display current page and total page count

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Project Structure

The application separates UI, service logic, models, configuration, and utilities so later features such as bookmarks, notes, recent books, dark mode, and AI tools can be added without crowding the main window.
