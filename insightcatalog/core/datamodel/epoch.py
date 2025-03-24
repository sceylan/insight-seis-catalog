# *-* coding: utf-8 *-*
""" Annotated epoch classes as marked by the MQS team. """
import obspy
from insightcatalog.core.utils.customlogger import logger

class AnnotationTypes:
    """ Dummy enum class for annotation types """
    GLITCH_SINGLE_COMP = 'SINGLE_COMPONENT'
    GLITCH_MULTI_COMP = 'MULTIPLE_COMPONENT'
    DUST_DEVIL = 'PRESSURE_DROP_DUST_DEVIL'
    DONK = 'DONKS'
    EVENING_RUMBLE = 'EVENING_RUMBLE'
    SUSPICIOUS_SIGNAL = 'SUSPICIOUS_SEISMIC_SIGNAL'
    VBB2_LP_NOISE = 'VBB_V_LP_NOISE'
    VBB_V_GLITCH_TRAIN = 'VBB_V_GLITCH_TRAIN'

    @staticmethod
    def to_list():
        return [AnnotationTypes.GLITCH_SINGLE_COMP,
                AnnotationTypes.GLITCH_MULTI_COMP,
                AnnotationTypes.DUST_DEVIL,
                AnnotationTypes.DONK,
                AnnotationTypes.SUSPICIOUS_SIGNAL,
                AnnotationTypes.EVENING_RUMBLE,
                AnnotationTypes.VBB_V_GLITCH_TRAIN,
                AnnotationTypes.VBB2_LP_NOISE]
    
class Epoch(dict):
    """ Class to store a single annotated epoch """
    def __init__(self, starttime=None, endtime=None, epoch_type=None, **kwargs):
        super().__init__(**kwargs)
        
        self['starttime'] = starttime
        self['endtime'] = endtime
        self['epochtype'] = epoch_type

    @property
    def starttime(self):
        return self.get('starttime')

    @starttime.setter
    def starttime(self, value):
        if isinstance(value, obspy.UTCDateTime):
            self['starttime'] = value
        else:
            try:
                self['starttime'] = obspy.UTCDateTime(value)
            except:
                raise ValueError('Invalid starttime value')

    @property
    def endtime(self):
        return self.get('endtime')

    @endtime.setter
    def endtime(self, value):
        if isinstance(value, obspy.UTCDateTime):
            self['endtime'] = value
        else:
            try:
                self['endtime'] = obspy.UTCDateTime(value)
            except:
                raise ValueError('Invalid endtime value')

    @property
    def epochtype(self):
        return self.get('epochtype')

    @epochtype.setter
    def epochtype(self, value):
        self['epochtype'] = value

    def set_starttime(self, value):
        self.starttime = value

    def set_endtime(self, value):
        self.endtime = value

    def set_epochtype(self, value):
        self.epochtype = value

    def get_starttime(self):
        return self.starttime
    
    def get_endtime(self):
        return self.endtime
    
    def get_epochtype(self):
        return self.epochtype
    
    def get_duration(self):
        return self.endtime - self.starttime
    
    def __getitem__(self, key):
        return self.get(key)
    
    def __setitem__(self, key, value):
        # Make sure to call the super class method to 
        # avoid infinite recursion
        super().__setitem__(key, value)

    def __repr__(self):
        return f'Epoch({self.starttime}, {self.endtime}, {self.epochtype})'
    
    def __str__(self):
        return f'Epoch: {self.starttime} to {self.endtime} ({self.epochtype})'
    
    def __eq__(self, other):
        return (self.starttime == other.starttime and
                self.endtime == other.endtime and
                self.epochtype == other.epochtype)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    

class AnnotatedEpochs:
    """ Class to store and manage a list of Epochs """
    def __init__(self, epochs=None) -> None:
        # If epochs is not provided, create an empty list
        self._epochs = epochs if epochs else []
        
    def __repr__(self):
        return f'AnnotatedEpochs({len(self._epochs)} epochs)'
    
    def __str__(self):
        return f'AnnotatedEpochs with {len(self._epochs)} epochs'
    
    def __len__(self):
        return len(self._epochs)
    
    def __getitem__(self, index):
        return self._epochs[index]
    
    def __iter__(self):
        return iter(self._epochs)
    
    def __contains__(self, epoch):
        return epoch in self._epochs
    
    def __add__(self, other):
        if not isinstance(other, AnnotatedEpochs):
            raise TypeError(
                'Can only add AnnotatedEpochs to AnnotatedEpochs')
        return AnnotatedEpochs(self._epochs + other._epochs)
    
    def append(self, epoch):
        self._epochs.append(epoch)

    def extend(self, epochs):
        self._epochs.extend(epochs)

    def remove(self, epoch):
        self._epochs.remove(epoch)

    def clear(self):
        self._epochs.clear()

    @staticmethod
    def read(annotations_file):
        """ Read annotated epochs from the given file"""
        # This is a new read. Create a new object 
        _self = AnnotatedEpochs()

        logger.info(f'Reading annotated epochs from {annotations_file}')

        # Read the file and parse the lines
        with open(annotations_file, 'r') as fin:
            _lines = fin.readlines()

            for _line in _lines:
                # Remove quotes and split the line
                _line = _line.replace('"', '')
                _tokens = _line.split(',')

                # Sometimes start or end time does not exist. Check for
                # these cases beforehand
                if len(_tokens) > 2 and _tokens[0] and len(_tokens[0]) > 0:
                    for _type in AnnotationTypes.to_list():
                        if _line.find(_type) > -1:
                            _starttime = obspy.UTCDateTime(_tokens[0])

                            if _tokens[1] and len(_tokens[1]) > 0:
                                _endtime = obspy.UTCDateTime(_tokens[1])
                            else:
                                _endtime = _starttime + 35

                            _epoch = Epoch(_starttime, _endtime, _type)
                            _self.append(_epoch)
                            
        logger.ok(f'Read {len(_self)} epochs from {annotations_file}')
        return _self

    def select(self, starttime=None, endtime=None, epoch_type=None):
        """ Filter epochs by type, starttime and endtime."""
        selected_epochs = []

        for epoch in self._epochs:
            # If any of the conditions are not met, skip this epoch
            if epoch_type and epoch.epochtype != epoch_type:
                continue
            if starttime and epoch.starttime <= starttime:
                continue
            if endtime and epoch.endtime >= endtime:
                continue

            # Conditions are met. Add this epoch to the list
            selected_epochs.append(epoch)

        # Return a new AnnotatedEpochs object with the selected 
        # epochs so that same class interface is maintained
        return AnnotatedEpochs(selected_epochs)
    