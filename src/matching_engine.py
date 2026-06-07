# src/matching_engine.py
import pandas as pd
import numpy as np

def run_reconciliation(df_core: pd.DataFrame, df_gateway: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Performs full-outer reconciliation logic between Core Banking Ledger 
    and Gateway Settlement data.
    
    Returns:
        - df_exceptions (pd.DataFrame): Rows flagged with anomalies (RECON_02, RECON_03, RECON_04)
        - summary_stats (dict): High-level metadata dictionary for the database run log
    """
    
    # 1. Full Outer Join on the matching reference key
    # Core uses 'gateway_ref' to point out, Gateway uses 'external_ref_id'
    df_recon = pd.merge(
        df_core, 
        df_gateway, 
        left_on='gateway_ref', 
        right_on='external_ref_id', 
        how='outer', 
        suffixes=('_core', '_gw')
    )
    
    # 2. Vectorized Conditional Tagging using numpy.select
    # Define conditions for our four business states
    conditions = [
        # RECON_01: Perfect Match
        df_recon['gateway_ref'].notna() & df_recon['external_ref_id'].notna() & (df_recon['amount'] == df_recon['gateway_amount']),
        
        # RECON_02: Amount Mismatch (Ref exists on both sides, but amount differs)
        df_recon['gateway_ref'].notna() & df_recon['external_ref_id'].notna() & (df_recon['amount'] != df_recon['gateway_amount']),
        
        # RECON_03: Missing in Gateway (Exists in Core Ledger, but not in Gateway Report)
        df_recon['gateway_ref'].notna() & df_recon['external_ref_id'].isna(),
        
        # RECON_04: Missing in Core (Exists in Gateway Report, but not in Core Ledger)
        df_recon['gateway_ref'].isna() & df_recon['external_ref_id'].notna()
    ]
    
    choices = ['RECON_01', 'RECON_02', 'RECON_03', 'RECON_04']
    
    # Apply conditions to create the status code column
    df_recon['exception_type_code'] = np.select(conditions, choices, default='UNKNOWN')
    
    # 3. Calculate metrics for the run summary metadata
    total_source = len(df_core)
    total_target = len(df_gateway)
    perfect_matches = int((df_recon['exception_type_code'] == 'RECON_01').sum())
    
    # Filter down to true anomalies/exceptions only
    df_exceptions = df_recon[df_recon['exception_type_code'] != 'RECON_01'].copy()
    variance_count = len(df_exceptions)
    
    # Calculate absolute monetary exposure from variances
    # (Handling nulls safely by using filling with 0.0)
    core_amt_clean = df_exceptions['amount'].fillna(0.0)
    gw_amt_clean = df_exceptions['gateway_amount'].fillna(0.0)
    total_variance_amt = float(np.abs(core_amt_clean - gw_amt_clean).sum())
    
    summary_stats = {
        'total_source_records': total_source,
        'total_target_records': total_target,
        'perfect_matches': perfect_matches,
        'variance_count': variance_count,
        'total_variance_amount': total_variance_amt
    }
    
    # Clean up the output dataframe to match our SQL destination schema columns
    df_exceptions = df_exceptions.rename(columns={
        'amount': 'core_amount',
        'timestamp': 'core_timestamp',
        'account_no': 'core_account_no'
    })
    
    # Select only the columns mapping to the `unreconciled_exceptions` table
    final_exception_cols = [
        'exception_type_code', 'core_txn_id', 'core_account_no', 
        'core_amount', 'core_timestamp', 'external_ref_id', 
        'gateway_amount', 'gateway_timestamp'
    ]
    
    return df_exceptions[final_exception_cols], summary_stats