book_ids = ['243705', '2920664', '22855867']
sent_ids = ','.join(book_ids)

print(sent_ids)

received_ids = sent_ids.split(',')

print(received_ids)

base_url = "https://www.goodreads.com/book/show/"

for book_id in received_ids:
    url = f"{base_url}{book_id}"

    print(url)
