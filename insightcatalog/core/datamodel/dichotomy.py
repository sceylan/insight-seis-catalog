# *-* coding: utf-8 *-*
from core.utils.customlogger import logger
    
class Dichotomy:
    """ Class to read and store the coordinates of the Martian dichotomy."""
    def __init__(self) -> None:
        self.lats = []
        self.lons = []

    @staticmethod
    def read(filename: str) -> None:
        logger.info(f'Reading dichotomy coordinates from {filename}')

        # Create a new object
        _self = Dichotomy()

        with open(filename, 'r') as f:
            for line in f:
                lon, lat = line.split()
                _self.lats.append(float(lat))
                _self.lons.append(float(lon))
        
        logger.ok(f'Read {len(_self.lats)} coordinates')
        
        # Return the object itself so that we can chain methods
        return _self
    
    def add(self, lat: float, lon: float) -> None:
        self.lats.append(lat)
        self.lons.append(lon)

    def add_lat(self, lat: float) -> None:
        self.lats.append(lat)

    def add_lon(self, lon: float) -> None:
        self.lons.append(lon)

    def set_coordinates(self, lats: list, lons: list) -> None:
        self.lats = lats
        self.lons = lons

    def get_coordinates(self) -> tuple:
        return self.lats, self.lons
    
    def __repr__(self) -> str:
        return f'Dichotomy({len(self.lats)} coordinates)'
    
    def __str__(self) -> str:
        return f'Dichotomy: latitudes {len(self.lats)}, and longitudes {len(self.lons)}'
    
    def __new__(cls) -> object:
        return super().__new__(cls)
