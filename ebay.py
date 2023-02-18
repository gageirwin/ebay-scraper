import requests
from bs4 import BeautifulSoup
from math import ceil
import numpy as np

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

url = 'https://www.ebay.com/sch/i.html?_nkw=intel+i7+8700k+cpu&_sacat=0&LH_TitleDesc=0&LH_PrefLoc=2&LH_Complete=1&_ipg=240&LH_Sold=1&LH_ItemCondition=3000&rt=nc&Processor%2520Type=Core%2520i7%25208th%2520Gen%252E&_dcat=164'

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
item_block = soup.find('ul', class_='srp-results srp-list clearfix')
items = item_block.find_all('li')
prices = []
for item in items[1:]:
    price = item.find('span', class_='s-item__price')
    if price and 'to' not in price.text:
        prices.append(float(price.text[1:]))

prices = discard_outliers(prices)
percent = 0.10
average = compute_average(prices)
top_average = compute_top_percentage_average(prices, percent)
bottom_average = compute_bottom_percentage_average(prices, percent)
print(f"The average price is: ${average:.2f}")
print(f"The top {percent*100}% sold for an average of: ${top_average:.2f}")
print(f"The bottom {percent*100}% sold for an average of: ${bottom_average:.2f}")