import argparse
from requests import get, post
import base64
from typing import *
from PIL import Image
from io import BytesIO

LUT = [
    (255, 255, 255, "§Zw"),
    (170, 170, 170, "§ZW"),
    (85, 85, 85, "$Zz"),
    (0, 0, 0, "§ZZ"),
    (255, 255, 85, "§Zy"),
    (0, 170, 0, "§ZG"),
    (85, 255, 85, "$Zg"),
    (255, 85, 85, "§Zr"),
    (170, 0, 0, "§ZR"),
    (170, 85, 0, "§ZY"),
    (170, 0, 170, "§ZP"),
    (255, 85, 255, "§Zp"),
    (85, 255, 255, "§Zm"),
    (0, 170, 170, "§ZM"),
    (0, 0, 170, "§ZB"),
    (85, 85, 255, "§Zb"),
]


def find_nearest_color(color: tuple) -> tuple:
    scores = [i for i in map(lambda x: sum([(x[i] - color[i]) ** 2 for i in [0, 1, 2]]), LUT)]
    return LUT[scores.index(min(scores))]


def to_rgb(url: str):
    """
    Convert an image to 16x16 and return a 2-dimensional array with [r, g, b]-list.
    """

    response = get(url)
    img = Image.open(BytesIO(response.content))
    img = img.resize((48, 24), Image.ANTIALIAS)
    img.save("test.png")
    return img


def to_cammie(string: str):
    """
    Send the color-string to cammie.
    """
    base = base64.b64encode(string.encode())
    post(url="http://10.0.5.42:8000", headers={"X-Messages": base})
    print("Sent!")


def add_error(image, pos, error, percent):
    if 0 <= pos[0] < image.width and 0 <= pos[1] < image.height:
        pixel = image.getpixel(pos)
        image.putpixel(pos, tuple([max(0, min(255, round(pixel[i] + error[i] * percent))) for i in [0, 1, 2]]))


def parse(image: Image, compressed: bool = False) -> str:
    s = []
    for y in range(0, image.height):
        temp_s = ""
        for x in range(0, image.width):
            op = image.getpixel((x, y))
            np = find_nearest_color(op)
            error = tuple([op[i] - np[i] for i in [0, 1, 2]])
            image.putpixel((x, y), (np[0], np[1], np[2]))
            add_error(image, (x + 1, y), error, 7 / 16)
            add_error(image, (x - 1, y + 1), error, 3 / 16)
            add_error(image, (x, y + 1), error, 5 / 16)
            add_error(image, (x + 1, y + 1), error, 1 / 16)
            temp_s += np[3] + ' '
        s.append(temp_s)
    if compressed:
        s = compress(s)
    image.save('test2.png')
    image.close()
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
