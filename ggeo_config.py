class ggeo:
    photo_dir = 'D:\\Takeout\\Google Photos'
    test_photo = 'data\\75E2CE7E-A4C0-4319-B1C2-7DD9C8AB5AC0.jpg'
    location_file = 'D:\\Takeout\\Location History\\Records.json'
    exif = {'datetime': 306, 'date_origin': 36867}
    def coord(latitudeE7, longitudeE7):
        if latitudeE7 > 900000000:
            lat = (latitudeE7 - 4294967296) / 1e7
        if longitudeE7 > 1800000000:
            long = (longitudeE7 - 4294967296) / 1e7
        return (lat, long)

if __name__ == '__main__':
    exit()