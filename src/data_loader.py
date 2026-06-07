# src/data_loader.py
import pandas as pd
import os
from config.settings import DATA_RAW_DIR

def stream_csv_chunks(filename: str, chunk_size: int = 1000000):
    """
    Generator that yields dataframes from a CSV file in chunks 
    to preserve system memory.
    """
    file_path = os.path.join(DATA_RAW_DIR, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source data file missing at: {file_path}")
        
    return pd.read_csv(file_path, chunksize=chunk_size)