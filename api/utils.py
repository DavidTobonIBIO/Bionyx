import pandas as pd
import math
import unicodedata
import re

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def normalize_station_name(name: str) -> str:
    name = name.upper()
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.replace("AV.", "AVENIDA").replace("CR.", "CARRERA").replace("CL.", "CALLE")
    name = re.sub(r'\s+', ' ', name)  # replace multiple spaces
    name = name.strip()
    return name

def load_text_file(file_path: str) -> pd.DataFrame:
    
    '''
    file_path: str - path to the file
    ------------
    return: pd.DataFrame - DataFrame containing the data from the file
    
    '''
        
    with open(file_path, 'r', encoding='utf-8') as f:
        data = pd.read_csv(f, encoding='utf-8')
        
    return data