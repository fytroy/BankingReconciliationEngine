# src/large_data_generator.py
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_tier1_ledger_stream(total_records=10000000, chunk_size=500000, base_dir="data/raw"):
    """
    Generates millions of banking ledger and gateway records using chunked streams 
    to prevent memory failure. Simulates real-world financial transaction distributions.
    """
    os.makedirs(base_dir, exist_ok=True)
    
    core_file = os.path.join(base_dir, "core_ledger_huge.csv")
    gateway_file = os.path.join(base_dir, "gateway_settlement_huge.csv")
    
    # Remove old files if executing a fresh run
    for f in [core_file, gateway_file]:
        if os.path.exists(f): os.remove(f)
        
    base_time = datetime(2026, 5, 1, 0, 0, 0)
    
    # Trackers for incremental tracking IDs across chunks
    global_idx = 0
    
    print(f"Starting Tier 1 Data Generation Pipeline [{total_records} rows]...")
    
    for chunk_num in range(0, total_records, chunk_size):
        current_chunk_size = min(chunk_size, total_records - chunk_num)
        
        # 1. Real Financial Distribution: Log-Normal distribution for transaction amounts
        # Most transactions are small (e.g. $10-$50), rare corporate transactions are large ($10,000+)
        amounts = np.round(np.random.lognormal(mean=3.5, sigma=1.2, size=current_chunk_size) + 2.0, 2)
        # Cap excessive outliers to normal corporate limits ($50,000)
        amounts = np.clip(amounts, 1.00, 50000.00)
        
        # 2. Timestamps over 30 days
        seconds_offsets = np.random.randint(0, 2592000, size=current_chunk_size)
        
        # 3. Generating Chunk Core Arrays
        chunk_core_ids = [f"TXN-CORE-{i:08d}" for i in range(global_idx + 1, global_idx + current_chunk_size + 1)]
        chunk_gw_refs = [f"GW-REF-{i:08d}" for i in range(global_idx + 1, global_idx + current_chunk_size + 1)]
        chunk_accounts = [f"ACC-{n}" for n in np.random.randint(1000000, 9999999, size=current_chunk_size)]
        chunk_timestamps = [base_time + timedelta(seconds=int(s)) for s in seconds_offsets]
        
        df_core_chunk = pd.DataFrame({
            'core_txn_id': chunk_core_ids,
            'timestamp': chunk_timestamps,
            'amount': amounts,
            'account_no': chunk_accounts,
            'gateway_ref': chunk_gw_refs
        })
        
        # --- BUILDING THE GATEWAY STREAM WITH SCALED DISCREPANCIES ---
        df_gw_chunk = df_core_chunk.copy()
        
        # Injected Delay (Network latency: 1 to 300 seconds delay on gateway ledger)
# --- BUILDING THE GATEWAY STREAM WITH SCALED DISCREPANCIES ---
        df_gw_chunk = df_core_chunk.copy()
        
        # Injected Delay (Network latency: 1 to 300 seconds delay on gateway ledger)
        df_gw_chunk['gateway_timestamp'] = df_gw_chunk['timestamp'] + pd.to_timedelta(np.random.randint(1, 300, current_chunk_size), unit='s')
        
        # FIX HERE: Drop core_txn_id along with account_no and timestamp
        df_gw_chunk.drop(columns=['core_txn_id', 'account_no', 'timestamp'], inplace=True)
        
        df_gw_chunk.rename(columns={'gateway_ref': 'external_ref_id', 'amount': 'gateway_amount'}, inplace=True)
        
        # Vectorized Variance Injection via fast array masking
        # A. Amount Discrepancies (0.1% of transactions suffer gateway exchange rate/fee distortions)
        amt_mask = np.random.rand(current_chunk_size) < 0.001
        df_gw_chunk.loc[amt_mask, 'gateway_amount'] = np.round(df_gw_chunk.loc[amt_mask, 'gateway_amount'] * 1.012, 2)
        
        # B. Missing from Gateway (0.05% drop rate due to API timeout errors)
        drop_mask = np.random.rand(current_chunk_size) > 0.0005
        df_gw_chunk = df_gw_chunk[drop_mask]
        
        # Append Chunk to Disk immediately (Keeps memory footprint close to zero)
        df_core_chunk.to_csv(core_file, mode='a', header=not os.path.exists(core_file), index=False)
        df_gw_chunk.to_csv(gateway_file, mode='a', header=not os.path.exists(gateway_file), index=False)
        
        global_idx += current_chunk_size
        print(f"Processed chunk {chunk_num + current_chunk_size}/{total_records} records successfully...")
        
    print(f"\nGeneration Complete! Files saved in '{base_dir}' directory.")

if __name__ == "__main__":
    # Test execution with 5 Million rows as a benchmark
    generate_tier1_ledger_stream(total_records=5000000, chunk_size=1000000)