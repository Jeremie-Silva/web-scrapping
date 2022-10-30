import re
import csv
import requests
from bs4 import BeautifulSoup


URL_MAIN = "https://books.toscrape.com"


class Book:
    def __init__(self,
                 url_product: str):
        # Récupérer et perser le html de la page produit
        soup = BeautifulSoup(requests.get(url_product).content, "html.parser")
        self.product_page_url = url_product
        self.universal_product_code = soup.find(
            "th", string="UPC").parent.td.contents[0]
        self.title = soup.title.contents[0]
        self.price_including_tax = soup.find(
            "th", string=re.compile("incl")).parent.td.contents[0]
        self.price_excluding_tax = soup.find(
            "th", string=re.compile("excl")).parent.td.contents[0]
        self.number_available = soup.find(
            "th", string=re.compile("Availability")).parent.td.contents[0]
        self.catch_product_description(soup)
        self.category = soup.find(
            "li", class_="active").previous_sibling.previous_sibling.a.contents[0]
        self.review_rating = soup.find(
            "p", class_="star-rating").get("class")[1]
        self.image_url = soup.find("div", class_="item active").img.get("src")
        self.title_book = soup.find("h1").contents[0]

    def catch_product_description(self, soup: str) -> str:
        # On evite que le programme ne bloque si la description est vide
        x = soup.select("article.product_page > p")
        if x == []:
            self.product_description = x
        else:
            self.product_description = x[0].contents[0]


class Category_book:
    def __init__(self, url_category):
        soup = BeautifulSoup(requests.get(url_category).content, "html.parser")
        # Liste contenant toutes les URLs de la pagination
        self.urls_category = [url_category]
        self.list_urls_livres = []
        self.catch_urls_books(soup)
        self.heading = soup.find("h1").contents[0]

    def catch_urls_books(self, soup):
        # Recupere tous les liens placés sur des <h3> dans le corps de la page
        for i in range(0, len(soup.select("ol.row h3 a"))):
            x = soup.select("ol.row h3 a")[i].get("href").split("/")
            del x[0:2]
            x[0] = "https://books.toscrape.com/catalogue"
            self.list_urls_livres.append("/".join(x))
        # Verifie si il y a un bouton de pagination
        if soup.find("li", class_="next"):
            self.pagination_category(soup)

    def pagination_category(self, soup):
        # Recupere l'URL de la prochaine page de pagination et la rajoute dans la liste des URLs
        url_category_split = self.urls_category[-1].split("/")
        url_category_split[-1] = soup.select("li.next a")[0].get("href")
        self.urls_category.append("/".join(url_category_split))
        # Relance la fonction d'extraction des URLs avec la nouvelle page de pagination
        soup = BeautifulSoup(requests.get(
            self.urls_category[-1]).content, "html.parser")
        self.catch_urls_books(soup)


class BooksToScrape_category:
    def __init__(self):
        self.url_parent = "https://books.toscrape.com/catalogue/category/books_1/index.html"
        soup = BeautifulSoup(requests.get(
            self.url_parent).content, "html.parser")
        self.list_all_category_urls = []
        self.catch_urls_category(soup)
        print(f"Total : {len(self.list_all_category_urls)} category")

    def catch_urls_category(self, soup):
        # Recuperer l'URL de chaque categories et incrementer la liste
        for i in range(0, len(soup.select("div.side_categories > ul.nav > li > ul > li > a"))):
            x = soup.select("div.side_categories > ul.nav > li > ul > li > a")[
                i].get("href").split("/")
            x[0] = "https://books.toscrape.com/catalogue/category"
            self.list_all_category_urls.append("/".join(x))


# --------------------------PROGRAMME--------------------------


super_category_book = BooksToScrape_category()
print()
for i in range(0, len(super_category_book.list_all_category_urls)):
    x = Category_book(super_category_book.list_all_category_urls[i])
    print(f"OK -- {x.heading} : {len(x.list_urls_livres)} books")
    for u in range(0, len(x.list_urls_livres)):
        y = Book(x.list_urls_livres[u])
        print(f"{u+1} >> {y.title_book}")
    print()

# with open("test.csv", "w", newline="\n") as csvfile:
#    csv.writer(csvfile).writerow("ergrdgbrfsefsef, fefe, fesfs")


"""
   VSC : retour à la ligne '\n' + virgules pour changer de cellule
   https://www.scrapingbee.com/blog/download-image-python/
   Paramétrer les class pour qu'elles soient parentes ?

"""
