# illinois_tax.py

def apply_pso_credit(income_sources, is_pso_eligible):
    if is_pso_eligible:
        income_sources["Pension"] = max(income_sources.get("Pension", 0) - 3000, 0)
    return income_sources

def compute_illinois_tax(income_sources, fed_taxable_income, fed_taxed_retirement, taxable_social_security, capital_loss_carryover, resident_tax_credit):
    # Step 1: Include IL-taxable income sources
    il_base_income = (
        income_sources.get("Qualified Dividends", 0) +
        income_sources.get("Interest", 0) +
        income_sources.get("Annuity", 0)  # Include if non-qualified
    )

    # Step 2: Subtract capital loss carryover (up to $3,000)
    il_base_income -= min(capital_loss_carryover, 3000)

    # Step 3: Subtract Illinois standard deduction ($2,775 per filer)
    il_base_income -= 2 * 2775  # = $5,550

    # Step 4: Compute tax due
    il_tax_due = max(0, il_base_income * 0.0495)

    # Step 5: Apply real estate tax credit (up to $300)
    il_tax_due -= min(resident_tax_credit, 300)

    return {
        "IL Taxable Income": round(il_base_income, 2),
        "Illinois Tax": round(il_tax_due, 2)
    }
