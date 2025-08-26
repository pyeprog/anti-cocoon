# Anti-Cocoon

A web scraping tool for collecting video data from Bilibili using Playwright and storing it in a SQLite database.

## Overview

Anti-Cocoon is designed to automatically search for and collect video metadata from Bilibili, a popular Chinese video sharing platform. The application uses Playwright for web automation to navigate the site, extract video information, and store it in a structured database format.

## Features

- Automated Bilibili video search and data collection
- Web scraping using Playwright with Chromium browser
- Data storage in SQLite database using SQLModel
- Scheduled execution with configurable intervals
- Support for collecting multiple pages of search results
- Extraction of key video metadata including:
  - Title
  - Link
  - Author
  - Release date
  - View count
  - Barrage count (comments)
  - Duration

## Prerequisites

- Python 3.11 or higher
- Poetry (for dependency management)

## Installation

```bash
poetry install
playwright install chromium
```

## Usage

### Manual Execution

To run the scraper manually:

```bash
poetry run python main.py
```

### Scheduled Execution

The application is configured to run on a schedule (every 4 hours by default). The scheduler will automatically search for videos related to:
- "AI agent"
- "AIF�" (AI frameworks)
- "AI'!�" (AI large models)

### Customizing Searches

To modify the search terms or frequency, edit the `main.py` file:

```python
# In main.py, modify these lines:
await search_from_bili("your search term", number_of_pages)
```

And adjust the schedule interval:

```python
# Change the frequency (currently every 4 hours)
schedule.every(4).hours.do(main)
```

## Data Storage

Collected data is stored in a SQLite database at `.data/bili.sqlite.db`. The database contains a `video` table with the following schema:

- `title` (Primary Key): Video title
- `link`: URL to the video
- `author`: Creator of the video
- `release_date`: When the video was published
- `collect_date`: When the video was collected
- `n_views`: Number of views
- `n_barrages`: Number of barrages/comments
- `duration_sec`: Video duration in seconds
- `source`: Source of the data (currently "search")

## Project Structure

```
.
├── README.md
├── main.py                  # Entry point and scheduler
├── pyproject.toml           # Project dependencies
├── anti_cocoon/             # Main package
│   ├── __init__.py
│   ├── util.py              # Utility functions
│   └── bilibili/            # Bilibili-specific code
│       ├── __init__.py
│       ├── app.py           # Main Bilibili application logic
│       ├── search_page.py   # Search page interaction
│       ├── video_card.py    # Video card element model
│       ├── video_card_parser.py  # Video card data extraction
│       └── model/
│           ├── __init__.py
│           └── video.py     # Video data model
└── playwright_player.ipynb  # Development notebook
```

## Dependencies

- Playwright: For browser automation
- Pydantic & SQLModel: For data validation and database ORM
- Schedule: For task scheduling
- Notebook: For development and testing

See `pyproject.toml` for complete dependency list.

## License

MIT