import sqlite3
import ssl
from urllib.request import urlopen
from urllib.parse import urljoin
from urllib.parse import urlparse
import urllib.error
from bs4 import BeautifulSoup

# Ignore SSL certificates
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Create a sqlite database
conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()

# Create tables
cur.executescript('''
CREATE TABLE IF NOT EXISTS Pages(
id INTEGER PRIMARY KEY,
url TEXT UNIQUE,
html TEXT,
error INTEGER,
old_rank REAL,
new_rank REAL
);
CREATE TABLE IF NOT EXISTS Links(
from_id INTEGER,
to_id INTEGER
);
CREATE TABLE IF NOT EXISTS Webs(
url TEXT UNIQUE
);
''')

# Check to see if the crawling process is in progress
cur.execute('SELECT id, url FROM Pages WHERE html IS NULL AND error IS NULL ORDER BY RANDOM() LIMIT 1')
row = cur.fetchone()
if row is not None:
    print('Restarting existing page crawl.')
else:
    starturl = input('Enter the web url to crawl: ')
    if starturl.endswith('/'):
        starturl = starturl[:-1]
    web = starturl
    if (starturl.endswith('.htm') or starturl.endswith('.html')):
        pos = starturl.rfind('/')
        web = starturl[:pos]

    if len(web) > 1:
        cur.execute('INSERT OR IGNORE INTO Webs (url) VALUES (?)', (web,))
        # Assign initial page rank
        cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES (?, NULL, 1.0)', (starturl,))
        conn.commit()

# Print the current Webs
cur.execute('SELECT url FROM Webs')
webs = list()
for row in cur:
    webs.append(str(row[0]))
print(webs)

many = 0
while True:
    if many < 1:
        sval = input('How many pages to crawl? ')
        if len(sval) < 1:
            break
        many = int(sval)
    many = many - 1

    cur.execute('SELECT id, url FROM Pages WHERE html IS NULL and error IS NULL ORDER BY RANDOM() LIMIT 1')
    try:
        row = cur.fetchone()
        fromid = row[0]
        url = row[1]
    except:
        print('No unretrieved HTML pages found.')
        many = 0
        break

    print(fromid, url, end=' ')

    # There should be no links from a page we are retrieving
    cur.execute('DELETE from Links WHERE from_id = ?', (fromid,))

    # Catch peculiar errors
    try:
        document = urlopen(url, context=ctx)
        html = document.read()
        if document.getcode() != 200:
            print("Error on page: ", document.getcode())
            cur.execute('UPDATE Pages SET error = ? WHERE url = ?', (document.getcode(), url))

        if 'text/html' != document.info().get_content_type():
            print("Ignore non-text/html page.")
            cur.execute('UPDATE Pages SET error = 0 WHERE url = ?', (url,))
            conn.commit()
            continue

        print('('+str(len(html))+')', end=' ')

        soup = BeautifulSoup(html, "html.parser")
    except KeyboardInterrupt:
        print('\nProgram interrupted by user.')
        break
    except:
        print('Unable to retrieve or parse page.')
        cur.execute('UPDATE Pages SET error = -1 WHERE url = ?', (url,))
        conn.commit()
        continue

    # Assign initial page rank
    cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES (?, NULL, 1.0)', (url,))
    cur.execute('UPDATE Pages SET html = ? WHERE url = ?', (memoryview(html), url))
    conn.commit()

    # Retrieve all the anchor tags
    tags = soup('a')
    count = 0
    for tag in tags:
        href = tag.get('href', None)
        if href is None:
            continue
        # Resolve relative references like href="/contact"
        up = urlparse(href)
        if len(up.scheme) < 1:
            href = urljoin(url, href)
        ipos = href.find('#')
        if ipos > 1:
            href = href[:ipos]
        if (href.endswith('.png') or href.endswith('.jpg') or href.endswith('.gif')):
            continue
        if (href.endswith('/')):
            href = href[:-1]
        if len(href) < 1:
            continue
        # Check if the URL is in any of the webs
        found = False
        for web in webs:
            if (href.startswith(web)):
                found = True
                break
        if not found:
            continue

        cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES (?, NULL, 1.0)', (href,))
        count = count + 1
        conn.commit()

        cur.execute('SELECT id FROM Pages WHERE url = ? LIMIT 1', (href,))
        try:
            row = cur.fetchone()
            toid = row[0]
        except:
            print('Could not retrieve id')
            continue
        cur.execute('INSERT OR IGNORE INTO Links (from_id, to_id) VALUES (?, ?)', (fromid, toid))

    print(count)

cur.close()
