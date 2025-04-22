from src.reports import log_reports_to_file


def test_log_reports_to_file():
    @log_reports_to_file("test.json")
