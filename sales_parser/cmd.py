import argparse
import json


def main():
    cli_parser = argparse.ArgumentParser(
        prog="sales_parser",
        description="parses offers by given URL",
        epilog="Written by Katy248",
    )

    cli_parser.add_argument("url")
    cli_parser.add_argument(
        "-j", "--json", action="store_true", help="Prints output as JSON"
    )
    cli_parser.add_argument(
        "--pretty", action="store_true", help="Enable JSON pretty print"
    )
    cli_parser.add_argument(
        "--ensure-ascii",
        action="store_true",
        help="Ensures all symbols encoded as ASCII",
    )

    args = cli_parser.parse_args()

    from .parser import parse

    offers = list(parse(args.url))
    if args.json:
        from .utils import CustomJSONEncoder

        print(
            json.dumps(
                offers,
                indent=(4 if args.pretty else 0),
                cls=CustomJSONEncoder,
                ensure_ascii=args.ensure_ascii,
            )
        )
        return

    for o in offers:
        print(o)
