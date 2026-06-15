# Desktop PDF Reader

A desktop PDF reader built with Python, PyQt6, and PyMuPDF.

## Implemented Features

- Open PDF files
- Render PDF pages
- Navigate with floating next and previous page controls
- Display current page and total page count
- Zoom in, zoom out, and reset zoom to 100%
- Save the last read page for each PDF
- Restore the last read page when reopening a PDF
- Add bookmarks for PDF pages
- View bookmarks for the active PDF
- Jump to a bookmarked page
- Rename, delete, pin, and unpin bookmarks
- Smart Search for direct page jumps, chapter matches, and full-text matches
- Clear search results by clearing the search box or using the Clear button

## User Data

Reading progress is stored in `data/progress.json`. Progress records are keyed by the stable `document_id` generated from each PDF's resolved file path.

Bookmarks are stored in `data/bookmarks.json`. Bookmark lists are keyed by the same `document_id`, and each bookmark stores its ID, page index, label, creation timestamp, and pinned state.

## Smart Search

The toolbar search box supports page numbers, chapter queries, and text queries. Direct page-number searches jump without scanning PDF text. Chapter and text searches build an in-memory cache for the currently opened PDF on first use, then reuse that cache for later searches until another PDF is opened.

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
