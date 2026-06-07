-- sql/audit_queries.sql
USE BRE;
GO

-- 1. Flattened Fact Table View for Power BI
CREATE OR ALTER VIEW v_fact_unreconciled_exceptions AS
SELECT 
    exception_id,
    run_id,
    exception_type_code,
    core_txn_id,
    core_account_no,
    core_amount,
    core_timestamp,
    CAST(core_timestamp AS DATE) AS core_date_key, -- Used for Date Dimension joining
    external_ref_id,
    gateway_amount,
    gateway_timestamp,
    variance_amount,
    days_outstanding,
    investigation_status,
    ISNULL(assigned_to, 'Unassigned') AS assigned_to,
    resolution_comments
FROM unreconciled_exceptions;
GO

-- 2. Run Metadata Dimension View
CREATE OR ALTER VIEW v_dim_recon_runs AS
SELECT 
    run_id,
    run_date,
    CAST(run_date AS DATE) AS run_date_key,
    total_source_records,
    total_target_records,
    perfect_matches
FROM recon_runs;
GO