# Visto URL Extractor

A simple project to show a PoC of using Tornado with some DB (PostgreSQL in this case) to extract 
all URLs from a website and get a tag from an already scraped website.

## Steps to run to make it work:
1. Run the command 'git clone https://github.com/Ramakrisna/visto.git'
2. Run the command 'docker-compose up'
3. Run the script by typing 'python app.py'
4. Using Postman or the browser, send a GET request to 'localhost:8888/parse_url?url={website-to-scrape}' 
   to scrape the contents of that webpage
5. Using Postman or the browser, send a GET request to 
   'localhost:8888/parse_url?url={website-to-scrape}&uri={one-of-the-scraped-uri}'