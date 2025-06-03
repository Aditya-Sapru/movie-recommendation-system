from sqlalchemy import create_engine, text
import pandas as pd

# --- Database Connection Details ---
# IMPORTANT: Replace 'username', 'password', and 'yourdatabase' with your actual PostgreSQL credentials and database name.
DB_USERNAME = 'postgres'
DB_PASSWORD = 'Adianshu00#'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'moviedb' # This is the database you expect to be created

# Construct the connection string for the database you want to check
# For checking if the database itself exists, we'll first try connecting to a default database like 'postgres'
# or 'template1' to query `pg_database`.
# Then, if the database exists, we'll connect directly to it.

def check_database_and_table():
    """
    Checks for the existence of the specified database and table in PostgreSQL.
    """
    # First, try connecting to a default database to check if 'yourdatabase' exists
    try:
        temp_engine = create_engine(f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres')
        with temp_engine.connect() as connection:
            # Check if the database exists
            db_exists_query = text(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
            result = connection.execute(db_exists_query).fetchone()
            if result:
                print(f"Database '{DB_NAME}' exists.")
                # Now, connect to the specific database to check for the table
                try:
                    target_engine = create_engine(f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
                    with target_engine.connect() as target_connection:
                        # Check if the 'movies' table exists within 'yourdatabase'
                        table_exists_query = text(f"""
                            SELECT 1 FROM information_schema.tables
                            WHERE table_schema = 'public' AND table_name = 'movies'
                        """)
                        table_result = target_connection.execute(table_exists_query).fetchone()

                        if table_result:
                            print(f"Table 'movies' exists in database '{DB_NAME}'.")
                            # Optionally, read a few rows to confirm data
                            try:
                                df_check = pd.read_sql('SELECT * FROM movies LIMIT 5', target_engine)
                                print("\nFirst 5 rows from 'movies' table:")
                                print(df_check)
                            except Exception as e:
                                print(f"Error reading data from 'movies' table: {e}")
                        else:
                            print(f"Table 'movies' does NOT exist in database '{DB_NAME}'.")

                except Exception as e:
                    print(f"Could not connect to database '{DB_NAME}'. Please ensure it is accessible and your credentials are correct.")
                    print(f"Error: {e}")
            else:
                print(f"Database '{DB_NAME}' does NOT exist.")

    except Exception as e:
        print(f"Could not connect to PostgreSQL server using default database 'postgres'.")
        print(f"Please ensure PostgreSQL is running and your username/password are correct.")
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database_and_table()