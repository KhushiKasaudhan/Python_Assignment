import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Part 1: Scraping product listing pages

base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"
search_query = "bags"
pages_to_scrape = 20
urls_to_scrape = 200

product_data = []
counter = 0

for page in range(1, pages_to_scrape + 1):
    params = {
        "k": search_query,
        "page": page
    }

    response = requests.get(base_url, params=params)
    soup = BeautifulSoup(response.content, "html.parser")

    product_cards = soup.find_all("div", {"data-component-type": "s-search-result"})

    for card in product_cards:
        if counter >= urls_to_scrape:
            break

        product_url = card.find("a", class_="a-link-normal")["href"]
        product_name = card.find("span", class_="a-size-medium").text.strip()
        product_price = card.find("span", class_="a-price-whole").text.strip()

        rating_element = card.find("span", class_="a-icon-alt")
        rating = rating_element.text.strip() if rating_element else "Not available"

        review_count_element = card.find("span", class_="a-size-base")
        review_count = review_count_element.text.strip() if review_count_element else "Not available"

        product_url = urljoin(base_url, product_url)  # Fix: Add proper scheme to the URL

        product_data.append({
            "Product URL": product_url,
            "Product Name": product_name,
            "Product Price": product_price,
            "Rating": rating,
            "Number of Reviews": review_count
        })

        counter += 1

        if counter >= urls_to_scrape:
            break

# Part 2: Scraping additional information from product URLs

for product in product_data:
    product_url = product["Product URL"]
    response = requests.get(product_url)
    soup = BeautifulSoup(response.content, "html.parser")

    product_description_element = soup.find("div", id="productDescription")
    product_description = product_description_element.text.strip() if product_description_element else "Not available"

    asin_element = soup.find("th", string="ASIN")
    asin = asin_element.find_next_sibling("td").text.strip() if asin_element else "Not available"

    manufacturer_element = soup.find("th", string="Manufacturer")
    manufacturer = manufacturer_element.find_next_sibling("td").text.strip() if manufacturer_element else "Not available"

    product.update({
        "Description": product_description,
        "ASIN": asin,
        "Product Description": product_description,
        "Manufacturer": manufacturer
    })

# Exporting data to CSV
csv_filename = "product_data.csv"

with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["Product URL", "Product Name", "Product Price", "Rating", "Number of Reviews",
                  "Description", "ASIN", "Product Description", "Manufacturer"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(product_data)

print("Data exported to", csv_filename)
