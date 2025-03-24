# *-* coding: utf-8 *-*
from scipy.io import loadmat
import numpy as np
from core.utils.customlogger import logger

class Faults:
    def __init__(self):
        self.global_faults = [] 
        self.cerberus_faults = []

    def get_global_faults(self):
        """ Return the global faults as a list of tuples """
        return self.global_faults
    
    def get_cerberus_faults(self):
        return self.cerberus_faults
    
    def __repr__(self):
        return f'Faults({self.global_faults})'
    
    def __str__(self):
        return f'Faults, Global: {len(self.global_faults)}, CF: {len(self.cerberus_faults)}'
    
    @staticmethod
    def read(global_faults_file, cerberus_faults_file):
        """ Read the global and Cerberus faults together. """
        _self = Faults()
        
        _self.read_global_faults(global_faults_file)
        _self.read_cerberus_faults(cerberus_faults_file)
        
        return _self
    
    def read_global_faults(self, filename):
        """
        Read the global faults of Knapmeyer et al. 
        The file is newfaults.mat
        """
        logger.info(f'Reading global faults from {filename}')
        
        faults = loadmat(filename)
        
        for f in faults['newfaults']:
            lons = f['lon'].flatten()
            lats = f['lat'].flatten()
            
            lons = np.concatenate([lon.flatten() for lon in lons])
            lats = np.concatenate([lat.flatten() for lat in lats])

            self.global_faults.append([lons, lats])
        
        # Log message and return the self object
        logger.ok(f'Read {len(self.global_faults)} global faults')
        
        return self
    
    def read_cerberus_faults(self, filename):
        """
        Read the Cerberus faults from Perrin et al. 
        The file is Cerberus-Perrin-etal.csv
        """
        logger.info(f'Reading Cerberus faults from {filename}')
        cf_faults = {}
        with open(filename) as cf_faults_file:
            lines = cf_faults_file.readlines()

            for fault_idx, line in enumerate(lines):
                line = line[13:].strip()
                if line:
                    line = line[0:line.index(')')]
                    cf_faults[fault_idx] = {'lon': [], 'lat': []}
                    coord_pairs = line.split(',')

                    for coord in coord_pairs:
                        lon, lat = coord.split(' ')
                        cf_faults[fault_idx]['lon'].append(float(lon))
                        cf_faults[fault_idx]['lat'].append(float(lat))
        
        # Cerberus faults are too dense. Use only the first and 
        # the last points of each fault segment.
        self.cerberus_faults = [
            ([cf_faults[idx]['lon'][0], cf_faults[idx]['lon'][-1]], 
             [cf_faults[idx]['lat'][0], cf_faults[idx]['lat'][-1]]) 
             for idx in cf_faults]

        logger.ok(f'Read {len(self.cerberus_faults)} Cerberus faults')

        return self
    
    def filter_global_faults(self, min_lat, max_lat, min_lon, max_lon):
        self.global_faults = [
            fault for fault in self.global_faults 
                if min_lat <= fault.latitude <= max_lat 
                    and min_lon <= fault.longitude <= max_lon]