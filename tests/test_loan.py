"""Unit tests for the loan projection function."""

from decimal import Decimal as D

import pytest

import loan


def approx_website_value(value):
    """Test approximate equality to the nearest £0.4, or 0.05%.

    This is suitable for testing values from website calculators which
    have unknown rounding rules or accuracy requirements.
    """
    return pytest.approx(value, abs=D("0.4"), rel=D("0.0005"))


@pytest.mark.parametrize(
    "principal, interest_rate_annual_percentage, term_months, monthly_payment",
    [
        (D(10000), D("6.5"), 24, D("444.62")),  # Barclays
        (D(35000), D("7.8"), 55, D("754.52")),  # Tesco
        (D(10000), D("6.1"), 60, D("193.03")),  # Nationwide
    ],
)
def test_loan_website_calculator_values(
    principal, interest_rate_annual_percentage, term_months, monthly_payment
):
    """Values from personal loan calculators on bank websites."""
    projection = loan.loan_projection(
        principal,
        interest_rate_annual_percentage,
        term_months,
        monthly_payment,
        loan.InterestType.EFFECTIVE,
    )

    assert len(projection.month_end_balance) == term_months
    assert len(projection.monthly_interest_charged) == term_months
    assert projection.month_end_balance[-1] == approx_website_value(0)


@pytest.mark.parametrize(
    "principal, interest_rate_annual_percentage, term_months, monthly_payment",
    [
        (D(100000), D("4.5"), 36, D("2974.69")),  # Nationwide
        (D(50000), D("4.05"), 60, D("921.95")),  # Barclays
    ],
)
def test_mortgage_website_calculator_values(
    principal, interest_rate_annual_percentage, term_months, monthly_payment
):
    """Values from capital repayment mortgage calculators on bank websites."""
    projection = loan.loan_projection(
        principal,
        interest_rate_annual_percentage,
        term_months,
        monthly_payment,
        loan.InterestType.NOMINAL,
    )

    assert len(projection.month_end_balance) == term_months
    assert len(projection.monthly_interest_charged) == term_months
    assert projection.month_end_balance[-1] == approx_website_value(0)
