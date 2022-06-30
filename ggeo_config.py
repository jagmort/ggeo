from dataclasses import dataclass

@dataclass
class Config:
    pickle_file: str
    images_path: str
    location_file: str
    destination_path: str

config = Config(
    pickle_file = r'geo.pkl',
    images_path = r'D:\Takeout\Google Photos\Photos from 2018',
    location_file = r'D:\Takeout\Location History\Records.json',
    destination_path = r'E:\ggeo_photo'
)

if __name__ == '__main__':
    exit()