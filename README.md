# Banking Reconciliation Engine

## Description

This project is a banking reconciliation engine that matches transactions from a core ledger with settlement reports from a payment gateway.

## Project Structure

```
BankingReconciliationEngine/
├── .gitignore
├── config/
│   └── settings.py
├── data/
│   └── raw/
│       ├── core_ledger_huge.csv
│       └── gateway_settlement_huge.csv
├── main.py
├── README.md
├── requirements.txt
├── sql/
│   ├── create views.sql
│   └── db schema.sql
├── src/
│   ├── data_loader.py
│   ├── db_writer.py
│   ├── large_data_generator.py
│   └── matching_engine.py
└── tests/
    └── test_matching.py
```

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd BankingReconciliationEngine
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Database Setup

The project uses a database to store and reconcile the data.

1.  **Database Schema:**
    The database schema is defined in `sql/db schema.sql`. You need to execute this script to create the necessary tables.

2.  **Create Views:**
    The `sql/create views.sql` script creates views that might be used for reporting or analysis.

## Usage

To run the reconciliation engine, execute the `main.py` script:

```bash
python main.py
```

This will load the data from the CSV files, write it to the database, and then run the matching engine to reconcile the transactions.

## Data

The `data/raw` directory contains the input data for the reconciliation engine:

*   `core_ledger_huge.csv`: Transactions from the core banking system.
*   `gateway_settlement_huge.csv`: Settlement reports from the payment gateway.

The `src/large_data_generator.py` script can be used to generate larger datasets for testing purposes.

## Configuration

The `config/settings.py` file contains configuration settings for the application, such as database connection details. You may need to update this file with your local settings.

## Testing

To run the tests, you can use `pytest`:

```bash
pytest
```

The tests are located in the `tests/` directory.
