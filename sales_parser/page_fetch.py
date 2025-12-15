import os
import pathlib
import datetime
from .utils import print_error
from .utils import print_log
import urllib.request as req

CACHE_DIR = os.getenv("HOME", "/root") + "/./cache/sp"


def __ensure_cache_dir_created():
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
    except Exception as e:
        print_error(f"failed create cache dir ({CACHE_DIR}), error: {e}")


def __url_to_filename(url: str) -> pathlib.Path:
    return pathlib.Path(CACHE_DIR) / url.replace(":", "_").replace("/", "_")


def fetch(url: str) -> pathlib.Path:
    __ensure_cache_dir_created()

    file = __url_to_filename(url)

    print_log(str(file))
    if file.exists():
        print_log("file exists")
    else:
        return __fetch(url, file)

    file_last_modified = datetime.datetime.fromtimestamp(file.lstat().st_mtime)
    print_log(f"last modified: {file_last_modified}")

    if datetime.datetime.now() - file_last_modified < __get_cache_expiration_time():
        print_log("Cached file")
        return file.absolute()
    return __fetch(url, file)


def __fetch(url: str, file: pathlib.Path) -> pathlib.Path:
    request = req.Request(url)

    with open("AVITO_COOKIE", "r", encoding="UTF-8") as cookie_file:
        cookie = cookie_file.readline().replace("b'", "").replace("\n", "")
        request.add_header("Cookie", str(cookie))

    response = req.urlopen(request)
    data = response.read().decode("UTF-8")

    with open(file, "w") as output:
        output.write(data)

    return file.absolute()


def __get_cache_expiration_time():
    return datetime.timedelta(hours=1)
