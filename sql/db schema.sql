-- sql/ddl_schemas.sql

-- 1. Metadata table to track overall reconciliation batch jobs
CREATE TABLE recon_runs (
    run_id INT IDENTITY(1,1) PRIMARY KEY,
    run_date DATETIME DEFAULT GETDATE(),
    source_system VARCHAR(50) NOT NULL,       -- e.g., 'Core_Ledger'
    target_system VARCHAR(50) NOT NULL,       -- e.g., 'MPESA_Gateway'
    total_source_records INT NOT NULL,
    total_target_records INT NOT NULL,
    perfect_matches INT DEFAULT 0,
    variance_count INT DEFAULT 0,
    total_variance_amount DECIMAL(18, 2) DEFAULT 0.00,
    executed_by VARCHAR(50) DEFAULT SYSTEM_USER
);

-- 2. Granular exceptions table for investigation and Power BI reporting
CREATE TABLE unreconciled_exceptions (
    exception_id INT IDENTITY(1,1) PRIMARY KEY,
    run_id INT FOREIGN KEY REFERENCES recon_runs(run_id),
    exception_type_code VARCHAR(10) NOT NULL,  -- RECON_02, RECON_03, RECON_04
    
    -- Core Ledger Data (Will be NULL for RECON_04)
    core_txn_id VARCHAR(50) NULL,
    core_account_no VARCHAR(20) NULL,
    core_amount DECIMAL(18, 2) NULL,
    core_timestamp DATETIME NULL,
    
    -- Gateway Data (Will be NULL for RECON_03)
    external_ref_id VARCHAR(50) NULL,
    gateway_amount DECIMAL(18, 2) NULL,
    gateway_timestamp DATETIME NULL,
    
    -- Auditing Metrics
    variance_amount AS (ISNULL(core_amount, 0.00) - ISNULL(gateway_amount, 0.00)),
    days_outstanding AS (DATEDIFF(day, ISNULL(core_timestamp, gateway_timestamp), GETDATE())),
    
    -- Workflow / Triage Management State
    investigation_status VARCHAR(20) DEFAULT 'OPEN', -- OPEN, INVESTIGATING, RESOLVED, IGNORED
    assigned_to VARCHAR(50) NULL,
    resolution_comments VARCHAR(500) NULL,
    updated_at DATETIME DEFAULT GETDATE()
);

-- Indexing for fast lookups and efficient Power BI dashboard refreshes
CREATE INDEX idx_exceptions_run_id ON unreconciled_exceptions(run_id);
CREATE INDEX idx_exceptions_status ON unreconciled_exceptions(investigation_status);
CREATE INDEX idx_exceptions_type ON unreconciled_exceptions(exception_type_code);