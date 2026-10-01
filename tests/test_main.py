from unittest.mock import patch

from main import main


def test_main_uses_postgresql_by_default():
    with patch("main.run_SupplyNode") as mock_run:
        with patch("sys.argv", ["main.py"]):
            main()

        mock_run.assert_called_once_with()

def test_main_uses_excel_when_requested():
    with patch("main.run_SupplyNode") as mock_run:
        with patch("sys.argv", ["main.py", "--excel"]):
            main()

        mock_run.assert_called_once_with(
            "supplynode/data/sample_data.xlsx"
        )