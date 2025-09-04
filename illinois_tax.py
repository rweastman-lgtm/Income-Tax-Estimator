def compute_illinois_tax(
    adjusted_income,
    fed_taxable_income,
    fed_taxed_retirement,
    capital_loss_carryover=0.0,
    resident_tax_credit=0.0
):
    """
    Calculates Illinois income tax based on IL-taxable sources only.

    Args:
        dividends (float): Taxable dividends.
        interest (float): Taxable interest.
        capital_gains (float): Realized capital gains.
        capital_losses (float): Realized capital losses (max $3,000 deduction).
        annuities (float): Non-retirement annuity income.
        resident_tax_credit (float): Credit for taxes paid to other states.

    Returns:
        dict: {
            'il_taxable_income': float,
            'il_tax': float,
            'resident_credit': float,
            'tax_due': float,
            'effective_rate': float
        }
    """
   # Extract IL-taxable sources from adjusted income
dividends = adjusted_income.get("Dividends", 0.0)
interest = adjusted_income.get("Interest", 0.0)
annuities = adjusted_income.get("Annuity", 0.0)

# Apply IL capital loss cap
net_capital = min(0.0, adjusted_income.get("Capital Gains", 0.0) + max(capital_loss_carryover, -3000.0))

il_taxable_income = max(0.0, dividends + interest + annuities + net_capital)

    il_taxable_income = max(0.0, dividends + interest + annuities + net_capital)
    il_tax = round(il_taxable_income * 0.0495, 2)
    tax_due = max(0.0, il_tax - resident_tax_credit)
    effective_rate = round(tax_due / il_taxable_income, 4) if il_taxable_income else 0.0

    return {
        "il_taxable_income": il_taxable_income,
        "il_tax": il_tax,
        "resident_credit": resident_tax_credit,
        "tax_due": tax_due,
        "effective_rate": effective_rate
    }

