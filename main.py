"""Script to scrap https://books.toscrape.com."""
import re
import csv
import requests
import os
from bs4 import BeautifulSoup


URL_MAIN: str = "https://books.toscrape.com/"
PATH_URL_CATEGORY: str = "https://books.toscrape.com/catalogue/"
URL_META_CATEGORY_BOOK: str = "https://books.toscrape.com/catalogue/category/books_1/index.html"
PATH_URL_META_CATEGORY: str = "https://books.toscrape.com/catalogue/category/"
FIELDNAMES = ['product_page_url', 'universal_product_code', 'title', 'price_including_tax',
    'price_excluding_tax', 'number_available', 'product_description', 'category',
    'review_rating', 'image_url']


class Book:
    """Cette class permet de scraper le contenu d'une page livre,
    et inscremete le self de chaque instance avec les valeurs scrapées.
    """
    def __init__(self, url_product: str, FIELDNAMES: list, count: int):
    # Initialisation de l'instance à partir de l'url du livre passé en parametre
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
        self.image_url = soup.find("div", class_="item active").img.get("src").replace("../..", URL_MAIN)
        self.title_book = soup.find("h1").contents[0]
        # Si count égal 0 alors c'est le premier livre de la catégorie
        if count == 0 : self.initialisation_directory_and_file(FIELDNAMES)
        self.export_csv_file(FIELDNAMES)
        self.export_images_files()

    def catch_product_description(self, soup: BeautifulSoup) -> None:
    # On evite que le programme ne bloque si la description est vide
        x = soup.select("article.product_page > p")
        if x == []:
            self.product_description = x
            return None
        self.product_description = x[0].contents[0]
        return None

    def initialisation_directory_and_file(self, FIELDNAMES: list) -> None:
        # On vérifie si le dossier général existe et on le crée si ce n'est pas le cas
        if not os.path.exists("Data_books_to_scrape"):
            os.mkdir("Data_books_to_scrape")
        # On vérifie si le dossier des catégories existe et on le crée si ce n'est pas le cas
        if not os.path.exists(f"Data_books_to_scrape/{self.category}"):
            os.mkdir(f"Data_books_to_scrape/{self.category}")
        # On vérifie si le dossier des images existe et on le crée si ce n'est pas le cas
        if not os.path.exists(f"Data_books_to_scrape/{self.category}/images_{self.category}"):
            os.mkdir(f"Data_books_to_scrape/{self.category}/images_{self.category}")
        # On vérifie si le fichier existe et on choisit le mode d'ouverture en fonction
        if os.path.exists(f"Data_books_to_scrape/{self.category}/{self.category}.csv"):
            csv_mode = "w+"
        else: csv_mode = "x+"
        # On crée le fichier csv ou on le reinitialise et on ajoute les en-têtes
        with open(f"Data_books_to_scrape/{self.category}/{self.category}.csv", csv_mode, newline="") as csv_file:
            csv.DictWriter(csv_file, fieldnames=FIELDNAMES).writeheader()

        return None

    def export_csv_file(self, FIELDNAMES: list) -> None:
        # On exporte les données dans un fichier csv portant le nom de la catégorie du livre
        with open(f"Data_books_to_scrape/{self.category}/{self.category}.csv", "a", newline="") as csv_file:
            csv.DictWriter(csv_file, fieldnames=FIELDNAMES).writerow({
                'product_page_url': self.product_page_url,
                'universal_product_code': self.universal_product_code,
                'title': self.title_book,
                'price_including_tax': self.price_including_tax,
                'price_excluding_tax': self.price_excluding_tax,
                'number_available': self.number_available,
                'product_description': self.product_description,
                'category': self.category,
                'review_rating': self.review_rating,
                'image_url': self.image_url,
            })
        return None

    def export_images_files(self) -> None:
        # On exporte les images dans un dossier portant le nom de la catégorie du livre
        image = requests.get(self.image_url)
        if "/" in self.title_book:
            title = self.title_book.replace("/", "-")
        else: title = self.title_book
        with open(f"Data_books_to_scrape/{self.category}/images_{self.category}/{title}.jpg", "wb") as image_file:
            image_file.write(image.content)
        return None


class Category_book:
    """Cette classe permet de scraper les urls des livres sur les pages catégorie,
    en tenant compte de l'éventuelle pagination,
    et incrémente une liste avec les valeurs.
    """
    def __init__(self, url_category: str):
    # Initialisation de l'instance à partir de l'url de la catégorie passé en parametre
        soup = BeautifulSoup(requests.get(url_category).content, "html.parser")
        # Liste éventuellement incrementée par toutes les URLs de la pagination
        self.urls_category = [url_category]
        self.list_urls_books: list[str] = []
        self.catch_urls_books(soup)
        self.heading = soup.find("h1").contents[0]

    def catch_urls_books(self, soup: BeautifulSoup) -> None:
    # Permet de scraper une page de catégorie et incrémente la liste des urls de cette catégorie
        # Récupere tous les liens placés sur des balises <h3> dans le corps de la page
        for i in range(0, len(soup.select("ol.row h3 a"))):
            x = soup.select("ol.row h3 a")[i].get("href")
            self.list_urls_books.append(x.replace("../../../", PATH_URL_CATEGORY))
        # Verifie si il y a un bouton de pagination
        if soup.find("li", class_="next"):
            self.pagination_category(soup)
        return None

    def pagination_category(self, soup: BeautifulSoup) -> None:
    # Recupere l'URL de la prochaine page de pagination et la rajoute dans la liste des URLs de catégorie
        url_category_split = self.urls_category[-1].split("/")
        url_category_split[-1] = soup.select("li.next a")[0].get("href")
        self.urls_category.append("/".join(url_category_split))
        # Relance la fonction d'extraction des URLs avec la nouvelle page de pagination
        soup = BeautifulSoup(requests.get(
            self.urls_category[-1]).content, "html.parser")
        self.catch_urls_books(soup)
        return None



class BooksToScrape_category:
    """Cette class permet de scraper les urls des catégories de livres du site BookToScrape,
    et incrémente une liste avec les valeurs.
    """
    def __init__(self):
    # Initialisation de l'instance à partir de l'url META de la catégorie
        self.url_parent = URL_META_CATEGORY_BOOK
        soup = BeautifulSoup(requests.get(
            self.url_parent).content, "html.parser")
        self.list_all_category_urls: list[str] = []
        self.catch_urls_category(soup)
        print(f"Total : {len(self.list_all_category_urls)} category")

    def catch_urls_category(self, soup: BeautifulSoup) -> None:
    # Recuperer l'URL de chaque categories et incrementer une liste avec les valeurs
        for i in range(0, len(soup.select("div.side_categories > ul.nav > li > ul > li > a"))):
            x = soup.select("div.side_categories > ul.nav > li > ul > li > a")[i].get("href")
            self.list_all_category_urls.append(x.replace("../", PATH_URL_META_CATEGORY))
        return None



# --------------------------PROGRAMME--------------------------

# Récupere la liste des catégories de livres
super_category_book = BooksToScrape_category()
print()

# Premiere boucle qui parcours la liste des urls des catégories
for i in range(0, len(super_category_book.list_all_category_urls)):
    # Créer une instance de chaque catégorie en lui passant l'url de la catégorie en parametre
    x = Category_book(super_category_book.list_all_category_urls[i])
    print(f"OK -- {x.heading} : {len(x.list_urls_books)} books")

    # Deuxieme boucle qui cible la catégorie en cours et qui parcours sa liste d'url de livres
    for u in range(0, len(x.list_urls_books)):
        # Chaque page de livre est scrapée
        y = Book(x.list_urls_books[u], FIELDNAMES, u)
        print(f"{u+1} >> {y.title_book}")

    print()

print("END")
