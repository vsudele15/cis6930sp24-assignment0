import pytest
from unittest.mock import patch
from unittest import mock
from assignment0 import main

# Sample data for testing
record = "1/21/2024 23:30 2024-00001511 318 E HAYES ST Falls EMSSTAT"
adjusted_incident_num = "2024-00001511I38"
middle_com = ["318", "E", "HAYES", "ST", "Falls"]
ori = "EMSSTAT"
sample_page_content = [
    "1/1/2024 23:14 2024-00000215 4741 N PORTER AVE Traffic Stop OK0140200",
    "1/1/2024 23:17 2024-00000062 2000 ANN BRANDEN BLVD Transfer/Interfacility EMSSTAT",
    "1/1/2024 23:38 2024-00000218 1028 LESLIE LN 911 Call Nature Unknown OK0140200",
]
expected_incidents = [
    {
        "incident_time": "23:14",
        "incident_number": "2024-00000215",
        "incident_location": "4741 N PORTER AVE",
        "incident_nature": "Traffic Stop",
        "incident_ori": "OK0140200",
    },
    {
        "incident_time": "23:17",
        "incident_number": "2024-00000062",
        "incident_location": "2000 ANN BRANDEN BLVD",
        "incident_nature": "Transfer/Interfacility",
        "incident_ori": "EMSSTAT",
    },
    {
        "incident_time": "23:38",
        "incident_number": "2024-00000218",
        "incident_location": "1028 LESLIE LN",
        "incident_nature": "911 Call Nature Unknown",
        "incident_ori": "OK0140200",
    },
]
sample_page_con = """
Date / Time Incident Number Location Nature Incident ORI
1/17/2024 1:16 2024-00003594 222 MCCULLOUGH ST Suspicious OK0140200NORMAN POLICE DEPARTMENT
Daily Incident Summary (Public)
"""


@pytest.fixture
def mock_db_cursor():
    cursor = mock.MagicMock()
    cursor.fetchall.return_value = []
    return cursor


@pytest.fixture
def mock_db_connection(mock_db_cursor):
    db = mock.MagicMock()
    db.cursor.return_value = mock_db_cursor
    return db


@pytest.fixture
def mock_sqlite_connect():
    with patch("assignment0.main.sqlite3.connect") as mock_connect:
        mock_connection = mock.MagicMock()
        mock_cursor = mock.MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        yield mock_connect, mock_connection, mock_cursor


def test_fetch_incidents_success():
    url = "http://example.com/incidents"
    mock_data = b"Mock incident data"
    with mock.patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.return_value.read.return_value = mock_data
        data = main.fetch_incidents(url)
        assert data == mock_data


def test_extract_incidents():
    # Mocks
    reader = mock.Mock()
    mock_page = mock.Mock()
    mock_page.extract_text.return_value = sample_page_con
    reader.pages = [mock_page, mock_page]
    sample_incident_data = mock.Mock()
    with patch("assignment0.main.io.BytesIO", return_vale=mock.Mock()), \
            patch("assignment0.main.PdfReader", return_value=reader), \
            patch("assignment0.main.get_inc_details", return_value=sample_page_content):
        incidents = main.extract_incidents(sample_incident_data)

        assert incidents[0] == '1/1/2024 23:14 2024-00000215 4741 N PORTER AVE Traffic Stop OK0140200'
        assert incidents[1] == '1/1/2024 23:17 2024-00000062 2000 ANN BRANDEN BLVD Transfer/Interfacility EMSSTAT'
        assert incidents[2] == '1/1/2024 23:38 2024-00000218 1028 LESLIE LN 911 Call Nature Unknown OK0140200'


def test_split_record_components():
    expected = ("23:30", "2024-00001511", ["318", "E", "HAYES", "ST", "Falls"], "EMSSTAT")
    assert main.split_record_components(record) == expected


def test_adjust_incident_number():
    inc_num, middle = main.adjust_incident_number(adjusted_incident_num, middle_com)
    assert inc_num == "2024-00001511"
    assert middle == ["I38", "318", "E", "HAYES", "ST", "Falls"]


def test_is_location_component():
    assert main.is_location_component("318") is True
    assert main.is_location_component("E") is True
    assert main.is_location_component("HAYES") is True
    assert main.is_location_component("ST") is True
    assert main.is_location_component("Falls") is False


def test_process_middle_components():
    loc, nat = main.process_middle_components(middle_com)
    assert loc == ["318", "E", "HAYES", "ST"]
    assert nat == ["Falls"]


def test_handle_numeric_edge_case_in_location():
    loc = ["318", "E", "HAYES", "ST", "911"]
    nat = ["No Injuries"]
    loc, nat = main.handle_numeric_edge_case_in_location(loc, nat)
    assert loc == ["318", "E", "HAYES", "ST"]
    assert nat == ["911", "No Injuries"]


def test_create_inc_record():
    time = "23:30"
    inc_num = "2024-00001511"
    loc = ["318 E HAYES ST"]
    nat = ["Falls"]
    ori = "EMSSTAT"
    inc_record = main.create_inc_record(time, inc_num, loc, nat, ori)
    assert inc_record == {
        "inc_time": time,
        "inc_number": inc_num,
        "inc_location": loc[0],
        "inc_nature": nat[0],
        "inc_ori": ori,
    }


def test_get_inc_details():
    inc_record = main.get_inc_details([record])
    assert len(inc_record) == 1
    assert inc_record[0] == {
        "inc_time": "23:30",
        "inc_number": "2024-00001511",
        "inc_location": "318 E HAYES ST",
        "inc_nature": "Falls",
        "inc_ori": "EMSSTAT",
    }


def test_create_db_success(mock_sqlite_connect):
    mock_connect, mock_connection, mock_cursor = mock_sqlite_connect

    db_conn = main.create_db()

    mock_connect.assert_called_once_with('resources/normanpd.db')
    mock_cursor.execute.assert_called()
    assert db_conn == mock_connection


def test_populate_db_success(mock_sqlite_connect):
    _, mock_connection, mock_cursor = mock_sqlite_connect
    inc_records = [
        {"inc_time": "12:00", "inc_number": "2024-00000872", "inc_location": "1307 BEVERLY HILLS ST", "inc_nature": "Public Assist", "inc_ori": "14005"},
        {"inc_time": "13:00", "inc_number": "2024-00000871", "inc_location": "27 WILLS MT", "inc_nature": "Arrest", "inc_ori": "4665"}
    ]

    main.populate_db(mock_connection, inc_records)

    assert mock_cursor.execute.call_count == len(inc_records)
    mock_connection.commit.assert_called_once()


def test_create_db_exception(mock_sqlite_connect):
    mock_connect, _, mock_cursor = mock_sqlite_connect
    mock_cursor.execute.side_effect = Exception("Mocked exception")

    db_conn = main.create_db()
    assert db_conn is not None


def test_populate_db_exception(mock_sqlite_connect):
    _, mock_connection, mock_cursor = mock_sqlite_connect
    mock_cursor.execute.side_effect = Exception("Mocked exception")
    inc_records = [{"inc_time": "12:00", "inc_number": "2024-00000872", "inc_location": "1307 BEVERLY HILLS ST", "inc_nature": "Public Assist", "inc_ori": "14005"}]
    main.populate_db(mock_connection, inc_records)
    mock_connection.commit.assert_not_called()


def test_status_with_records(mock_db_connection, mock_db_cursor):
    mock_db_cursor.fetchall.return_value = [("Nature1", 2), ("", 1), ("Nature2", 3)]

    with patch('builtins.print') as mock_print:
        main.status(mock_db_connection)
        mock_print.assert_any_call("Nature1|2")
        mock_print.assert_any_call("Nature2|3")
        mock_print.assert_any_call("|1")


def test_status_no_records(mock_db_connection, mock_db_cursor):
    mock_db_cursor.fetchall.return_value = []
    with patch('builtins.print') as mock_print:
        main.status(mock_db_connection)
        mock_print.assert_not_called()


def test_status_closes_cursor_on_exception(mock_db_connection, mock_db_cursor):
    # Simulate an exception to test cursor closure in the finally block
    mock_db_cursor.execute.side_effect = Exception("Mocked exception")

    with patch('builtins.print'):
        main.status(mock_db_connection)

    mock_db_cursor.close.assert_called_once()
