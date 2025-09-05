# illinois_tax.py

def apply_pso_credit(income_sources, is_pso_eligible):
    if is_pso_eligible:
        income_sources["Pension"] = max(income_sources.get("Pension", 0) - 6000, 0)
    return income_sources

def compute_illinois_tax(income_sources, fed_taxable_income, fed_taxed_retirement, taxable_social_security, capital_loss_carryover, resident_tax_credit):
    # Compute total income from all sources
    total_income = sum(income_sources.values())

    # Subtract federally taxed retirement income that Illinois excludes
    il_taxable_income = max(0, total_income - fed_taxed_retirement)

    # Apply flat tax rate
    il_tax_due = round(il_taxable_income * 0.0495, 2)

    return {
        "IL Taxable Income": il_taxable_income,
        "Illinois Tax": il_tax_due
    }
