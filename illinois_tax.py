# illinois_tax.py

def apply_pso_credit(income_sources, is_pso_eligible):
    if is_pso_eligible:
        income_sources["Pension"] = max(income_sources.get("Pension", 0) - 6000, 0)
    return income_sources

def compute_illinois_tax(income_sources, fed_taxable_income, fed_taxed_retirement, taxable_social_security, capital_loss_carryover, resident_tax_credit):
    # Start with federal taxable income
    il_taxable_income = fed_taxable_income

    # Add back federally taxed retirement income that Illinois excludes
    il_taxable_income += (
        income_sources.get("IRA Withdrawals",
