"""Unit tests for loan projection function errors."""

from decimal import Decimal as D

import pytest

import loan

too_many_decimal_places = D("1000.1" + "1" * loan.DECIMAL_PLACES_IO)


@pytest.mark.parametrize(
    "interest_type", [loan.InterestType.NOMINAL, loan.InterestType.EFFECTIVE]
)
@pytest.mark.parametrize("principal", [D("0"), D("-500"), too_many_decimal_places])
def test_principal_value_error(interest_type, principal):
    interest_rate_annual_percentage = D("5.5")
    term_months = 15
    monthly_payment = D(120)
    with pytest.raises(ValueError):
        loan.loan_projection(
            principal,
            interest_rate_annual_percentage,
            term_months,
            monthly_payment,
            interest_type,
        )


@pytest.mark.parametrize(
    "interest_type", [loan.InterestType.NOMINAL, loan.InterestType.EFFECTIVE]
)
@pytest.mark.parametrize("monthly_payment", [D(-200), too_many_decimal_places])
def test_payment_value_error(interest_type, monthly_payment):
    principal = D(10000)
    interest_rate_annual_percentage = D("5.5")
    term_months = 10
    with pytest.raises(ValueError):
        loan.loan_projection(
            principal,
            interest_rate_annual_percentage,
            term_months,
            monthly_payment,
            interest_type,
        )


@pytest.mark.parametrize(
    "interest_type", [loan.InterestType.NOMINAL, loan.InterestType.EFFECTIVE]
)
@pytest.mark.parametrize("interest_rate_annual_percentage", [D("-2.5")])
def test_negative_interest_rate(interest_type, interest_rate_annual_percentage):
    principal = D(10000)
    monthly_payment = D("523.50")
    term_months = 10
    with pytest.raises(ValueError):
        loan.loan_projection(
            principal,
            interest_rate_annual_percentage,
            term_months,
            monthly_payment,
            interest_type,
        )


@pytest.mark.parametrize(
    "interest_type", [loan.InterestType.NOMINAL, loan.InterestType.EFFECTIVE]
)
def test_fractional_term(interest_type):
    principal = D(100000)
    interest_rate_annual_percentage = D("5.5")
    term_months = 10.5
    monthly_payment = D(120)
    with pytest.raises(TypeError):
        loan.loan_projection(
            principal,
            interest_rate_annual_percentage,
            term_months,  # type: ignore
            monthly_payment,
            interest_type,
        )


def test_unknown_interest_type():
    principal = D(100000)
    interest_rate_annual_percentage = D("5.5")
    term_months = 10
    monthly_payment = D(120)
    with pytest.raises(ValueError):
        loan.loan_projection(
            principal,
            interest_rate_annual_percentage,
            term_months,
            monthly_payment,
            interest_type=7678988,  # type: ignore
        )
