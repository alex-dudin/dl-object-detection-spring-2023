import ctypes
import datetime as dt
import math
import platform
import time
from pathlib import Path
from typing import Iterable
from PIL.ExifTags import TAGS, GPSTAGS


IMAGE_EXTENSIONS = ['jpg', 'png']


def get_exif(image):
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == 'GPSInfo':
                gps_data = {}
                for gps_tag in value:
                    sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
                    gps_data[sub_decoded] = value[gps_tag]
                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value

    return exif_data


def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == 'S' or ref == 'W':
        decimal_degrees = -decimal_degrees
    return decimal_degrees


def get_gps_coordinates(image):
    exif = get_exif(image)
    if 'GPSInfo' in exif:
        gps_info = exif['GPSInfo']
        lat = decimal_coords(gps_info['GPSLatitude'], gps_info['GPSLatitudeRef'])
        lon = decimal_coords(gps_info['GPSLongitude'], gps_info['GPSLongitudeRef'])
        return lat, lon
    return None, None


def get_datetime_original(image):
    exif = get_exif(image)
    if 'DateTimeOriginal' in exif:
        return dt.datetime.strptime(exif['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')

    return None


def deg_to_dms(deg, type='lat'):
    decimals, number = math.modf(deg)
    d = int(number)
    m = int(decimals * 60)
    s = (deg - d - m / 60) * 3600.00
    compass = {
        'lat': ('N','S'),
        'lon': ('E','W')
    }
    compass_str = compass[type][0 if d >= 0 else 1]
    return f'{abs(d)}º{abs(m)}\'{abs(s):.2f}"{compass_str}'


class Stopwatch:

    def __init__(self):
        self.start_time = time.perf_counter()

    def elapsed(self, seconds_rounding=float) -> dt.timedelta:
        return dt.timedelta(seconds=seconds_rounding(self.elapsed_seconds()))

    def elapsed_seconds(self) -> float:
        return time.perf_counter() - self.start_time


def enum_images(root: Path) -> Iterable[Path]:
    for path in root.rglob('*.*'):
        if path.suffix[1:].lower() in IMAGE_EXTENSIONS:
            yield path


def set_console_title(title: str):
    if platform.system() == 'Windows':
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    else:
        print(f'\33]0;{title}\a', end='', flush=True)


def remaining_time(stopwatch: Stopwatch, done: int, total: int, seconds_rounding=float) -> dt.timedelta:
    assert done > 0
    assert done <= total
    remaining_seconds = stopwatch.elapsed().total_seconds() / done * (total - done)
    return dt.timedelta(seconds=seconds_rounding(remaining_seconds))
