def compute_illinois_tax(federal_taxable_income, federally_taxed_retirement=0):
    """
    Calculates Illinois income tax based on federal taxable income.
    
    Args:
        federal_taxable_income (float): Total taxable income from federal estimator.
        federally_taxed_retirement (float): Portion of retirement income taxed federally but exempt in IL.

    Returns:
        dict: {
            'adjusted_income': float,
            'il_tax': float,
            'effective_rate': float
        }
    """
    adjusted_income = max(0, federal_taxable_income - federally_taxed_retirement)
    il_tax = round(adjusted_income * 0.0495, 2)
    effective_rate = round(il_tax / federal_taxable_income, 4) if federal_taxable_income else 0.0

    return {
        "adjusted_income": adjusted_income,
        "il_tax": il_tax,
        "effective_rate": effective_rate
    }
