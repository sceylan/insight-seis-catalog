# -*- encoding: utf-8 -*-
""" Utility methods for color ramp files from QGIS. """
import xml.etree.ElementTree as ET

def parse_qgis_color_ramp_file(file_path):
    """ Parse a QGIS color ramp file and return the color ramp as a dictionary.

    Parameters:
    file_path: str
        The path to the QGIS color ramp file.
    """
    # Read the XML content
    with open(file_path, 'r') as f:
        xml_content = f.read()

    if xml_content is None:
        raise ValueError("Failed to read the XML file.")

    # Parse the XML content
    root = ET.fromstring(xml_content)
    
    # Find the colorramp element
    colorramp = root.find('.//colorramp')
    if colorramp is None:
        raise ValueError("Colorramp not found in the XML file.")
    
    # Extract color1 and color2
    color1 = colorramp.find('.//Option[@name="color1"]').attrib['value']
    color2 = colorramp.find('.//Option[@name="color2"]').attrib['value']
    
    # Extract the stops
    stops = colorramp.find('.//Option[@name="stops"]').attrib['value']
    
    # Parse color1 and color2
    color1_rgba = [int(c) for c in color1.split(',')[:4]]
    color2_rgba = [int(c) for c in color2.split(',')[:4]]
    
    # Parse stops
    stop_values = []
    stop_rgba = []
    
    for stop in stops.split(';'):
        # This is the initial stop value
        try:
            f_stop = float(stop)
            stop_values.append(f_stop)
        except ValueError:
            pass
        
        # Secondary stop values
        if "cw:" in stop:
            stop_values.append(float(stop.split(':')[-1]))

        # This is the rgba value
        if 'rgb:' in stop:
            stop_list = [float(c) for c in stop.split(',')[:4]]
            print(stop_list)
            stop_rgba.append(stop_list)
    
    return color1_rgba, color2_rgba, stop_rgba, stop_values


# 0.109375;171,221,164,255,rgb:0.6705882352941176,0.8666666666666667,0.64313725490196083,1;rgb;cw:
# 0.191106;255,255,191,255,rgb:1,1,0.74901960784313726,1;rgb;cw:
# 0.280048;253,174,97,255,rgb:0.99215686274509807,0.68235294117647061,0.38039215686274508,1;rgb;cw