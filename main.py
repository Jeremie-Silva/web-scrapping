import requests
from bs4 import BeautifulSoup
import re
import csv

URL_MAIN = "https://books.toscrape.com"

class Book:
   def __init__(self, url_product):
      # Récupérer et perser le html de la page produit
      soup = BeautifulSoup(requests.get(url_product).content, "html.parser")
      self.product_page_url = url_product
      self.universal_product_code = soup.find("th", string="UPC").parent.td.contents[0]
      self.title = soup.title.contents[0]
      self.price_including_tax = soup.find("th", string=re.compile("incl")).parent.td.contents[0]
      self.price_excluding_tax = soup.find("th", string=re.compile("excl")).parent.td.contents[0]
      self.number_available = soup.find("th", string=re.compile("Availability")).parent.td.contents[0]
      self.catch_product_description(soup)
      self.category = soup.find("li", class_="active").previous_sibling.previous_sibling.a.contents[0]
      self.review_rating = soup.find("p", class_="star-rating").get("class")[1]
      self.image_url = soup.find("div", class_="item active").img.get("src")
      self.title_book = soup.find("h1").contents[0]

   def catch_product_description(self, soup):
      # On evite que le programme ne bloque si la description est vide
      x = soup.select("article.product_page > p")
      if x == []:
         self.product_description = x
      else: self.product_description = x[0].contents[0]

