import requests
from bs4 import BeautifulSoup
from math import ceil
import numpy as np

def percent_at_value(data, value):
    count = 0
    for item in data:
        if item == value:
            count += 1
    return count/len(data)

def discard_outlier_tuples(tuples_list, num_mad=2):
    numbers = [t[0] for t in tuples_list]
    filtered_numbers = discard_outliers(numbers, num_mad)
    filtered_tuples = [t for t in tuples_list if t[0] in filtered_numbers]
    return filtered_tuples

def discard_outliers(numbers, num_mad=2):
    median = np.median(numbers)
    mad = np.median(np.abs(numbers - median))
    min_value = median - num_mad * mad
    max_value = median + num_mad * mad
    filtered_numbers = [n for n in numbers if n >= min_value and n <= max_value]
    return filtered_numbers

def compute_percentage_average(numbers, percentage, bottom=None):
    if bottom == None:
        sorted_numbers = sorted(numbers, reverse=True)
    else:
        sorted_numbers = sorted(numbers)
    count = int(ceil(len(numbers) * percentage))
    percent_numbers = sorted_numbers[:count]
    percent_average = sum(percent_numbers) / count
    return percent_average, count

def scrape(session, url):
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
    }
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    items_block = soup.find('ul', class_='srp-results srp-grid clearfix')
    if items_block == None:
        items_block = soup.find('ul', class_='srp-results srp-list clearfix')
    items = items_block.find_all('li')
    found = []
    for item in items[1:]:
        section_notice = item.find('span', class_='section-notice__main')
        if section_notice and section_notice.text == 'Results matching fewer words':
            break
        price = item.find('span', class_='s-item__price')
        if price and 'to' not in price.text:
            ship_price = item.find('span', class_='s-item__shipping')
            if ship_price == None:
                found.append((float(price.text[1:].replace(',','')),0))
            elif ship_price.text == 'Free shipping':
                found.append((float(price.text[1:].replace(',','')),0))
            else:
                found.append((float(price.text[1:].replace(',','')),1))

    found = discard_outlier_tuples(found)
    return found

def average_listed_sold(session, url, top_percent=0.1, bottom_percent=0.1):
    search_url = url + '&_ipg=240'
    sold_url = f'{search_url}&rt=nc&LH_Sold=1&LH_Complete=1'

    found = scrape(session, search_url)
    prices, shipping = [t[0] for t in found], [t[1] for t in found]
    avg_listed = 0
    if len(prices) != 0:
        avg_listed = sum(prices)/len(prices)

    found = scrape(session, sold_url)
    prices, shipping = [t[0] for t in found], [t[1] for t in found]
    avg_sold = 0
    if len(prices) != 0:
        avg_sold = sum(prices)/len(prices)

    return avg_listed, avg_sold

def update_drive(session, full_refresh=False):
    import gspread
    sa = gspread.service_account(filename="service_account.json")
    sh = sa.open("ebay")
    wks = sh.worksheet("Items")
    urls = wks.get('A:E')
    new = []
    for row in urls[1:]:
        if len(row) != 3 or full_refresh:
            print(f"Processing: {row[0]}")
            name = row[0].replace(" ","+")
            url = f'https://www.ebay.com/sch/i.html?_nkw={name}&_sacat=0'
            row[1] = url
            avg_listed, avg_sold = average_listed_sold(session, url)
            if len(row) == 1:
                row.append(str(avg_listed))
            row.append(str(avg_sold))                
        new.append(row)
    wks.update(f"A2:E{wks.row_count}", new)    

def main():
    session = requests.Session()

    # update_drive(session)

    url = ''
    avg_listed, avg_sold = average_listed_sold(session, url)
    print(avg_listed, avg_sold)
    print(f"Listed Average:${avg_listed:.2f} | Sold Average: ${avg_sold:.2f}")

if __name__ == '__main__':
    main()