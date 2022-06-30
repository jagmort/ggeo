import bisect
from collections.abc import Mapping
from datetime import datetime
import json
import os
import pytz
import sys

from exif import Image
from pickle import Pickler, Unpickler, HIGHEST_PROTOCOL

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from ggeo_config import config


class closest_dict(Mapping):
    def __init__(self, items):
        s = [*sorted(items)]
        self._keys = [i[0] for i in s]
        self._items = [i[1] for i in s]

    def __getitem__(self, key):
        idx = bisect.bisect_left(self._keys, key)

        if idx > len(self._keys) - 1:
            return self._items[-1]

        if abs(self._keys[idx-1] - key) < abs(self._keys[idx] - key):
            return self._items[idx-1]

        return self._items[idx]

    def __iter__(self):
        yield from self._keys

    def __len__(self):
        return len(self._keys)

def coord(latitude, longitude):
    if latitude > 9e8:
        latitude = (latitude - 4_294_967_296)
    if longitude > 18e8:
        longitude = (longitude - 4_294_967_296)
    return (latitude / 1e7, longitude / 1e7)

def decdeg2dms(dd: float, lat: bool):
    if dd < 0:
        ref = 'S' if lat else 'W'
    else:
        ref = 'N' if lat else 'E'
    mnt, sec = divmod(abs(dd) * 3600, 60)
    deg, mnt = divmod(mnt, 60)
    return (round(deg, 3), round(mnt, 3), round(sec, 3)), ref

def make_pkl():
    with open(config.location_file) as json_file:
        json_data = json.load(json_file)
        print('File is loaded')
        location_data = {}
        for item in json_data['locations']:
            if '.' in item['timestamp']:
                dt = datetime.strptime(item['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z')
            else:
                dt = datetime.strptime(item['timestamp'], '%Y-%m-%dT%H:%M:%S%z')
            location_data[dt] = (dt, ) + coord(item['latitudeE7'], item['longitudeE7'])
    print('Data is created')
    data = closest_dict((k, v) for k, v in location_data.items())
    print('Dictionary is created')
    with open(config.pickle_file, 'wb') as outfile:
        Pickler(outfile, HIGHEST_PROTOCOL).dump(data)
    print('File is saved')

local_tz = pytz.timezone('Europe/Moscow')

with open(config.pickle_file, 'rb') as inputfile:
    data = Unpickler(inputfile).load()
print('File is loaded')

def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)

def get_images_gen():
    for root, dirs, files in os.walk(config.images_path):
        for file in files:
            if '(' not in file and (file.endswith(".JPG") or file.endswith(".jpg") or file.endswith(".JPEG") or file.endswith(".jpeg")):
                yield os.path.join(root, file)

def get_exif_location(file_name):
    dt, latitude, latitude_ref, longitude, longitude_ref = None, None, None, None, None
    with open(file_name, 'rb') as f:
        im = Image(f)
        all = im.list_all()
        if 'datetime_original' in all:
            dt = im.datetime_original
        if 'gps_latitude' in all:
            latitude = im.gps_latitude
        if 'gps_latitude_ref' in all:
            latitude_ref = im.gps_latitude_ref
        if 'gps_longitude' in all:
            longitude = im.gps_longitude
        if 'gps_longitude_ref' in all:
            longitude_ref = im.gps_longitude_ref
        return (dt, latitude, latitude_ref, longitude, longitude_ref)

def get_json_location(file_name):
    with open(file_name) as json_file:
        data = json.load(json_file)
        dt = datetime.fromtimestamp(int(data['photoTakenTime']['timestamp']), pytz.timezone("UTC"))
        return (dt, data['geoData']['latitude'], data['geoData']['longitude'])

def main():
    for jpeg_file in get_images_gen():
        #print(jpeg_file)
        json_file = f'{jpeg_file}.json'
        if os.path.exists(json_file):
            print(jpeg_file)
            (json_dt, json_latitude, json_longitude) = get_json_location(json_file)
            json_latitude, json_latitude_ref = decdeg2dms(json_latitude, True)
            json_longitude, json_longitude_ref = decdeg2dms(json_longitude, False)
            print('JSON', json_dt, json_latitude, json_latitude_ref, json_longitude, json_longitude_ref) 

            g_dt = data[json_dt][0]
            g_latitude, g_latitude_ref = decdeg2dms(data[json_dt][1], True)
            g_longitude, g_longitude_ref = decdeg2dms(data[json_dt][2], False)
            print('Google', utc_to_local(g_dt), g_latitude, g_latitude_ref, g_longitude, g_longitude_ref)

            (exif_dt, exif_latitude, exif_latitude_ref, exif_longitude, exif_longitude_ref) = get_exif_location(jpeg_file)
            print('EXIF', exif_dt, exif_latitude, exif_latitude_ref, exif_longitude, exif_longitude_ref)

            if exif_longitude[0] > 0:
                break

if __name__ == '__main__':
    main()

