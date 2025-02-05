A personal library based on Goodreads data.

## Installation

### Linux

- Have Docker installed
- Clone this repo locally or Download zip and extract
- Open a terminal and change directory to SoloScribe-main
- Run `docker compose up -d`
- Open a browser and go to http://127.0.0.1:8000/

### Windows

- The easiest way to get the app running on Windows is to install Docker Desktop 
https://www.docker.com/products/docker-desktop/
- If you have git locally installed you can use `git clone https://github.com/yamesyung/SoloScribe.git`
- If you don't have git locally installed you can download the source code from Code -> Download ZIP and extract to your preferred location
- Open Docker Desktop and make sure docker engine is running
- Go inside to extracted folder, open a console (Shift + Right click -> Open powershell) and type `docker compose up -d`
- Open a browser and go to http://127.0.0.1:8000/
- To close the app you can type `docker compose down` in the same powershell and close the docker engine from Docker Desktop


## Adding Data
There are 2 ways to add books in the library:
- Profile -> Import data -> Goodreads file (can use the Goodreads export library file and is compatible with library export csv file)
- Profile -> Add new book (which adds a singular book, based on its url, to one of the predefined shelves)

I also included in the demo directory an export file to get started with the project.

## Features

- List of books and authors from Goodreads library
- Quotes page, where you can search, filter and mark quotes as favorite
- Book gallery (an interactive page where you can search, filter, rate and review shelved books)
- Advanced stats for books and authors
- Map view (using the Setting/Places field in book data; Named Entity Recognition for Geo Political Entity based on author's description)
- Word cloud based on books' descriptions grouped in genres (books with language = "English")
- Timeline view for authors with known birth/death date
- Influence graph for authors (some authors may appear more than once, ex: Kafka and Franz Kafka)
- A recommendations page with curated books
- Export function: csv file
- Export function: zip file structured as Obsidian vault
- Theme support

Notes:
- Markdown syntax works when reviewing in book gallery, so you can add tags or create additional content
- Importing the csv file won't overwrite ratings and review in the database

## Themes

There are 3 "official" themes. 
The "custom" theme allows for more customization options.

If these are not enough you can create your own theme in the static/themes folder.
Django sends the html and htmx interactions with the backend and loads the static files from the selected theme folder.
This means you have a lot of freedom to style this library with your own static files and share them with the community.
Keep in mind that the app is still in development so html structure might change.

## Screenshots
![book-list](https://github.com/user-attachments/assets/b829cd82-7dc7-4986-838d-079b59d41eb6)

![book-detail](https://github.com/user-attachments/assets/784c2384-b81a-4bea-be0b-d5c751903b61)

![gallery](https://github.com/user-attachments/assets/5fffb53b-61f0-4607-b7d9-fe7f6cae00bb)

![quotes](https://github.com/user-attachments/assets/caff7064-48ad-44a6-9f04-f0246a268b84)

### Custom theme
![themes-1](https://github.com/user-attachments/assets/6f6a12f9-fb33-48a1-ae4f-54674eb82c8a)

![themes-2](https://github.com/user-attachments/assets/a960cc8c-ed3c-4585-8cea-c95009414a15)

![themes-3](https://github.com/user-attachments/assets/eb03d66f-c98f-466f-b1f1-23c1879e13e9)

![themes-4](https://github.com/user-attachments/assets/e056e3fa-1493-40b7-b3b0-b4c4ea661f0b)
