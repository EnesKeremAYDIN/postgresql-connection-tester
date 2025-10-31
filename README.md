# PostgreSQL Connection Tester

Comprehensive PostgreSQL connection testing and analysis toolkit written in Python. This tool allows you to test database connections, analyze server performance, and gather detailed information about your PostgreSQL instances using only native Python libraries and psycopg2.

## Features

- **URL Parsing**: Parse PostgreSQL connection URLs with parameter support
- **Connection Testing**: Test database connectivity with detailed error reporting
- **Performance Metrics**: Measure connection and query execution times
- **Server Analysis**: Gather server details, database statistics, and configuration info
- **Interactive Interface**: User-friendly CLI with emoji-rich output

## Installation and Usage

1. **Clone the repository**:
   ```bash
   git clone https://github.com/EnesKeremAYDIN/postgresql-connection-tester.git
   cd postgresql-connection-tester
   ```

2. **Install dependencies**:
   - The tool uses `psycopg2-binary`. Install it via pip:
   ```bash
   pip install psycopg2-binary
   ```

3. **Run the tool**:
   ```bash
   python script.py
   ```

## Supported URL Formats

The tool supports standard PostgreSQL connection URLs:

```
postgresql://username@hostname/database
postgresql://username:password@hostname:port/database?sslmode=prefer
```

## Information Collected

- **Server**: Version, IP, port, startup time
- **Database**: Name, user, schema, size, connection counts
- **Performance**: Memory settings, WAL buffers, checkpoint config
- **Statistics**: Table counts, schemas, users, databases

## Files

- **`script.py`** – The main script file for PostgreSQL connection testing and analysis.

## Requirements

- Python 3.x
- PostgreSQL database access
- `psycopg2-binary` library
- Network connectivity to the target database

## Error Handling

- **Host Unreachable**: Network connectivity issues
- **Connection Failed**: Authentication or parameter errors
- **Query Errors**: Database query execution issues
- **URL Parsing**: Invalid connection URL format

## Security Features

- **Password Masking**: Passwords hidden in output
- **SSL Support**: Full SSL mode configuration
- **Connection Timeout**: 10-second default timeout
- **Safe Error Reporting**: No sensitive data exposure

## Disclaimer


This tool is intended for database administrators, developers, and system administrators to test and analyze PostgreSQL connections. Use responsibly and only on databases you have permission to access. Always ensure you have proper authorization before testing database connections.
