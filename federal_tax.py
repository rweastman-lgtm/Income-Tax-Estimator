# federal_tax.py

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

    cg_tax, cg_verbose, carryover_remaining = calculate_cg_tax(
        qualified_dividends=qualified_div,
        capital_gains=cap_gains,
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
    "CG Breakdown": cg_verbose,
    "Taxed Retirement": sum([
        income_dict.get("Social Security", 0),
        income_dict.get("Pension", 0),
        income_dict.get("IRA Withdrawals", 0),
        income_dict.get("Annuity", 0)
    ]),
    "Taxed Social Security": round(ss_taxable, 2)
}



