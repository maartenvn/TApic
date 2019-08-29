import argparse
import requests
import base64
from urllib import request
from wand.image import Image
from typing import *


def to_rgb(url: str):
    """
    Convert an image to 16x16 and return a 2-dimensional array with [r, g, b]-list.
    """

    with request.urlopen(url) as file:
        with Image(file=file) as img:
            img.resize(48, 24)
            img.save(filename="test.png")
            # Get image byte blob.
            blob = img.make_blob(format="RGB")
            # Map with rgb-values for each pixel.
            # 2 dimensions represent the rows.
            pixels = []
            for y in range(0, img.height):
                row = []
                for x in range(0, img.width * 3, 3):
                    loc = x + (img.width * y * 3)
                    row.append([blob[loc], blob[loc + 1], blob[loc + 2]])
                pixels.append(row)
            return pixels


def to_cammie(string: str):
    """
    Send the color-string to cammie.
    """
    base = base64.b64encode(string.encode())
    requests.post(url="http://10.0.5.42:8000", headers={"X-Messages": base})
    print("Send!")


def parse(image: List[List[Tuple[int]]], compressed: bool = False) -> str:
    color_map = {
        (0, 0, 0): "§ZZ",
        (255, 0, 0): "§Zr",
        (127.5, 0, 0): "§ZR",
        (0, 255, 0): "§Zg",
        (0, 127.5, 0): "§ZG",
        (0, 0, 255): "§Zb",
        (0, 0, 127.5): "§ZB",
        (255, 255, 0): "§Zy",
        (127.5, 127.5, 0): "§ZY",
        (0, 255, 255): "§Zm",
        (0, 127.5, 127.5): "§ZM",
        (255, 0, 255): "§Zp",
        (127.5, 0, 127.5): "§ZP",
        (255, 255, 255): "§Zw",
        (127.5, 127.5, 127.5): "§ZW"
    }
    mapping_map = {
        0: {0: 0, 127.5: 0, 255: 0},
        1: {0: 0, 127.5: 127.5, 255: 0},
        2: {0: 0, 127.5: 127.5, 255: 255},
        3: {0: 0, 127.5: 127.5, 255: 255}
    }
    s = []
    for row in image:
        temp_s = ""
        for pixel in row:
            np = [0, 0, 0]
            max_value = 0
            for i, value in enumerate(pixel):
                if value > 255 / 2:
                    if value > 3 * 255 / 4:
                        np[i] = 3
                        max_value = max([max_value, 255])
                    else:
                        np[i] = 2
                        max_value = max([max_value, 127.5])
                else:
                    if value > 255 / 4:
                        np[i] = 1
                        max_value = max([max_value, 127.5])
                    else:
                        np[i] = 0
            for i in range(len(np)):
                pixel[i] = mapping_map[np[i]][max_value]
            temp_s += color_map[tuple(pixel)] + "0"
        s.append(temp_s)
    if compressed:
        s = compress(s)
    return "\n".join(s)


def compress(strings: List[str]) -> List[str]:
    """
    Compress the sent strings, we don't need to change colors when they stay the same.
    """
    from textwrap import wrap
    retval = []
    length = 4
    first_chars = 3
    for a in strings:
        b = wrap(a, length)
        i = 1
        checkstring = b[0]
        while i < len(b):
            tocheckstring = b[i]
            if tocheckstring[:first_chars] == checkstring[:first_chars]:
                b[i] = tocheckstring[first_chars]
            else:
                checkstring = tocheckstring
            i += 1
        retval.append("".join(b))
    return retval


parser = argparse.ArgumentParser(
    description="Send a JPG/PNG image to the cammie messageboard")
parser.add_argument("url", type=str, help="URL to a PNG/JPG image")
parser.add_argument("--compress", action="store_true")
args = parser.parse_args()
to_cammie(parse(to_rgb(args.url), args.compress))
