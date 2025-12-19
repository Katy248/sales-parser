from typing import Generator
from .page_fetch import fetch
from .utils import print_error
from bs4 import BeautifulSoup, Tag


class Offer:
    id: str
    name: str
    price: float
    priceCurrency: str
    subtitle: str

    def __init__(
        self, id: str, name: str, price: float, priceCurrency: str, subtitle: str
    ) -> None:
        self.id = id
        self.name = name
        self.price = price
        self.priceCurrency = priceCurrency
        self.subtitle = subtitle

    def __str__(self) -> str:
        return f"{self.name} - {self.price} {self.priceCurrency}"


def __get_id__(item: Tag) -> str:
    id = item.attrs.get("data-item-id")
    if id is None:
        raise Exception("Item has no 'data-item-id' attribute")
    return str(id)


def __get_name_element__(item: Tag):
    name_element = item.select_one("a[data-marker=item-title]")
    if name_element is None:
        raise Exception(
            "Item element has no child <a> with attribute [data-marker=item-title]"
        )
    return name_element


def __get_name__(item: Tag) -> str:
    name_element = __get_name_element__(item)
    return name_element.text


def __get_title__(item: Tag) -> str:
    name_element = __get_name_element__(item)
    title = name_element.attrs.get("title")
    if title is None:
        raise Exception("Item name element contains no [title] attribute")
    return str(title)


def __get_price__(item: Tag) -> float:
    price_element = item.select_one("meta[itemprop=price]")
    if price_element is None:
        raise Exception("Item has no price element")
    content = price_element.attrs.get("content")
    if content is None:
        raise Exception(
            "Item price element has no attribute [content], or it is just empty"
        )
    return float(str(content))


def __get_currency__(item: Tag) -> str:
    pc_element = item.select_one("meta[itemprop=priceCurrency]")
    if pc_element is None:
        raise Exception("Item has no price currency element")
    content = pc_element.attrs.get("content")
    if content is None:
        raise Exception(
            "Item price currency element has no attribute [content], or it is just empty"
        )
    return str(content)


def parse(url: str) -> Generator[Offer]:
    file = fetch(url)
    soup = BeautifulSoup(file.read_text(encoding="UTF-8"), "html.parser")
    for item in soup.select("div[data-marker=item]"):
        try:
            id = __get_id__(item)
            name = __get_name__(item)
            subtitle = __get_title__(item)
            price = __get_price__(item)
            priceCurrency = __get_currency__(item)

            offer = Offer(id, name, price, priceCurrency, subtitle)

            yield offer
        except Exception as e:
            print_error("Failed parse element: " + str(e) + " Skipping.")
            continue
