# tax_estimator_app.py
import streamlit as st

def apply_pso_credit(income_dict, is_pso_eligible):
    """Applies PSO exclusion if eligible. Reduces taxable pension/annuity income by up to $3,000."""
    if not is_pso_eligible:
        return income_dict

    reduction = 3000
    pension = income_dict.get("Pension", 0)
    annuity = income_dict.get("Annuity", 0)

    if pension >= reduction:
        income_dict["Pension"] -= reduction
    elif annuity >= reduction:
        income_dict["Annuity"] -= reduction
    else:
        # Partial exclusion if neither covers full $3,000
        total_available = pension + annuity
        income_dict["Pension"] = max(0, pension - reduction)
        income_dict["Annuity"] = max(0, annuity - (reduction - pension))

    return income_dict

def simulate_roth_conversion(income_dict, age_1=64, age_2=60):
    """Simulates Roth conversions from $0 to $150k and tracks marginal tax impact."""
    results = []
    for conv_amount in range(0, 150001, 5000):
        temp_income = income_dict.copy()
        temp_income["Roth Conversions"] = conv_amount
        adjusted = apply_pso_credit(temp_income, is_pso_eligible)
        tax_result = estimate_tax(adjusted, age_1, age_2)
        results.append((conv_amount, tax_result["Total Tax"]))
    return results
def apply_capital_loss_offset(income_dict, capital_loss_carryover):
    """Applies up to $3,000 of capital loss carryover against ordinary income."""
    offset_limit = min(capital_loss_carryover, 3000)

    # Prioritize offsetting taxable interest, then pension, then annuity
    for key in ["Taxable Interest", "Pension", "Annuity"]:
        if key in income_dict and income_dict[key] > 0:
            reduction = min(offset_limit, income_dict[key])
            income_dict[key] -= reduction
            offset_limit -= reduction
            if offset_limit <= 0:
                break

    return income_dict

def estimate_tax(income_dict, age_1, age_2):
    base_deduction = 29200
    age_bonus = 1500 * sum([age_1 >= 65, age_2 >= 65])
    deduction = base_deduction + age_bonus

    ss = income_dict.get("Social Security", 0)
    qualified_div = income_dict.get("Qualified Dividends", 0)
    cap_gains = income_dict.get("Capital Gains", 0)

    ordinary_income = sum([
        income_dict.get("IRA Withdrawals", 0),
        income_dict.get("Roth Conversions", 0),
        income_dict.get("Pension", 0),
        income_dict.get("TSP", 0),
        income_dict.get("Annuity", 0),
        income_dict.get("Interest", 0),
        income_dict.get("Ordinary Dividends", 0)
    ])

    provisional = ordinary_income + 0.5 * ss + qualified_div + cap_gains
    if provisional <= 32000:
        ss_taxable = 0
    elif provisional <= 44000:
        ss_taxable = 0.5 * (provisional - 32000)
    else:
        ss_taxable = 0.85 * ss
    ss_taxable = min(ss_taxable, 0.85 * ss)

    taxable_income = max(0, ordinary_income + ss_taxable - deduction)

    brackets = [
        (0, 23200, 0.10),
        (23200, 94300, 0.12),
        (94300, 201050, 0.22),
        (201050, 383900, 0.24),
        (383900, 487450, 0.32),
        (487450, 731200, 0.35),
        (731200, float('inf'), 0.37)
    ]

    tax = 0
    for lower, upper, rate in brackets:
        if taxable_income > lower:
            taxed_amount = min(taxable_income, upper) - lower
            tax += taxed_amount * rate
        else:
            break

    cg_thresholds = [(0, 89450, 0.00), (89450, 553850, 0.15), (553850, float('inf'), 0.20)]
    cg_taxable = qualified_div + cap_gains
    cg_tax = 0
    for lower, upper, rate in cg_thresholds:
        if taxable_income + cg_taxable > lower:
            taxed_amount = min(taxable_income + cg_taxable, upper) - lower
            cg_tax += taxed_amount * rate
        else:
            break

    return {
        "Total Income": ordinary_income + ss + qualified_div + cap_gains,
        "Deduction": deduction,
        "Taxable Income": taxable_income,
        "Ordinary Tax": round(tax, 2),
        "Capital Gains Tax": round(cg_tax, 2),
        "Total Tax": round(tax + cg_tax, 2)
    }

# Streamlit UI
st.title("💸 IRA Conversion & Tax Estimator")
st.caption("For Married Filing Jointly | Ages 64 & 60")

income_sources = {
    "IRA Withdrawals": st.slider("IRA Withdrawals", 0, 150000, 30000, step=1000),
    "Roth Conversions": st.slider("Roth Conversions", 0, 150000, 20000, step=1000),
    "Pension": st.slider("Pension Income", 0, 100000, 25000, step=1000),
    "TSP": st.slider("TSP Withdrawals", 0, 100000, 15000, step=1000),
    "Annuity": st.slider("Annuity Payments", 0, 100000, 10000, step=1000),
    "Interest": st.slider("Interest Income", 0, 50000, 3000, step=500),
    "Ordinary Dividends": st.slider("Ordinary Dividends", 0, 50000, 0, step=500),
    "Qualified Dividends": st.slider("Qualified Dividends", 0, 50000, 5000, step=500),
    "Capital Gains": st.slider("Capital Gains", 0, 100000, 10000, step=1000),
    "Social Security": st.slider("Social Security Benefits", 0, 80000, 40000, step=1000)
}

capital_loss_carryover = st.number_input(
    "💸 Capital Loss Carryover ($)", min_value=0, max_value=100000, value=0, step=500
)

# Eligibility toggles
is_pso_eligible = st.checkbox("✅ Eligible for PSO Credit (Retired Law Enforcement / Firefighter)")
is_illinois_resident = st.checkbox("🏠 Illinois Resident (Retirement Income Excluded from State Tax)")

adjusted_income = apply_pso_credit(income_sources.copy(), is_pso_eligible)
results = estimate_tax(adjusted_income, age_1=64, age_2=60)

st.subheader("📊 Tax Summary")
for k, v in results.items():
    st.write(f"**{k}:** ${v:,.2f}")

if is_pso_eligible:
    st.info("✅ PSO Credit Applied: Up to $3,000 excluded from taxable pension/annuity income.")

if is_illinois_resident:
    st.info("🏠 Illinois Resident: Retirement income (IRA, pension, annuity, Social Security) is excluded from *state* tax. This estimator models **federal** tax only.")

st.subheader("📈 Roth Conversion Tax Impact")

conversion_data = simulate_roth_conversion(income_sources.copy(), age_1=64, age_2=60)
conv_amounts, total_taxes = zip(*conversion_data)

import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(conv_amounts, total_taxes, marker='o', color='purple')
ax.set_title("Marginal Tax Impact of Roth Conversions")
ax.set_xlabel("Roth Conversion Amount ($)")
ax.set_ylabel("Total Federal Tax ($)")
ax.grid(True)

if capital_loss_carryover > 0:
    st.info(f"💸 Capital Loss Carryover Applied: ${min(capital_loss_carryover, 3000):,.0f} offset against ordinary income.")

st.pyplot(fig)
