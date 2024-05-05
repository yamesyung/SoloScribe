A personal library based on Goodreads' data.

### Introduction

This is a Django project which runs locally. It uses data scraped from Goodreads and the Goodreads export file to create a personal library.

### Installation

- Have Docker installed
- Clone this repo locally
- Open a terminal and change directory to SoloScribe-main
- Run `docker-compose up`
- Open a browser and go to `http://127.0.0.1:8000/`

### Data gathering

The application uses data scraped from Goodreads using this repo: `https://github.com/havanagrawal/GoodreadsScraper`

So we'll need to run a few additional steps (more info in linked repo):

- Clone GoodreadsScraper locally
- Create a virtual environment inside the repo
- Activate the environment and install the requirements file
- Make sure your Goodreads profile is set to public
- Run `python3 crawl.py my-books --shelf="all" --user_id="<your Goodreads user ID>"`
- It outputs 2 .jl files, containing books and authors data

The 2nd source of data is from Goodreads.

- Navigate to My Books -> Import/Export -> Export library
- It exports a csv file containing user's data about books, such as rating, review, read date

### Test files

I've included in the demo directory a set of files to get started with the project.

## Features

- List of books and authors from Goodreads' library
- Advanced stats for books and authors
- Map view (using the Setting/Places field in book data; Named Entity Recognition for Geo Political Entity based on author's description)
- Word cloud based on books' descriptions grouped in genres (books with language = "English")
- Timeline view for authors with known birth/death date
- Influence graph for authors (some authors may appear more than once, ex: Kafka and Franz Kafka)
- Download book covers locally and use them in book gallery (an interactive page where you can search, filter, rate and review shelved books)
- A recommendations page with curated books
- Export function: csv file
- Export function: zip file structured as Obsidian vault

Notes:
- Markdown syntax works when reviewing in book gallery, so you can add tags or create additional content
- If book covers are stored locally, it will add them in the zip file
