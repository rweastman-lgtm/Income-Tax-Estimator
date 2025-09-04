# federal_tax.py

def estimate_tax(income_sources, age_1, age_2, capital_loss_carryover):
    # Placeholder for actual bracket logic
    taxable_income = sum(income_sources.values()) - 29500  # Example standard deduction
    tax_due = taxable_income * 0.22  # Example flat rate for simplicity
    return {
        "Taxable Income": max(taxable_income, 0),
        "Federal Tax": max(tax_due, 0)
    }

def compute_federal_tax(income_sources, age_1, age_2, capital_loss_carryover):
    adjusted_income = income_sources.copy()
    fed_capital_loss = min(capital_loss_carryover, 3000)
    results = estimate_tax(adjusted_income, age_1, age_2, fed_capital_loss)
    results["Taxed Retirement"] = (
        income_sources.get("Social Security", 0) +
        income_sources.get("Pension", 0) +
        income_sources.get("IRA Withdrawals", 0) +
        income_sources.get("Annuity", 0)
    )
    return results

