import os
import requests
from bs4 import BeautifulSoup
import re

def scrape_movie(url, imdb_id):
    headers = {
        'accept': 
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.8',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }

    content = requests.get(url, headers=headers)
    soup = BeautifulSoup(content.text, "html.parser")

    def extract_el(label, parser=lambda x: x):
        try:
            el = soup.select_one(label)
            return '' if not el else parser(el.get_text())
        except Exception as e:
            return ''

    # Find revenue, assuming max between US/global gross
    revenue = None
    for elem in soup.find_all('h4', text=re.compile(r'Gross')):
        try:
            curr_revenue = re.sub('[ ,$]', '', elem.next_sibling)
            if curr_revenue and ((not revenue) or (curr_revenue > revenue)):
                revenue  = curr_revenue
        except Exception as e:
            pass

    if not revenue:
        return

    return {
        'imdb_id': imdb_id,
        'revenue': revenue,
    }

####################################################
# Scrape
####################################################

import sys
import os
import pandas as pd

if __name__ == '__main__':
    imdb_info = pd.DataFrame([], columns=['imdb_id', 'revenue'])

    if not (len(sys.argv) == 3):
        print('Need 2 arguments [input_file] [output_file]')
        sys.exit()

    OUTPUT_FILE = sys.argv[2]
    INPUT_FILE = sys.argv[1]

    try:
        imdb_ids = pd.read_csv(INPUT_FILE, names=['imdb_id'])

        for (i, row) in imdb_ids.iloc[1:].iterrows():
            imdb_id = row['imdb_id']

            try:
                IMDB_MOVIE_URL_FORMAT = 'https://www.imdb.com/title/%s'
                url = IMDB_MOVIE_URL_FORMAT % (imdb_id)
                print(url)

                movie = scrape_movie(url, imdb_id)
                if movie:
                    imdb_info = imdb_info.append(movie, ignore_index = True)
            except Exception as e:
                print('[%08d] %s' % (i, e))

    except KeyboardInterrupt:
        print('Interrupted')
        # Write to file
        imdb_info.to_csv(OUTPUT_FILE, index=False)

        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

    # Write to file
    imdb_info.to_csv(OUTPUT_FILE, index=False)
