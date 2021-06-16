"""Script parsing a Nexus url and look for the latest docker image"""

import argparse
import dateutil
import requests
import sys
import pandas as pd
from bs4 import BeautifulSoup


def poll(url):
    """Poll the URL and convert html table to pandas dataframe"""
    requests.get(url)
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    table_data = soup.find('table')

    headers = []
    for i in table_data.find_all('th'):
        title = i.text.strip()
        headers.append(title)
    print(headers)
    df = pd.DataFrame(columns=headers)

    for j in table_data.find_all('tr')[2:]:
        row_data = j.find_all('td')
        row = [tr.get_text().strip() for tr in row_data]
        length = len(df)
        df.loc[length] = row

    # Convert Last Modified from string to datetime and sort by timestamp
    tzmapping = {'CEST': dateutil.tz.gettz('Europe/Berlin')}
    df['Last Modified'] = df['Last Modified'].apply(dateutil.parser.parse, tzinfos=tzmapping)
    df = df.sort_values(by=['Last Modified'], ascending=False)

    print(df.to_markdown())
    return df


def main():
    parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)
    default_url = "https://nexus.ssb.no/service/rest/repository/browse/gcp-bip-cr/v2/prod-bip/ssb/stratus/am-hello-world/tags/"
    parser.add_argument('--url', default=default_url, help="Nexus url to parse")
    args = parser.parse_args()

    if args.url:
        poll(args.url)


if __name__ == '__main__':
    main()
