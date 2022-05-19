from datetime import datetime
import json
import os
import sys

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from ggeo_config import ggeo


def main():
    with open(f'{ggeo.test_photo}.json') as json_file:
        data = json.load(json_file)
        print('JSON datetime', datetime.fromtimestamp(int(data['photoTakenTime']['timestamp'])))
        print('JSON latitude', data['geoData']['latitude'])
        print('JSON longitude', data['geoData']['longitude'])
        print('JSON altitude', data['geoData']['altitude'])

    my_image = Image.open(ggeo.test_photo)
    info = my_image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == 'DateTimeOriginal':
                print(decoded, value)
            if decoded == 'GPSInfo':
                print(decoded, value)
                for key in value.keys():
                    decode = GPSTAGS.get(key, key)
                    print(decode, value[key])

if __name__ == '__main__':
    main()

