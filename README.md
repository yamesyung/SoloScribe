A personal library based on Goodreads data.

### New Changes
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

Notes:
- Markdown syntax works when reviewing in book gallery, so you can add tags or create additional content
- Importing the csv file won't overwrite ratings and review in the database
- The exported csv contains less data than the original Goodreads export file (won't contain Binding, Bookshelves or user shelves, Private Notes as they are not imported in the db in the first place)

## Screenshots


![book_gallery](https://github.com/yamesyung/SoloScribe/assets/96660815/4803a14e-fefc-4a48-b053-4e446329eb8c)
![detail_view](https://github.com/yamesyung/SoloScribe/assets/96660815/4f953e49-9642-4af2-bfc7-110398c40d14)
![recs](https://github.com/yamesyung/SoloScribe/assets/96660815/0ab3846c-e53f-4fcc-bab7-2d62476ac353)
![map view](https://github.com/yamesyung/SoloScribe/assets/96660815/404e4cd8-6bc0-4404-870b-62c9d6481ddc)
![wordcloud](https://github.com/yamesyung/SoloScribe/assets/96660815/3abd9965-c6b1-45e0-96ce-e829e2719a9b)
![award stats](https://github.com/yamesyung/SoloScribe/assets/96660815/45e0ea3c-a5d9-40dd-b684-b5a995a66745)
![graphs](https://github.com/yamesyung/SoloScribe/assets/96660815/22317adc-39b7-498f-81a7-f46d09ab741c)
![more graphs](https://github.com/yamesyung/SoloScribe/assets/96660815/d4ee9457-cdd4-4b2e-9b64-7dffb1527084)
