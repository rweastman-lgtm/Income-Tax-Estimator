# Tax_estimator_app.py

import streamlit as st
from federal_tax import estimate_tax
from illinois_tax import apply_pso_credit, compute_illinois_tax

st.title("💸 IRA Conversion & Tax Estimator")
st.caption("For Married Filing Jointly | Ages 64 & 60")

age_1 = st.number_input("Age of Taxpayer 1", value=64)
age_2 = st.number_input("Age of Taxpayer 2", value=60)

income_sources = {
    "IRA Withdrawals": st.number_input("IRA Withdrawals", value=30000),
    "Roth Conversions": st.number_input("Roth Conversions", value=20000),
    "Pension": st.number_input("Pension", value=25000),
    "TSP": st.number_input("TSP", value=15000),
    "Annuity": st.number_input("Annuity", value=10000),
    "Interest": st.number_input("Interest", value=3000),
    "Ordinary Dividends": st.number_input("Ordinary Dividends", value=0),
    "Qualified Dividends": st.number_input("Qualified Dividends", value=5000),
    "Capital Gains": st.number_input("Capital Gains", value=10000),
    "Social Security": st.number_input("Social Security", value=40000)
}

capital_loss_carryover = st.number_input("Capital Loss Carryover", value=0)
resident_tax_credit = float(st.number_input("Resident Tax Credit", value=0))
is_pso_eligible = st.checkbox("Eligible for PSO Credit")
is_illinois_resident = st.checkbox("Illinois Resident")

# Scoped copies
adjusted_income_fed = income_sources.copy()
adjusted_income_il = apply_pso_credit(income_sources.copy(), is_pso_eligible)

# Compute taxes
fed_results = estimate_tax(adjusted_income_fed, age_1, age_2, min(capital_loss_carryover, 3000))
fed_taxed_retirement = (
    income_sources.get("Social Security", 0) +
    income_sources.get("Pension", 0) +
    income_sources.get("IRA Withdrawals", 0) +
    income_sources.get("Annuity", 0) +
    income_sources.get("Roth Conversions", 0) +
    income_sources.get("TSP", 0)
)

il_results = compute_illinois_tax(
    income_sources,
    fed_taxable_income=fed_results["Taxable Income"],
    fed_taxed_retirement=fed_taxed_retirement,
    taxable_social_security=fed_results["Taxed Social Security"],
    capital_loss_carryover=capital_loss_carryover,
    resident_tax_credit=resident_tax_credit
)

# Display
st.subheader("📊 Federal Tax Summary")
for k, v in fed_results.items():
    if k not in ["Bracket Breakdown", "CG Breakdown"]:
        st.write(f"**{k}:** ${v:,.2f}" if isinstance(v, (int, float)) else f"**{k}:** {v}")

st.write(f"Federally Taxed Retirement (excluded by IL): ${fed_taxed_retirement:,.2f}")
st.subheader("Illinois Income Tax")
st.write(f"IL Taxable Income: ${il_results['IL Taxable Income']:,.2f}")
st.write(f"IL Tax Due: ${il_results['Illinois Tax']:,.2f}")
