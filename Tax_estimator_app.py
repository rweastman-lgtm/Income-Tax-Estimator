# tax_estimator_app.py
import streamlit as st
import matplotlib.pyplot as plt

def apply_pso_credit(income_dict, is_pso_eligible):
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
        total_available = pension + annuity
        income_dict["Pension"] = max(0, pension - reduction)
        income_dict["Annuity"] = max(0, annuity - (reduction - pension))

    return income_dict

def apply_capital_loss_offset(income_dict, capital_loss_carryover):
    offset_limit = min(capital_loss_carryover, 3000)
    for key in ["Taxable Interest", "Pension", "Annuity"]:
        if key in income_dict and income_dict[key] > 0:
            reduction = min(offset_limit, income_dict[key])
            income_dict[key] -= reduction
            offset_limit -= reduction
            if offset_limit <= 0:
                break
    return income_dict

def get_bonus_deduction(magi):
    if magi <= 150000:
        return 12000
    elif magi <= 250000:
        return max(0, 12000 - 0.06 * (magi - 150000))
    else:
        return 0

def calculate_cg_tax(qualified_dividends, capital_gains, capital_loss_carryover, taxable_income):
    brackets = [
        (0, 89450, 0.00),
        (89450, 553850, 0.15),
        (553850, float('inf'), 0.20)
    ]

    offset = min(capital_gains, capital_loss_carryover)
    adjusted_gains = max(0, capital_gains - offset)
    remaining_loss = capital_loss_carryover - offset

    cg_plus_qd = adjusted_gains + qualified_dividends
    cg_tax = 0
    remaining = cg_plus_qd
    verbose = []

    for lower, upper, rate in brackets:
        bracket_start = max(lower, taxable_income)
        if bracket_start >= upper or remaining <= 0:
            continue
        bracket_range = upper - bracket_start
        taxed_amount = min(remaining, bracket_range)
        tax = taxed_amount * rate
        cg_tax += tax
        verbose.append((f"${bracket_start:,.0f}–${upper:,.0f} @ {int(rate*100)}%", round(tax, 2)))
        remaining -= taxed_amount

    return round(cg_tax, 2), verbose, remaining_loss

def estimate_tax(income_dict, age_1, age_2, capital_loss_carryover):
    base_deduction = 31500
    bonus_deduction = sum(
        get_bonus_deduction(sum(income_dict.values()))
        for age in [age_1, age_2] if age >= 65
    )
    deduction = base_deduction + bonus_deduction

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
        (0, 23850, 0.10),
        (23850, 96950, 0.12),
        (96950, 206700, 0.22),
        (206700, 394600, 0.24),
        (394600, 501050, 0.32),
        (501050, 751600, 0.35),
        (751600, float('inf'), 0.37)
    ]

    tax = 0
    breakdown = []
    for lower, upper, rate in brackets:
        if taxable_income > lower:
            taxed_amount = min(taxable_income, upper) - lower
            bracket_tax = taxed_amount * rate
            tax += bracket_tax
            breakdown.append((f"${lower:,}–${upper:,} @ {int(rate*100)}%", round(bracket_tax, 2)))
        else:
            break

    adjusted_gains = max(0, cap_gains - capital_loss_carryover)
    cg_tax, cg_verbose, carryover_remaining = calculate_cg_tax(
        qualified_dividends=qualified_div,
        capital_gains=adjusted_gains,
        capital_loss_carryover=capital_loss_carryover,
        taxable_income=taxable_income
    )

    return {
        "Total Income": ordinary_income + ss + qualified_div + cap_gains,
        "Deduction": deduction,
        "Taxable Income": taxable_income,
        "Ordinary Tax": round(tax, 2),
        "Capital Gains Tax": round(cg_tax, 2),
        "Total Tax": round(tax + cg_tax, 2),
        "Bracket Breakdown": breakdown,
        "CG Breakdown": cg_verbose
    }

def simulate_roth_conversion(income_dict, age_1=64, age_2=60, is_pso_eligible=False, capital_loss_carryover=0):
    results = []
    for conv_amount in range(0, 150001, 5000):
        temp_income = income_dict.copy()
        temp_income["Roth Conversions"] = conv_amount
        adjusted = apply_pso_credit(temp_income, is_pso_eligible)
        tax_result = estimate_tax(adjusted, age_1, age_2, capital_loss_carryover)
        results.append((conv_amount, tax_result["Total Tax"]))
    return results

# Streamlit UI
st.title("💸 IRA Conversion & Tax Estimator")
st.caption("For Married Filing Jointly | Ages 64 & 60")

age_1 = st.number_input("Age of Taxpayer 1", min_value=0, max_value=120, value=64, step=1)
age_2 = st.number_input("Age of Taxpayer 2", min_value=0, max_value=120, value=60, step=1)

income_sources = {
    "IRA Withdrawals": st.number_input("IRA Withdrawals ($)", min_value=0, value=30000, step=1000),
    "Roth Conversions": st.number_input("Roth Conversions ($)", min_value=0, value=20000, step=1000),
    "Pension": st.number_input("Pension Income ($)", min_value=0, value=25000, step=1000),
    "TSP": st.number_input("TSP Withdrawals ($)", min_value=0, value=15000, step=1000),
    "Annuity": st.number_input("Annuity Payments ($)", min_value=0, value=10000, step=1000),
    "Interest": st.number_input("Interest Income ($)", min_value=0, value=3000, step=500),
    "Ordinary Dividends": st.number_input("Ordinary Dividends ($)", min_value=0, value=0, step=500),
    "Qualified Dividends": st.number_input("Qualified Dividends ($)", min_value=0, value=5000, step=500),
    "Capital Gains": st.number_input("Capital Gains ($)", min_value=0, value=10000, step=1000),
    "Social Security": st.number_input("Social Security Benefits ($)", min_value=0, value=40000, step=1000)
}

capital_loss_carryover = st.number_input("💸 Capital Loss Carryover ($)", min_value=0, max_value=100000, value=0, step=500)
is_pso_eligible = st.checkbox("✅ Eligible for PSO Credit (Retired Law Enforcement / Firefighter)")
is_illinois_resident = st.checkbox("🏠 Illinois Resident (Retirement Income Excluded from State Tax)")

adjusted_income = apply_pso_credit(income_sources.copy(), is_pso_eligible)
results = estimate_tax(adjusted_income, age_1=age_1, age_2=age_2, capital_loss_carryover=capital_loss_carryover)

st.subheader("📊 Tax Summary")
for k, v in results.items():
    if k not in ["Bracket Breakdown", "CG Breakdown"]:
        if isinstance(v, (int, float)):
            st.write(f"**{k}:** ${v:,.2f}")
        else:
            st.write(f"**{k}:** {v}")

