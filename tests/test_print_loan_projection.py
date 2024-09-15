"""Unit tests for the loan.print_loan_projection function."""

from decimal import Decimal as D

import loan
from loan import LoanProjection

# ignore=W291


def test_print_loan_projection(capfd):
    expected_output = """
Month   Interest Charged   Remaining Balance   
-----   ----------------   -----------------   
    1               4.00                1.00   
    2               5.00                2.00   
    3               6.00                3.00   

"""
    loan.print_loan_projection(
        LoanProjection(
            month_end_balance=(D("1.00"), D("2.00"), D("3.00")),
            monthly_interest_charged=(D("4.00"), D("5.00"), D("6.00")),
        )
    )
    assert capfd.readouterr().out == expected_output


def test_print_loan_projection_negative_balance(capfd):
    expected_output = """
Month   Interest Charged   Remaining Balance   
-----   ----------------   -----------------   
    1             123.22              400.45   
    2             211.76                2.99   
    3              33.20             -317.43   

"""
    loan.print_loan_projection(
        LoanProjection(
            month_end_balance=(D("400.45"), D("2.99"), D("-317.43")),
            monthly_interest_charged=(D("123.22"), D("211.76"), D("33.20")),
        )
    )
    assert capfd.readouterr().out == expected_output


def test_print_loan_projection_wide_balance_column(capfd):
    expected_output = """
Month   Interest Charged     Remaining Balance   
-----   ----------------     -----------------   
    1             123.23   5434934343434343.43   
    2             211.77                 55.20   

"""
    loan.print_loan_projection(
        LoanProjection(
            month_end_balance=(D("5434934343434343.43"), D("55.20")),
            monthly_interest_charged=(D("123.23"), D("211.77")),
        )
    )
    assert capfd.readouterr().out == expected_output


def test_print_loan_projection_wide_negative_balance_column(capfd):
    expected_output = """
Month   Interest Charged      Remaining Balance   
-----   ----------------      -----------------   
    1             123.23   -5434934343434343.43   
    2             211.77                  55.20   

"""
    loan.print_loan_projection(
        LoanProjection(
            month_end_balance=(D("-5434934343434343.43"), D("55.20")),
            monthly_interest_charged=(D("123.23"), D("211.77")),
        )
    )
    assert capfd.readouterr().out == expected_output
