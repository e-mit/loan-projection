"""loan.py: functions for calculating loan balance and interest."""

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN
from decimal import Decimal as Dec
from enum import Enum, auto
from typing import Final

OUTPUT_ROUNDING_METHOD: Final[str] = ROUND_HALF_EVEN
DECIMAL_PLACES_IO: Final[int] = 2
MONTHS_IN_ONE_YEAR: Final[int] = 12


def round_decimal(value: Dec) -> Dec:
    """Apply rounding procedure to a Decimal number."""
    return value.quantize(Dec(10) ** -DECIMAL_PLACES_IO, OUTPUT_ROUNDING_METHOD)


@dataclass(frozen=True)
class LoanProjection:
    """The result of a loan projection calculation."""

    month_end_balance: tuple[Dec, ...]
    monthly_interest_charged: tuple[Dec, ...]

    def __post_init__(self):
        if len(self.month_end_balance) != len(self.monthly_interest_charged):
            raise ValueError(
                f"Data inputs have unequal length: {len(self.month_end_balance)} "
                f"and {len(self.monthly_interest_charged)}."
            )


def print_loan_projection(projection: LoanProjection):
    """Print a table to stdout showing loan interest and balance for each month."""
    month = {
        "title": "Month",
        "data": [1 + x for x in range(len(projection.month_end_balance))],
    }
    interest = {
        "title": "Interest Charged",
        "data": projection.monthly_interest_charged,
    }
    balance = {"title": "Remaining Balance", "data": projection.month_end_balance}
    spacer = "   "

    print()
    columns = [month, interest, balance]
    for v in columns:
        max_value_width = len(str(max(v["data"], key=abs)))  # type: ignore
        v["width"] = max(max_value_width, len(v["title"]))  # type: ignore
        print(f"{v['title']:>{v['width']}}{spacer}", end="")
    print()
    for v in columns:
        print(f"{'-' * len(v['title']):>{v['width']}}{spacer}", end="")
    print()
    for i in range(len(projection.month_end_balance)):
        for v in columns:
            print(f"{v['data'][i]:>{v['width']}}{spacer}", end="")
        print()
    print()


class InterestType(Enum):
    """Indicates the method of annual to monthly interest rate conversion."""

    EFFECTIVE = auto()
    NOMINAL = auto()


def loan_balance(
    principal: Dec, monthly_rate: Dec, months: int, monthly_payment: Dec
) -> Dec:
    """Calculate the remaining balance on a loan after a given number of months.

    This function computes the remaining loan balance using the initial principal,
    the monthly interest rate, the number of months of payments, and the monthly
    payment amount.

    Args:
        principal (Decimal): The loan principal (initial balance).
        monthly_rate (Decimal): The fractional monthly interest rate (e.g. 0.05 for 5%).
        months (int): The number of months that have passed since the loan began.
        monthly_payment (Decimal): The fixed monthly payment amount.

    Returns:
        Decimal: The remaining balance on the loan after the specified number of months.

    """
    return (
        principal * ((monthly_rate + 1) ** months)
        - monthly_payment * (((monthly_rate + 1) ** months) - 1) / monthly_rate
    )


def monthly_interest_rate(
    interest_rate_annual_percentage: Dec, interest_type: InterestType
) -> Dec:
    """Calculate the periodic interest rate from the annual rate."""
    if interest_type == InterestType.EFFECTIVE:
        return (Dec(1) + (interest_rate_annual_percentage / Dec(100))) ** (
            Dec(1) / Dec(MONTHS_IN_ONE_YEAR)
        ) - Dec(1)
    if interest_type == InterestType.NOMINAL:
        return interest_rate_annual_percentage / Dec(MONTHS_IN_ONE_YEAR * 100)
    raise ValueError("Unknown interest rate type.")


def loan_projection(  # pylint: disable=R0913
    principal: Dec,
    interest_rate_annual_percentage: Dec,
    term_months: int,
    monthly_payment: Dec,
    interest_type: InterestType,
    print_table: bool = False,
) -> LoanProjection:
    """Calculate the projected monthly balance and interest for a loan."""
    for var in [
        "principal",
        "interest_rate_annual_percentage",
        "term_months",
        "monthly_payment",
    ]:
        if locals()[var] < 0:
            raise ValueError(f"Argument '{var}' cannot be negative.")
    for var in ["term_months", "principal"]:
        if locals()[var] == 0:
            raise ValueError(f"Argument '{var}' cannot be zero.")
    for var in ["principal", "monthly_payment"]:
        if -locals()[var].as_tuple().exponent > DECIMAL_PLACES_IO:
            raise ValueError(
                f"Argument '{var}' cannot have more than {DECIMAL_PLACES_IO} "
                f"decimal places, but got {-locals()[var].as_tuple().exponent}."
            )
    if not isinstance(term_months, int):
        raise TypeError(
            "Argument 'term_months' must be an integer, "
            f"but got {type(term_months).__name__}."
        )

    if interest_rate_annual_percentage == 0:
        month_end_balance = [
            principal - monthly_payment * (n + 1) for n in range(term_months)
        ]
    else:
        monthly_rate = monthly_interest_rate(
            interest_rate_annual_percentage, interest_type
        )
        month_end_balance = [
            loan_balance(principal, monthly_rate, n + 1, monthly_payment)
            for n in range(term_months)
        ]

    # Truncate if balance goes negative or zero.
    stop_index = next(
        (i + 1 for i, bal in enumerate(month_end_balance) if bal <= 0), term_months
    )
    month_end_balance = month_end_balance[:stop_index]

    # Round the balances for output/display.
    month_end_balance = [round_decimal(x) for x in month_end_balance]

    # Calculate the output/display interest amounts.
    month_start_balance = [principal] + month_end_balance[:-1]
    monthly_interest_charged = [
        end_bal - start_bal + monthly_payment
        for end_bal, start_bal in zip(
            month_end_balance, month_start_balance, strict=True
        )
    ]

    projection = LoanProjection(
        month_end_balance=tuple(month_end_balance),
        monthly_interest_charged=tuple(monthly_interest_charged),
    )
    if print_table:
        print_loan_projection(projection)
    return projection
