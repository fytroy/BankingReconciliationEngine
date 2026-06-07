# main.py
import os
import time
from src.large_data_generator import generate_tier1_ledger_stream
from src.matching_engine import run_reconciliation
from src.db_writer import DBWriter
import pandas as pd

if __name__ == "__main__":
    print("==========================================================")
    print("      TIER 1 CORE BANKING RECONCILIATION ENGINE           ")
    print("==========================================================\n")
    
    TOTAL_RECORDS = 1000000  # Set to 1M for smooth local execution; scale up as desired
    CHUNK_SIZE = 500000
    DATA_DIR = "data/raw"
    
    # 1. Generate Massive Datasets
    start_gen = time.time()
    generate_tier1_ledger_stream(total_records=TOTAL_RECORDS, chunk_size=CHUNK_SIZE, base_dir=DATA_DIR)
    print(f"[BENCHMARK] Data Generation Finished in {time.time() - start_gen:.2f} seconds.")
    
    # 2. Ingest Data for Reconciliation processing
    print("\nReading generated datasets into memory frames...")
    df_core = pd.read_csv(os.path.join(DATA_DIR, "core_ledger_huge.csv"))
    df_gateway = pd.read_csv(os.path.join(DATA_DIR, "gateway_settlement_huge.csv"))
    
    # 3. Process Core Matching Strategy Engine
    print("Running vector matching checks across ledgers...")
    start_recon = time.time()
    exceptions_df, summary_stats = run_reconciliation(df_core, df_gateway)
    print(f"[BENCHMARK] Matching calculations completed in {time.time() - start_recon:.2f} seconds.")
    
    # 4. Persistence into Target DB Instance Tables
    print(f"\nPersisting run analytics metadata and {len(exceptions_df)} exceptions to SQL Server...")
    try:
        writer = DBWriter()
        run_id = writer.log_recon_run(summary_stats)
        writer.bulk_insert_exceptions(exceptions_df, run_id)
        print(f"SUCCESS: Run ID {run_id} completely written to 'BRE' Database.")
    except Exception as e:
        print(f"DATABASE PERSISTENCE ERROR: {e}")
        print("Verify your connection strings in config/settings.py and database server execution state.")
        
    print("\n========================= RUN COMPLETE =========================")