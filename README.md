# Desktop PDF Reader

A desktop PDF reader built with Python, PyQt6, and PyMuPDF.

## Implemented Features

- Open PDF files
- Render PDF pages
- Navigate to the next page
- Navigate to the previous page
- Display current page and total page count
- Save the last read page for each PDF
- Restore the last read page when reopening a PDF
- Add bookmarks for PDF pages
- View bookmarks for the active PDF
- Jump to a bookmarked page

## User Data

Reading progress is stored in `data/progress.json`. Progress records are keyed by the stable `document_id` generated from each PDF's resolved file path.

Bookmarks are stored in `data/bookmarks.json`. Bookmark lists are keyed by the same `document_id`, and each bookmark stores its page index, label, and creation timestamp.

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
