#! /usr/bin/python3
# seScraper.py - A web scraper which downloads all ebook files from www.standardebooks.org

import os, sys, requests, bs4


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

    # Collect ebook details and create eBook directory 
    bookDetails = bookSoup.find('meta', property='og:title').get('content')
    bookDir = os.path.splitext(os.path.basename(azw3Url))[0].title()
    os.makedirs(bookDir, exist_ok=True)

    # Download ebook files
    print('Downloading:  %s...' % bookDetails)
    for eBookFile in eBookFiles:
        fileName = os.path.join(bookDir, os.path.basename(eBookFile))
        if not os.path.exists(fileName):
            dlResponse = requests.get(eBookFile)
            dlResponse.raise_for_status()
            ebFile = open(fileName, 'wb')
            for chunk in dlResponse.iter_content(100000):
                ebFile.write(chunk)
            ebFile.close()
            print('Download complete: %s' % os.path.basename(eBookFile))

# Define base and start URLs
baseUrl = 'https://standardebooks.org'
startUrl = 'https://standardebooks.org/ebooks/'

# Create download directory
if len(sys.argv) < 2:
    print('Downloading eBooks to: %s' % os.path.join(os.getcwd(), 'standardEbooks'))
    os.makedirs('standardEbooks', exist_ok=True)
    os.chdir('standardEbooks')
elif len(sys.argv) == 2:
    newDir = os.path.join(sys.argv[1], 'standardEbooks')
    print('Downloading eBooks to: %s' % newDir)
    if os.path.exists(newDir):
        os.chdir(newDir)
    else:
        try:
            os.makedirs(newDir, exist_ok=True)
            os.chdir(newDir)
        except OSError:
            print('Cannot download to: %s. Please input a valid path.' % newDir)
            print('Usage: python seScraper.py <path> - set download directory')
            sys.exit()
else:
    print('Usage: python seScraper.py <path> - set download directory')
    sys.exit()

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
    bookList = cwSoup.find('ol')
    for li in bookList.find_all('li'):
        bookPages.append(baseUrl + li.find('a').get('href'))
    
    # Loop through book pages and download files
    for bookUrl in bookPages:
        bookDownload(bookUrl, baseUrl)

print('\nAll eBook files downloaded successfully!')



