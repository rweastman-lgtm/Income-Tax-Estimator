# illinois_tax.py

def apply_pso_credit(income_sources, is_pso_eligible):
    if is_pso_eligible:
        income_sources["Pension"] = max(income_sources.get("Pension", 0) - 6000, 0)
    return income_sources

def compute_illinois_tax(income_sources, fed_taxable_income, fed_taxed_retirement, capital_loss_carryover, resident_tax_credit):
    il_taxable_income = fed_taxable_income - fed_taxed_retirement
    il_taxable_income = max(il_taxable_income, 0)
    il_tax_due = il_taxable_income * 0.0495  # Illinois flat rate
    il_tax_due -= resident_tax_credit
    return {
        "IL Taxable Income": il_taxable_income,
        "Illinois Tax": max(il_tax_due, 0)
    }
