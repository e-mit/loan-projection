# Loan-Projection

![tests](https://github.com/e-mit/loan-projection/actions/workflows/tests.yml/badge.svg)
![coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/e-mit/9df92671b4e2859b1e75cf762121b73f/raw/loan-projection.json)
![mypy](https://github.com/e-mit/loan-projection/actions/workflows/mypy.yml/badge.svg)
![pylint](https://github.com/e-mit/loan-projection/actions/workflows/pylint.yml/badge.svg)
![pyright](https://github.com/e-mit/loan-projection/actions/workflows/pyright.yml/badge.svg)
![ruff-lint](https://github.com/e-mit/loan-projection/actions/workflows/ruff-lint.yml/badge.svg)
![ruff-format](https://github.com/e-mit/loan-projection/actions/workflows/ruff-format.yml/badge.svg)

A Python function to calculate the projected monthly balance on a loan.

The function displays the interest charged and the remaining balance each month, for the duration of the loan.


## Usage instructions

Import the ```loan``` module and call the ```loan_projection``` function. For example:

```
from decimal import Decimal

import loan

loan.loan_projection(
    principal=Decimal("100000"),
    interest_rate_annual_percentage=Decimal("4.05"),
    term_months=4,
    monthly_payment=Decimal("1530.60"),
    interest_type=loan.InterestType.NOMINAL,
    print_table=True
)

Month   Interest Charged   Remaining Balance
-----   ----------------   -----------------
    1             337.50            98806.90
    2             333.47            97609.77
    3             329.44            96408.61
    4             325.38            95203.39
```

No packages other than the Python standard library are used. Python version 3.10 or greater is required.


## Testing and development

1. Create a virtual environment and install testing packages with:
   ```python -m venv venv && source venv/bin/activate && pip install -r requirements-test.txt```
2. Ensure the bash script has execute permissions: ```chmod +x tests.sh```
3. Run all tests, linting, coverage report, type checking and format checking with ```./tests.sh```
4. Run just the unit tests with ```pytest```
5. Apply formatting and import sorting with ```ruff check --select I --fix && ruff format```


## Interest calculation

The ```interest_type``` function argument can take two enum values: NOMINAL and EFFECTIVE. These determine how the specified annual percentage interest rate, $a$, is converted to a monthly rate, $r$, by the following:

Nominal: $r = a/1200$

Effective: $r = (1 + a/100)^{1/12} - 1$

The monthly rate is used to calculate the loan balance $B(n)$ remaining after an integer number of months $n$ according to:

$B(n) = P(1 + r)^n - M\frac{(1 + r)^n - 1}{r}$

Where $P$ is the loan principal and $M$ is the fixed monthly payment.

#### Compounding

For either ```interest_type```, any monthly interest not paid by the monthly payment is added to the principal and then accrues interest in the next month. This could be changed to optionally allow "simple interest" without this monthly compounding.


## Output values

- The function returns an immutable ```LoanProjection``` object. This contains two tuples: ```month_end_balance``` and ```monthly_interest_charged```. If argument ```print_table``` is true, these tuples are also output to the terminal as a table.
- Each element of the output tuples corresponds to one month of the loan term, starting at the end of the first month.

## Rounding procedure

- All calculations are performed using decimal arithmetic with 28 significant figures, while output values are decimals with two decimal places for display purposes. This can be changed by setting ```loan.DECIMAL_PLACES_IO```.
- The output monthly balances are rounded using the "round half even" method, though this can be changed by setting ```loan.OUTPUT_ROUNDING_METHOD``` to a different method flag.
- The rounded balances are used to create the monthly interest output/display values, so that for each month the outputs for opening balance, interest and payment sum exactly to the closing balance.
