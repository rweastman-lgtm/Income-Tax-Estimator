# Create scoped copy for federal
adjusted_income_fed = income_sources.copy()

# Decouple capital loss logic
fed_capital_loss = min(capital_loss_carryover, 3000)

# Compute federal taxes
results = estimate_tax(
    adjusted_income_fed,
    age_1=age_1,
    age_2=age_2,
    capital_loss_carryover=fed_capital_loss
)

# Extract federal outputs
fed_taxable_income = results.get("Taxable Income", 0)
fed_taxed_retirement = (
    income_sources.get("Social Security", 0) +
    income_sources.get("Pension", 0) +
    income_sources.get("IRA Withdrawals", 0) +
    income_sources.get("Annuity", 0)
)
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
