import argparse
import requests
import base64
from urllib import request
from wand.image import Image
from typing import *

"""
Convert an image to 16x16 and return a 2-dimensional array with [r, g, b]-list.
"""
def to_rgb(url: str):

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

"""
Send the color-string to cammie.
"""
def to_cammie(string: str):
    base = base64.b64encode(string.encode())
    requests.post(url="http://10.0.5.42:8000", headers={"X-Messages": base})

    print("Send!")


def parse(image: List[List[Tuple[int]]]) -> str:
    color_map = {
        (0, 0, 0): "§ZZ",
        (255, 0, 0): "§Rr",
        (127.5, 0, 0): "§RR",
        (0, 255, 0): "§Gg",
        (0, 127.5, 0): "§GG",
        (0, 0, 255): "§Bb",
        (0, 0, 127.5): "§BB",
        (255, 255, 0): "§Yy",
        (127.5, 127.5, 0): "§YY",
        (0, 255, 255): "§Mm",
        (0, 127.5, 127.5): "§MM",
        (255, 0, 255): "§Pp",
        (127.5, 0, 127.5): "§PP",
        (255, 255, 255): "§Ww",
        (127.5, 127.5, 127.5): "§WW"
    }
    mapping_map = {
        0: {0: 0, 127.5: 0, 255: 0},
        1: {0: 0, 127.5: 127.5, 255: 0},
        2: {0: 0, 127.5: 127.5, 255: 255},
        3: {0: 0, 127.5: 127.5, 255: 255}
    }
    s = ""
    for row in image:
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
            for i in np:
                pixel[i] = mapping_map[np[1]][max_value]
            s += color_map[tuple(pixel)] + "0"
        s += '\n'
    return s.rstrip('\n')

parser = argparse.ArgumentParser(description="Send a JPG/PNG image to the cammie messageboard")
parser.add_argument("url", type=str, help="URL to a PNG/JPG image")
args = parser.parse_args()

to_cammie(parse(to_rgb(args.url)))
