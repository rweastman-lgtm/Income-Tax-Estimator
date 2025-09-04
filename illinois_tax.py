# illinois_tax.py

def apply_pso_credit(income_sources, is_pso_eligible):
    if is_pso_eligible:
        income_sources["Pension"] = max(income_sources.get("Pension", 0) - 6000, 0)
    return income_sources

def compute_illinois_tax(income_sources, fed_taxable_income, fed_taxed_retirement, taxable_social_security, capital_loss_carryover, resident_tax_credit):

    # Add back federally taxed retirement income that Illinois excludes
    il_taxable_income += (
        income_sources.get("IRA Withdrawals", 0) +
        income_sources.get("Roth Conversions", 0) +
        income_sources.get("Pension", 0) +
        income_sources.get("TSP", 0) +
        income_sources.get("Annuity", 0) +
        taxable_social_security
    )

    il_tax_due = max(il_taxable_income * 0.0495, 0)

    return {
        "IL Taxable Income": il_taxable_income,
        "Illinois Tax": il_tax_due
    }

st.write("🔍 IL Taxable Income:", il_results["IL Taxable Income"])
st.write("💰 IL Tax Due:", il_results["Illinois Tax"])
