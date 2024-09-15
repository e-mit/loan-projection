# Loan-Projection

A Python function to calculate the projected monthly balance on a loan.

The function displays the interest charged and the remaining balance each month, for the duration of the loan.



## Testing and development

1. Create a virtual environment and install testing packages with:
   ```python -m venv venv && source venv/bin/activate && pip install -r requirements-test.txt```
2. Ensure the bash script has execute permissions: ```chmod +x tests.sh```
3. Run all tests, linting, coverage report, type checking and format checking with ```./tests.sh```
4. Run just the unit tests with ```pytest```
5. Apply formatting and import sorting with ```ruff check --select I --fix && ruff format```
