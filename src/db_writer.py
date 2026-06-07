# src/db_writer.py
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from config.settings import DATABASE_URL

class DBWriter:
    def __init__(self):
        # We maintain the engine structure for compatibility, but extract the raw DBAPI connection factory
        self.engine = create_engine(DATABASE_URL)

    def log_recon_run(self, summary_stats: dict) -> int:
        """
        Logs metadata execution metrics using a clean, native driver connection 
        with fast_executemany disabled to guarantee safe scalar identity returns.
        """
        insert_query = """
            SET NOCOUNT ON;
            INSERT INTO recon_runs (source_system, target_system, total_source_records, 
                                    total_target_records, perfect_matches, variance_count, total_variance_amount)
            VALUES ('Core_Ledger', 'Gateway_Settlement', ?, ?, ?, ?, ?);
            SELECT CAST(SCOPE_IDENTITY() AS INT);
        """
        
        # Pull a clean, native pyodbc connection straight from the driver layer
        raw_conn = self.engine.raw_connection()
        try:
            cursor = raw_conn.cursor()
            # CRITICAL: Keep fast_executemany disabled for this transactional fetch
            cursor.fast_executemany = False 
            
            params = (
                summary_stats['total_source_records'],
                summary_stats['total_target_records'],
                summary_stats['perfect_matches'],
                summary_stats['variance_count'],
                summary_stats['total_variance_amount']
            )
            
            cursor.execute(insert_query, params)
            run_id = cursor.fetchval() # Safely grabs the single output scalar
            raw_conn.commit()
            return int(run_id)
        except Exception as e:
            raw_conn.rollback()
            raise e
        finally:
            raw_conn.close()

    def bulk_insert_exceptions(self, df_exceptions: pd.DataFrame, run_id: int):
        """
        Bulk inserts identified financial anomalies using raw DBAPI cursor execution.
        Safely toggles fast_executemany to True on an isolated connection loop.
        """
        if df_exceptions.empty:
            return

        df = df_exceptions.copy()
        df['run_id'] = run_id
        df['investigation_status'] = 'OPEN'
        df['assigned_to'] = None
        df['resolution_comments'] = None
        df['updated_at'] = pd.Timestamp.now()
        
        # Map NumPy NaNs straight to Python Nones
        df = df.replace({np.nan: None})

        insert_query = """
            INSERT INTO unreconciled_exceptions (
                exception_type_code, core_txn_id, core_account_no, 
                core_amount, core_timestamp, external_ref_id, 
                gateway_amount, gateway_timestamp, run_id, 
                investigation_status, assigned_to, resolution_comments, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        records = list(df[[
            'exception_type_code', 'core_txn_id', 'core_account_no', 
            'core_amount', 'core_timestamp', 'external_ref_id', 
            'gateway_amount', 'gateway_timestamp', 'run_id', 
            'investigation_status', 'assigned_to', 'resolution_comments', 'updated_at'
        ]].itertuples(index=False, name=None))

        raw_conn = self.engine.raw_connection()
        try:
            cursor = raw_conn.cursor()
            # CRITICAL: Safe to enable high-speed array binding on this fresh transaction block
            cursor.fast_executemany = True 
            cursor.executemany(insert_query, records)
            raw_conn.commit()
        except Exception as e:
            raw_conn.rollback()
            raise e
        finally:
            raw_conn.close()