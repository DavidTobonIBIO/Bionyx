import pandas as pd
import unicodedata
import re

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