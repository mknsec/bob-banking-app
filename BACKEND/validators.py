"""
validators.py — Input validation helpers for the Banking application.

All route handlers call validate_amount() before touching the database,
keeping the validation rules defined in one place.
"""


def validate_amount(raw_value):
    """
    Validate a raw string amount submitted from a deposit or withdrawal form.

    Checks applied in order:
    1. Value is present (not None / empty string)
    2. Value is numeric (convertible to float)
    3. Value is positive (> 0)
    4. Value has at most 2 decimal places

    Returns:
        (float, None)       — on success: the parsed amount and no error
        (None, str)         — on failure: None and a human-readable error message
    """
    # --- 1. Presence check ------------------------------------------------
    if raw_value is None or str(raw_value).strip() == "":
        return None, "Amount is required."

    # --- 2. Numeric check -------------------------------------------------
    try:
        amount = float(raw_value)
    except (ValueError, TypeError):
        return None, "Amount must be a valid number."

    # --- 3. Positive check ------------------------------------------------
    if amount <= 0:
        return None, "Amount must be greater than zero."

    # --- 4. Decimal precision check ---------------------------------------
    # Round-trip through string representation to count decimal places.
    str_amount = str(raw_value).strip()
    if "." in str_amount:
        decimal_part = str_amount.split(".")[1]
        if len(decimal_part) > 2:
            return None, "Amount must have at most 2 decimal places."

    return amount, None
