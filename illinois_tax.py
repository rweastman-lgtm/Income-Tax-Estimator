# illinois_tax.py

def apply_pso_credit(income_sources, is_pso_eligible):
    if is_pso_eligible:
        income_sources["Pension"] = max(income_sources.get("Pension", 0) - 6000, 0)
    return income_sources

def compute_illinois_tax(income_sources, fed_taxable_income, fed_taxed_retirement, taxable_social_security, capital_loss_carryover, resident_tax_credit):
    # Step 1: Compute total income
    total_income = sum(income_sources.values())

    # Step 2: Subtract federally taxed retirement income that Illinois excludes
    il_base_income = max(0, total_income - fed_taxed_retirement)

    il_base_income += income_sources.get("Annuity", 0)
    
    # Step 3: Subtract capital loss carryover (up to $3,000)
    il_base_income -= min(capital_loss_carryover, 3000)

    # Step 4: Subtract personal exemptions ($2,425 per filer)
    personal_exemption = 2 * 2425
    il_base_income -= personal_exemption

    # Step 5: Compute tax due
    il_tax_due = max(0, il_base_income * 0.0495)

    # Step 6: Apply real estate tax credit (up to $300)
    il_tax_due = max(0, il_tax_due - min(resident_tax_credit, 300))

    return {
        "IL Taxable Income": round(il_base_income, 2),
        "Illinois Tax": round(il_tax_due, 2)
    }
