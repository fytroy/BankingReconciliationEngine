# tests/test_matching.py
import pytest
import pandas as pd
from src.matching_engine import run_reconciliation

def test_reconciliation_logic():
    # Setup miniature mock datasets representing all 4 business conditions
    core_data = pd.DataFrame({
        'core_txn_id': ['TXN-01', 'TXN-02', 'TXN-03'],
        'timestamp': [pd.Timestamp.now()] * 3,
        'amount': [100.00, 250.00, 500.00],
        'account_no': ['ACC-1', 'ACC-2', 'ACC-3'],
        'gateway_ref': ['REF-MATCH', 'REF-MISMATCH', 'REF-ORPHAN-CORE']
    })

    gateway_data = pd.DataFrame({
        'external_ref_id': ['REF-MATCH', 'REF-MISMATCH', 'REF-ORPHAN-GW'],
        'gateway_amount': [100.00, 240.00, 999.00],
        'gateway_timestamp': [pd.Timestamp.now()] * 3
    })

    exceptions_df, summary = run_reconciliation(core_data, gateway_data)

    # RECON_01 (REF-MATCH) should be excluded from exceptions
    assert 'TXN-01' not in exceptions_df['core_txn_id'].values

    # RECON_02 Check (Amount mismatch)
    recon02 = exceptions_df[exceptions_df['exception_type_code'] == 'RECON_02']
    assert len(recon02) == 1
    assert recon02.iloc[0]['core_txn_id'] == 'TXN-02'

    # RECON_03 Check (Missing in Gateway)
    recon03 = exceptions_df[exceptions_df['exception_type_code'] == 'RECON_03']
    assert len(recon03) == 1
    assert recon03.iloc[0]['core_txn_id'] == 'TXN-03'

    # RECON_04 Check (Missing in Core Ledger)
    recon04 = exceptions_df[exceptions_df['exception_type_code'] == 'RECON_04']
    assert len(recon04) == 1
    assert recon04.iloc[0]['external_ref_id'] == 'REF-ORPHAN-GW'