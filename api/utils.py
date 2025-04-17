import pandas as pd

def load_text_file(file_path: str) -> pd.DataFrame:
    
    '''
    file_path: str - path to the file
    ------------
    return: pd.DataFrame - DataFrame containing the data from the file
    
    '''
        
    with open(file_path, 'r', encoding='utf-8') as f:
        data = pd.read_csv(f, encoding='utf-8')
        
    return data