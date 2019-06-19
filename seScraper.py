#! python3
# seScraper.py - Web scraper that downloads all ebook formats and covers from Standard eBooks

import os, requests, bs4


def bookDownload(bookUrl, siteUrl):
    # Download ebook page
    bookResponse = requests.get(bookUrl)
    bookResponse.raise_for_status()
    bookSoup = bs4.BeautifulSoup(bookResponse.text, 'html.parser')

    # Collect URLs of ebook files
    azw3Elem = bookSoup.select('.amazon')
    kepubElem = bookSoup.select('.kobo')
    epubElem = bookSoup.select('.epub')

    azw3Url = siteUrl + azw3Elem[0].get('href')
    kepubUrl = siteUrl + kepubElem[0].get('href')
    epubUrl = siteUrl + epubElem[0].get('href')
    epub3Url = siteUrl + epubElem[1].get('href')

    coverElem = bookSoup.find('a', string='Kindle cover thumbnail')
    coverUrl = siteUrl + coverElem.get('href')

    eBookFiles = [azw3Url, kepubUrl, epubUrl, epub3Url, coverUrl]

    # Collect ebook details. Create eBook directory or return if it exists already
    bookDetails = bookSoup.find('meta', property='og:title').get('content')
    bookDir = os.path.splitext(os.path.basename(azw3Url))[0].title()
    if os.path.exists(bookDir):
        print('%s has already been downloaded. Checking next book...' % bookDetails)
        return
    else:
        os.makedirs(bookDir, exist_ok=True)

    # Download ebook files
    print('Downloading eBook files for %s...' % bookDetails)
    for eBookFile in eBookFiles:
        dlResponse = requests.get(eBookFile)
        dlResponse.raise_for_status()
        ebFile = open(os.path.join(bookDir, os.path.basename(eBookFile)), 'wb')
        for chunk in dlResponse.iter_content(100000):
            ebFile.write(chunk)
        ebFile.close()
        print('Download of %s complete' % os.path.basename(eBookFile))

# Define base and start URLs
baseUrl = 'https://standardebooks.org'
startUrl = 'https://standardebooks.org/ebooks/'

# Create working directory
os.makedirs('standardEbooks', exist_ok=True)
os.chdir('standardEbooks')

# Download first page and collect nav page URLs
navResponse = requests.get(startUrl)
navResponse.raise_for_status()

soup = bs4.BeautifulSoup(navResponse.text, 'html.parser')

navSelect = soup.select('.ebooks nav li a')[1:]
navPages = [startUrl]
for i in range(len(navSelect)):
    navPages.append(baseUrl + navSelect[i].get('href'))

# Loop through nav pages
for navPage in navPages:
    cwResponse = requests.get(navPage)
    cwResponse.raise_for_status()

    cwSoup = bs4.BeautifulSoup(cwResponse.text, 'html.parser')

    # Collect book page URLs
    bookPages = []
    bookSelect = cwSoup.select('.ebooks ol li p a')
    for k in range(len(bookSelect)):
        if k % 2 == 0:
            bookPages.append(baseUrl + bookSelect[k].get('href'))
    
    # Loop through book pages and download files
    for bookUrl in bookPages:
        bookDownload(bookUrl, baseUrl)

print('\nAll eBook files downloaded successfully!')



