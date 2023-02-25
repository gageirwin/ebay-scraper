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

def calculate_bounds(data, num_mad=2):
    median = np.median(data)
    mad = np.median(np.abs(data - median))
    lower_bound = median - num_mad * mad
    upper_bound = median + num_mad * mad
    return lower_bound, upper_bound

def discard_outliers(numbers, num_mad=2):
    min_value, max_value = calculate_bounds(numbers, num_mad)
    filtered_numbers = [n for n in numbers if n >= min_value and n <= max_value]
    return filtered_numbers

def compute_average(numbers):
    average = sum(numbers)/len(numbers)
    return average

def compute_top_percentage_average(numbers, percentage):
    sorted_numbers = sorted(numbers, reverse=True)
    count = int(ceil(len(numbers) * percentage))
    top_numbers = sorted_numbers[:count]
    top_average = sum(top_numbers) / count
    return top_average

def compute_bottom_percentage_average(numbers, percentage):
    sorted_numbers = sorted(numbers)
    count = int(ceil(len(numbers) * percentage))
    bottom_numbers = sorted_numbers[:count]
    bottom_average = sum(bottom_numbers) / count
    return bottom_average

# sold listing page url for the exact item you are determining the worth of
# make sure to set max per page to highest as it doesn't get multiple pages
url = 'https://www.ebay.com/sch/i.html?_nkw=Action+Replay+for+Game+Boy+Advance+GBA&_sacat=0&LH_TitleDesc=0&rt=nc&_odkw=Datel+Action+Replay+for+Game+Boy+Advance+GBA&_osacat=0&LH_PrefLoc=2&LH_Complete=1&LH_Sold=1'

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
item_block = soup.find('ul', class_='srp-results srp-list clearfix')
items = item_block.find_all('li')
prices = []
shipping = []
for item in items[1:]:
    section_notice = item.find('span', class_='section-notice__main')
    if section_notice and section_notice.text == 'Results matching fewer words':
        break
    price = item.find('span', class_='s-item__price')
    if price and 'to' not in price.text:
        prices.append(float(price.text[1:]))
        shipping_price = item.find('span', class_='s-item__shipping')
        if shipping_price:
            if shipping_price.text == 'Free shipping':
                shipping.append(0.00)
            else:
                if 'estimate' in shipping_price.text:
                    shipping.append(float(shipping_price.text[2:-18]))
                else:
                    shipping.append(float(shipping_price.text[2:-9]))

prices = discard_outliers(prices)
top_percent = 0.10
bottom_percent = 0.10
average = compute_average(prices)
top_average = compute_top_percentage_average(prices, top_percent)
bottom_average = compute_bottom_percentage_average(prices, bottom_percent)
free_shipping_percent = percent_at_value(shipping, 0.00)
print(f"The average price is: ${average:.2f}")
print(f"The top {int(top_percent*100)}% sold for an average of: ${top_average:.2f}")
print(f"The bottom {int(bottom_percent*100)}% sold for an average of: ${bottom_average:.2f}")
print(f"{int(free_shipping_percent*100)}% offer free shipping.")