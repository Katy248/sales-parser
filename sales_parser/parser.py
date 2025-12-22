from typing import Generator
import json
from .page_fetch import fetch
from .utils import print_error, to_json
from bs4 import BeautifulSoup, Tag
import redis


class Offer:
    id: int
    name: str
    price: float
    priceCurrency: str
    subtitle: str
    url: str

    def __init__(
        self,
        id: int,
        name: str,
        price: float,
        priceCurrency: str,
        subtitle: str,
        url: str,
    ) -> None:
        self.id = id
        self.name = name
        self.price = price
        self.priceCurrency = priceCurrency
        self.subtitle = subtitle
        self.url = url

    def __str__(self) -> str:
        return f"{self.name} - {self.price} {self.priceCurrency}"


def __get_id__(item: Tag) -> int:
    id = item.attrs.get("data-item-id")
    if id is None:
        raise Exception("Item has no 'data-item-id' attribute")
    return int(str(id))


def __get_name_element__(item: Tag):
    name_element = item.select_one("a[data-marker=item-title]")
    if name_element is None:
        raise Exception(
            "Item element has no child <a> with attribute [data-marker=item-title]"
        )
    return name_element


def __get_url__(item: Tag) -> str:
    name_element = __get_name_element__(item)
    href = name_element.attrs.get("href")
    if href is None:
        raise Exception("There is no href attribute provided in item")
    return str(href)


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
            offer_url = __get_url__(item)

            offer = Offer(id, name, price, priceCurrency, subtitle, offer_url)

            yield offer
        except Exception as e:
            print_error("Failed parse element: " + str(e) + " Skipping.")
            continue


class RedisConfig:
    hostname = "localhost"
    port = 6379
    password: str | None = None


def __parse_offers_from_json(json_str: str) -> list[Offer]:
    offers: list[Offer] = []
    old_data = json.loads(json_str)
    for item in old_data:
        offers.append(
            Offer(
                int(item.get("id")),
                item.get("name"),
                float(item.get("price")),
                item.get("priceCurrency"),
                item.get("subtitle"),
                item.get("url"),
            )
        )
    return offers


def get_diff(url: str, rConf: RedisConfig):

    r = redis.Redis(
        host=rConf.hostname,
        password=rConf.password,
        port=rConf.port,
        decode_responses=True,
    )
    old_data = __parse_offers_from_json(str(r.get(url)))

    new_data = list(parse(url))
    diffs: list[Offer] = []
    for item in new_data:
        contains = (True for i in old_data if i.id == item.id)
        if contains:
            continue

        diffs.append(item)

    r.set(url, to_json(new_data))
    return diffs
