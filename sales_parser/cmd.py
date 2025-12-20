import argparse
from .utils import to_json


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
        "--diff",
        action="store_true",
        help="Prints difference between current and previous output, requires Redis",
    )
    cli_parser.add_argument(
        "--ensure-ascii",
        action="store_true",
        help="Ensures all symbols encoded as ASCII",
    )
    cli_parser.add_argument(
        "--redis-hostname",
        "--hostname",
        default="localhost",
        help="Specify redis hostname",
    )
    cli_parser.add_argument(
        "--redis-port",
        default=6379,
        help="Specify redis port",
    )
    cli_parser.add_argument(
        "--redis-password",
        help="Specify redis password",
    )

    args = cli_parser.parse_args()

    if args.diff:
        print_diff(args)
    else:
        print_parsed(args)


def print_diff(args: argparse.Namespace):
    from .parser import get_diff, RedisConfig

    conf = RedisConfig()
    conf.hostname = args.redis_hostname
    conf.port = args.redis_port
    conf.password = args.redis_password

    offers = get_diff(args.url, conf)
    if args.json:
        print(
            to_json(
                offers,
                indent=(4 if args.pretty else 0),
                ensure_ascii=args.ensure_ascii,
            )
        )

    else:
        for o in offers:
            print(o)


def print_parsed(args: argparse.Namespace):
    from .parser import parse

    offers = list(parse(args.url))
    if args.json:

        print(
            to_json(
                offers,
                indent=(4 if args.pretty else 0),
                ensure_ascii=args.ensure_ascii,
            )
        )
        return

    for o in offers:
        print(o)
