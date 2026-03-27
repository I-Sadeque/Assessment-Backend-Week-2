import pandas as pd
import pytest

from psycopg2.extensions import connection

@pytest.mark.parametrize("task_num", (0, 1, 2, 3, 4))
class TestDQLTask:
    """Runs checks for the DQL tasks."""

    def get_expected_result(self, task_num: int) -> pd.DataFrame:
        """Reads the expected result from a file."""
        task_csv = pd.read_csv(
            f'expected_outputs/task_{task_num}.csv', dtype=str)
        return task_csv.astype(str)
    
    def get_query_from_file(self, task_num: int) -> None:
        """Reads in a SQL query from a file."""
        with open(f'queries/task_{task_num}.sql', 'r') as file:
            query = file.read()
        return query

    def get_actual_result(self, task_num, test_temp_conn: connection) -> pd.DataFrame:
        """Runs the provided query against the database and returns the result."""
        with test_temp_conn.cursor() as cur:
            cur.execute(self.query)
            return pd.DataFrame(cur.fetchall()).astype(str)

    def setup_values(self, task_num, test_temp_conn):
        """Sets the required variables for each test."""
        self.query = self.get_query_from_file(task_num)
        self.expected_result = self.get_expected_result(task_num)
        self.actual_result = self.get_actual_result(task_num, test_temp_conn)

    def test_correct_columns_task_(self, task_num, test_temp_conn):
        """Checks that the query result has the same columns as the expected result."""
        self.setup_values(task_num, test_temp_conn)

        assert self.actual_result.columns.to_list() == self.expected_result.columns.to_list()

    def test_correct_number_of_rows_task_(self, task_num, test_temp_conn):
        """Checks that the query result has the expected number of rows."""
        self.setup_values(task_num, test_temp_conn)

        assert self.actual_result.shape[0] == self.expected_result.shape[0]

    def test_data_in_correct_order_task_(self, task_num, test_temp_conn):
        """Checks that the query result has the expected order."""
        self.setup_values(task_num, test_temp_conn)

        assert self.expected_result.iloc[:, 0].equals(self.actual_result.iloc[:, 0])

    def test_exact_data_match_task_(self, task_num, test_temp_conn):
        """Checks that the query result has the exact same data."""
        self.setup_values(task_num, test_temp_conn)

        assert self.actual_result.equals(self.expected_result)


@pytest.mark.parametrize("task_num", (5, 6, 7))
class TestDMLTask:
    """Runs checks for the DML tasks."""

    def get_expected_result(self, task_num: int) -> pd.DataFrame:
        """Reads the expected result from a file."""
        task_csv = pd.read_csv(
            f'expected_outputs/task_{task_num}.csv', dtype=str)
        return task_csv.astype(str)
    
    def get_query_from_file(self, task_num: int) -> None:
        """Reads in a SQL query from a file."""
        with open(f'queries/task_{task_num}.sql', 'r') as file:
            query = file.read()
        return query
    
    def run_command(self, test_temp_conn):
        """Runs the DML command against the database."""
        with test_temp_conn.cursor() as cur:
            cur.execute(self.query)

    def get_database_state(self, task_num, test_temp_conn: connection) -> pd.DataFrame:
        """Gets the current state of the affected table."""
        with test_temp_conn.cursor() as cur:
            if task_num == 6:
                # Task number 6 modifies the subject table
                cur.execute('SELECT * FROM subject;')
            else:
                # Task numbers 5 and 7 modify the experiment table
                cur.execute('SELECT * FROM experiment;')
            return pd.DataFrame(cur.fetchall()).astype(str)

    def setup_values(self, task_num, test_temp_conn):
        """Sets the required variables for each test."""
        self.query = self.get_query_from_file(task_num)
        self.expected_result = self.get_expected_result(task_num)
        self.run_command(test_temp_conn)
        self.actual_result = self.get_database_state(task_num, test_temp_conn)

    def test_correct_columns_task_(self, task_num, test_temp_conn):
        """Checks that the affected table has the same columns as the expected result."""
        self.setup_values(task_num, test_temp_conn)

        assert self.actual_result.columns.to_list() == self.expected_result.columns.to_list()

    def test_correct_number_of_rows_task_(self, task_num, test_temp_conn):
        """Checks that the affected table has the expected number of rows."""
        self.setup_values(task_num, test_temp_conn)

        assert self.actual_result.shape[0] == self.expected_result.shape[0]

    def test_data_in_correct_order_task_(self, task_num, test_temp_conn):
        """Checks that the affected table has the expected order."""
        self.setup_values(task_num, test_temp_conn)

        assert self.expected_result.iloc[:, 0].equals(self.actual_result.iloc[:, 0])

    def test_exact_data_match_task_(self, task_num, test_temp_conn):
        """Checks that the affected table has the exact same data."""
        self.setup_values(task_num, test_temp_conn)

        assert self.actual_result.equals(self.expected_result)