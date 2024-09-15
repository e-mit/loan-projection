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


def approx_summed_value(value):
    """Test approximate equality to the nearest £0.01, or 0.01%.

    This is suitable for testing values that are calculated from
    rounded values (which should not be used for accurate purposes).
    """
    return pytest.approx(value, abs=D("0.01"), rel=D("0.0001"))


def assert_monthly_balance_consistency(
    principal, monthly_payment, monthly_interest_charged, month_end_balance
):
    """Test that each new balance depends on previous balance, payment, and interest.

    This uses exact equality testing, without approx(), to ensure no rounding errors.
    """
    previous_balance = principal
    for month_index, end_balance in enumerate(month_end_balance):
        expected_month_end_balance = (
            previous_balance - monthly_payment + monthly_interest_charged[month_index]
        )
        assert expected_month_end_balance == end_balance
        previous_balance = end_balance


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
    total_charged = term_months * monthly_payment
    assert (
        sum(projection.monthly_interest_charged) + principal
    ) == approx_website_value(total_charged)
    assert_monthly_balance_consistency(
        principal,
        monthly_payment,
        projection.monthly_interest_charged,
        projection.month_end_balance,
    )


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
    total_charged = term_months * monthly_payment
    assert (
        sum(projection.monthly_interest_charged) + principal
    ) == approx_website_value(total_charged)
    assert_monthly_balance_consistency(
        principal,
        monthly_payment,
        projection.monthly_interest_charged,
        projection.month_end_balance,
    )


def test_mortgage_barclays_schedule():
    """Values from Barclays capital repayment mortgage calculator website."""
    principal = D(100000)
    interest_rate_annual_percentage = D("4.05")
    term_months = 63
    monthly_payment = D("530.60")
    year_end_balance = [
        D("97613.27"),
        D("95153.56"),
        D("92592.88"),
        D("89929.54"),
        D("87150.4"),
    ]
    end_balance = D("86436.14")  # After 63 months vs 60 for year_end_balance[-1]

    projection = loan.loan_projection(
        principal,
        interest_rate_annual_percentage,
        term_months,
        monthly_payment,
        loan.InterestType.NOMINAL,
    )

    assert len(projection.month_end_balance) == term_months
    assert len(projection.monthly_interest_charged) == term_months
    assert projection.month_end_balance[-1] == approx_website_value(end_balance)
    for year_index, month_index in enumerate(range(11, 63, 12)):
        assert projection.month_end_balance[month_index] == approx_website_value(
            year_end_balance[year_index]
        )
    assert_monthly_balance_consistency(
        principal,
        monthly_payment,
        projection.monthly_interest_charged,
        projection.month_end_balance,
    )


@pytest.mark.parametrize(
    "interest_type", [loan.InterestType.NOMINAL, loan.InterestType.EFFECTIVE]
)
def test_zero_interest(interest_type):
    principal = D(4656557)
    interest_rate_annual_percentage = D(0)
    term_months = 34
    monthly_payment = D("921.95")

    projection = loan.loan_projection(
        principal,
        interest_rate_annual_percentage,
        term_months,
        monthly_payment,
        interest_type,
    )

    assert set(projection.monthly_interest_charged) == {0}
    assert len(projection.monthly_interest_charged) == term_months
    assert len(projection.month_end_balance) == term_months
    assert projection.month_end_balance == tuple(
        principal - (monthly_payment * (i + 1)) for i in range(term_months)
    )
    assert_monthly_balance_consistency(
        principal,
        monthly_payment,
        projection.monthly_interest_charged,
        projection.month_end_balance,
    )


@pytest.mark.parametrize(
    "interest_type", [loan.InterestType.NOMINAL, loan.InterestType.EFFECTIVE]
)
def test_zero_interest_zero_payment(interest_type):
    principal = D(4656557)
    interest_rate_annual_percentage = D(0)
    term_months = 34
    monthly_payment = D(0)

    projection = loan.loan_projection(
        principal,
        interest_rate_annual_percentage,
        term_months,
        monthly_payment,
        interest_type,
    )

    assert set(projection.monthly_interest_charged) == {0}
    assert set(projection.month_end_balance) == {principal}
    assert len(projection.monthly_interest_charged) == term_months
    assert len(projection.month_end_balance) == term_months
    assert_monthly_balance_consistency(
        principal,
        monthly_payment,
        projection.monthly_interest_charged,
        projection.month_end_balance,
    )


def test_zero_payments_nominal_interest():
    principal = D(100000)
    interest_rate_annual_percentage = D("5.5")
    term_months = 12
    monthly_payment = D(0)

    projection = loan.loan_projection(
        principal,
        interest_rate_annual_percentage,
        term_months,
        monthly_payment,
        loan.InterestType.NOMINAL,
    )

    assert len(projection.monthly_interest_charged) == term_months
    assert len(projection.month_end_balance) == term_months
    assert projection.month_end_balance[-1] == approx_summed_value(
        principal + sum(projection.monthly_interest_charged)
    )
    for month in range(term_months):
        assert projection.month_end_balance[month] == approx_summed_value(
            principal + sum(projection.monthly_interest_charged[: month + 1])
        )
    assert_monthly_balance_consistency(
        principal,
        monthly_payment,
        projection.monthly_interest_charged,
        projection.month_end_balance,
    )


def test_zero_payments_effective_interest():
    principal = D(100000)
    interest_rate_annual_percentage = D("5.5")
    term_months = 12
    monthly_payment = D(0)

    projection = loan.loan_projection(
        principal,
        interest_rate_annual_percentage,
        term_months,
        monthly_payment,
        loan.InterestType.EFFECTIVE,
    )

    assert len(projection.monthly_interest_charged) == term_months
    assert len(projection.month_end_balance) == term_months
    assert projection.month_end_balance[-1] == principal + sum(
        projection.monthly_interest_charged
    )
    for i, bal in enumerate(projection.month_end_balance):
        assert bal == approx_summed_value(
            principal + sum(projection.monthly_interest_charged[: i + 1])
        )
    assert_monthly_balance_consistency(
        principal,
        monthly_payment,
        projection.monthly_interest_charged,
        projection.month_end_balance,
    )
