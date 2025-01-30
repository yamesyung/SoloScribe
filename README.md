A personal library based on Goodreads data.

### New Changes
- Book quotes
- New custom theme
- Front end changes
- Added scraper into the main app (based on `https://github.com/havanagrawal/GoodreadsScraper`)

### Installation

- Have Docker installed
- Clone this repo locally or Download zip and extract
- Open a terminal and change directory to SoloScribe-main
- Run `docker compose up`
- Open a browser and go to `http://127.0.0.1:8000/`

### Data gathering
- From Goodreads site navigate to My Books -> Import/Export -> Export library
- It exports a csv file containing user's data about books, such as rating, review, read date
- Use it on the Import Data page of the app

### Test files

I've included in the demo directory an export file to get started with the project.

## Features

- List of books and authors from Goodreads library
- Advanced stats for books and authors
- Map view (using the Setting/Places field in book data; Named Entity Recognition for Geo Political Entity based on author's description)
- Word cloud based on books' descriptions grouped in genres (books with language = "English")
- Timeline view for authors with known birth/death date
- Influence graph for authors (some authors may appear more than once, ex: Kafka and Franz Kafka)
- Book gallery (an interactive page where you can search, filter, rate and review shelved books)
- A recommendations page with curated books
- Export function: csv file
- Export function: zip file structured as Obsidian vault
- Theme support

Notes:
- Markdown syntax works when reviewing in book gallery, so you can add tags or create additional content
- Importing the csv file won't overwrite ratings and review in the database

## Screenshots
![Screenshot from 2024-12-07 20-17-14](https://github.com/user-attachments/assets/4743597c-9e85-44cf-b567-fb028bcea4b6)


