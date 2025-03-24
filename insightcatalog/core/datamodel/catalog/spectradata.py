# -*- coding: utf-8 -*-
""" Data model for storing the spectra of the event. """
from typing import NamedTuple
import numpy as np

class SpectrumContent(NamedTuple):
    """ Named tuple for storing the spectrum. """
    frequency: np.array
    amplitude: np.array

    def asdict(self):
        return self._asdict()

class Spectrum(NamedTuple):
    """ Named tuple for storing the spectrum of a component. """
    Z: SpectrumContent
    N: SpectrumContent
    E: SpectrumContent

    def get_attribute(self, component, attribute):
        """ Get an attribute from the spectrum. """
        return getattr(getattr(self, component), attribute)

    def asdict(self):
        # Nested dictionary for the spectrum content
        return {'Z': self.Z._asdict(), 'N': self.N._asdict(), 'E': self.E._asdict()}

class Spectra(NamedTuple):
    """ Named tuple for storing the spectra of the event 
    for different time windows. """
    all: Spectrum
    noise: Spectrum
    P: Spectrum
    S: Spectrum

    def get_attribute(self, signal, component, attribute):
        """ Get an attribute from the spectra. """
        return getattr(getattr(self, signal), component)._asdict()[attribute]
    
    def asdict(self):
        return {'all': self.all.asdict(), 'noise': self.noise.asdict(), 
                'P': self.P.asdict(), 'S': self.S.asdict()}
