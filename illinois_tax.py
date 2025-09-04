def compute_illinois_tax(
    adjusted_income_il,
    fed_taxable_income,
    fed_taxed_retirement,
    capital_loss_carryover=0.0,
    resident_tax_credit=0.0
):
    # Extract IL-taxable sources
    dividends = adjusted_income_il.get("Dividends", 0.0)
    interest = adjusted_income_il.get("Interest", 0.0)
    annuities = adjusted_income_il.get("Annuity", 0.0)
    net_capital = min(0.0, adjusted_income_il.get("Capital Gains", 0.0) + max(capital_loss_carryover, -3000.0))

    if not isinstance(adjusted_income_il, dict):
        raise TypeError("adjusted_income_il must be a dictionary")

    # Apply IL capital loss cap
    net_capital = min(0.0, adjusted_income_il.get("Capital Gains", 0.0) + max(capital_loss_carryover, -3000.0))

    # IL-taxable income calculation
    il_taxable_income = max(0.0, dividends + interest + annuities + net_capital)

    # IL tax calculation
    il_tax = round(il_taxable_income * 0.0495, 2)
    tax_due = max(0.0, il_tax - resident_tax_credit)
    effective_rate = round(tax_due / fed_taxable_income, 4) if fed_taxable_income else 0.0

    return {
        "il_taxable_income": il_taxable_income,
        "il_tax": il_tax,
        "resident_credit": resident_tax_credit,
        "tax_due": tax_due,
        "effective_rate": effective_rate
    }
