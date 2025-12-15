from typing import Generator
from .page_fetch import fetch
from bs4 import BeautifulSoup

class Offer:
    name: str
    price: float
    priceCurrency: str
    subtitle: str

    def __init__(self, name: str, price: float, priceCurrency: str, subtitle: str) -> None:
        self.name = name
        self.price = price
        self.priceCurrency = priceCurrency
        self.subtitle = subtitle
        

    def __str__(self) -> str:
        return f"{self.name} - {self.price} {self.priceCurrency}"

def parse(url: str) -> Generator[Offer]:
    file = fetch(url)
    soup = BeautifulSoup(file.read_text(encoding="UTF-8"), "html.parser")
    for item in soup.select('div[data-marker=item]'):
        name = item.select_one('a[data-marker=item-title]').text
        subtitle = str(item.select_one('a[data-marker=item-title]').attrs.get('title'))
        price = float(str(item.select_one('meta[itemprop=price]').attrs.get('content')))
        priceCurrency = str(item.select_one('meta[itemprop=priceCurrency]').attrs.get('content', ""))

        offer = Offer(name, price, priceCurrency, subtitle)

        yield offer
