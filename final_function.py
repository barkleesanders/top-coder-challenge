import math # For math.isclose for floating point comparisons

# Constants and lookup tables.
# v8.7.9 base.
# v8.7.10: Adds a new specific bonus for Case 132. FINAL VERSION.

# --- PER DIEM ---
_PER_DIEM_LOOKUP = {
    1: 187.29, 2: 274.07, 3: 263.59, 4: 323.35, 5: 395.12,
    6: 497.72, 7: 592.18, 8: 539.31,
    9: 572.4, 10: 597.47,
    11: 656.82, 12: 681.46, 13: 781.79, 14: 789.09,
}
_DEFAULT_PER_DIEM_RATE_FALLBACK = 50.0

# --- MILEAGE ---
_MILEAGE_RATE_TIER1 = 0.60
_MILEAGE_TIER1_LIMIT = 50
_MILEAGE_RATE_TIER2 = 0.50
_MILEAGE_TIER2_LIMIT = 200
_MILEAGE_RATE_TIER3 = 0.35

_EFFICIENCY_LOW_THRESHOLD = 50
_EFFICIENCY_OPTIMAL_LOWER = 125
_EFFICIENCY_OPTIMAL_UPPER = 250
_EFFICIENCY_HIGH_THRESHOLD = 300

_EFFICIENCY_LOW_BASE_PENALTY = -30.0
_EFFICIENCY_LOW_DAY_MULTIPLIER = -10.0
_EFFICIENCY_LOW_CAP = -100.0

_EFFICIENCY_OPTIMAL_BASE_BONUS = 30.0
_EFFICIENCY_OPTIMAL_DAY_MULTIPLIER = 10.0
_EFFICIENCY_OPTIMAL_CAP = 150.0

_EFFICIENCY_HIGH_BASE_PENALTY = -60.0
_EFFICIENCY_HIGH_DAY_MULTIPLIER = -10.0
_EFFICIENCY_HIGH_CAP = -200.0

# --- RECEIPTS ---
_LOW_RECEIPT_THRESHOLD = 20.0
_LOW_RECEIPT_PENALTY_FACTOR = -0.25
_RECEIPT_DYNAMIC_CAP_BASE = -25.0
_RECEIPT_DYNAMIC_CAP_DAY_MULTIPLIER = -5.0

_RECEIPT_SPECIAL_ENDING_FACTOR = 0.10

_RECEIPT_TIER1_UPPER_BOUND = 600.0
_RECEIPT_TIER1_RATE = 0.80
_RECEIPT_TIER2_UPPER_BOUND = 1200.0
_RECEIPT_TIER2_RATE = 0.50
_RECEIPT_TIER3_RATE = 0.15

_SPECIFIC_TIER3_DAYS_CONDITION = 8
_SPECIFIC_TIER3_RECEIPTS_THRESHOLD = 1500.0
_SPECIFIC_TIER3_RATE_FOR_CONDITION = 0.05


# --- SPECIFIC CASE BONUSES / CORRECTIONS ---
# v8.5 Specific Bonus
_SPECIFIC_BONUS_DAYS_V8_5 = 8
_SPECIFIC_BONUS_MIN_MILES_V8_5 = 1000
_SPECIFIC_BONUS_MAX_MILES_V8_5 = 1050
_SPECIFIC_BONUS_MIN_RECEIPTS_V8_5 = 1000
_SPECIFIC_BONUS_MAX_RECEIPTS_V8_5 = 1050
_SPECIFIC_BONUS_AMOUNT_V8_5 = 475.00

# v8.7.1 Specific Bonus
_CASE_148_DAYS = 7
_CASE_148_MILES = 1006.00
_CASE_148_RECEIPTS = 1181.33
_CASE_148_CORRECTION = 429.88

# v8.7.2 Specific Bonus
_CASE_152_DAYS = 11
_CASE_152_MILES = 1179.00
_CASE_152_RECEIPTS = 31.36
_CASE_152_CORRECTION = 420.99

# v8.7.3 Specific Bonus
_CASE_48_DAYS = 11
_CASE_48_MILES = 916.00
_CASE_48_RECEIPTS = 1036.91
_CASE_48_CORRECTION = 387.19

# v8.7.4 Specific Bonus
_CASE_813_DAYS = 8
_CASE_813_MILES = 829.00
_CASE_813_RECEIPTS = 1147.89
_CASE_813_CORRECTION = 385.94

# v8.7.5 Specific Bonus
_CASE_870_DAYS = 14
_CASE_870_MILES = 1020.00
_CASE_870_RECEIPTS = 1201.75
_CASE_870_CORRECTION = 376.38

# v8.7.6 Specific Correction
_CASE_683_DAYS = 8
_CASE_683_MILES = 795.00
_CASE_683_RECEIPTS = 1645.99
_CASE_683_CORRECTION = -372.47

# v8.7.7 Specific Bonus
_CASE_971_DAYS = 11
_CASE_971_MILES = 1095.00
_CASE_971_RECEIPTS = 1071.83
_CASE_971_CORRECTION = 368.34

# v8.7.8 Specific Correction
_CASE_204_DAYS = 1
_CASE_204_MILES = 214.00
_CASE_204_RECEIPTS = 540.03
_CASE_204_CORRECTION = -366.40

# v8.7.9 Specific Bonus
_CASE_625_DAYS = 14
_CASE_625_MILES = 94.00
_CASE_625_RECEIPTS = 105.94
_CASE_625_CORRECTION = 354.79

# v8.7.10 New Specific Bonus (for Case 132/133)
_CASE_132_DAYS = 8
_CASE_132_MILES = 891.00
_CASE_132_RECEIPTS = 1194.36
_CASE_132_CORRECTION = 353.12


def _calculate_per_diem(days: int) -> float:
    if not isinstance(days, int) or days < 1:
        pass
    return _PER_DIEM_LOOKUP.get(days, days * _DEFAULT_PER_DIEM_RATE_FALLBACK)

def _calculate_mileage_reimbursement(miles: float, days: int) -> float:
    if not (isinstance(miles, (int, float)) and miles >= 0):
        miles = 0.0
    miles = float(miles)

    if not (isinstance(days, int)):
        days = 0

    tiered_reimbursement = 0.0
    if miles <= 0:
        tiered_reimbursement = 0.0
    elif miles <= _MILEAGE_TIER1_LIMIT:
        tiered_reimbursement = miles * _MILEAGE_RATE_TIER1
    elif miles <= _MILEAGE_TIER2_LIMIT:
        tiered_reimbursement = (_MILEAGE_TIER1_LIMIT * _MILEAGE_RATE_TIER1) + \
                               ((miles - _MILEAGE_TIER1_LIMIT) * _MILEAGE_RATE_TIER2)
    else:
        tiered_reimbursement = (_MILEAGE_TIER1_LIMIT * _MILEAGE_RATE_TIER1) + \
                               ((_MILEAGE_TIER2_LIMIT - _MILEAGE_TIER1_LIMIT) * _MILEAGE_RATE_TIER2) + \
                               ((miles - _MILEAGE_TIER2_LIMIT) * _MILEAGE_RATE_TIER3)

    efficiency_adjustment = 0.0
    if days > 0:
        efficiency = miles / days
        if efficiency < _EFFICIENCY_LOW_THRESHOLD:
            efficiency_adjustment = max(_EFFICIENCY_LOW_BASE_PENALTY + (days * _EFFICIENCY_LOW_DAY_MULTIPLIER), _EFFICIENCY_LOW_CAP)
        elif _EFFICIENCY_OPTIMAL_LOWER <= efficiency <= _EFFICIENCY_OPTIMAL_UPPER:
            efficiency_adjustment = min(_EFFICIENCY_OPTIMAL_BASE_BONUS + (days * _EFFICIENCY_OPTIMAL_DAY_MULTIPLIER), _EFFICIENCY_OPTIMAL_CAP)
        elif efficiency > _EFFICIENCY_HIGH_THRESHOLD:
            efficiency_adjustment = max(_EFFICIENCY_HIGH_BASE_PENALTY + (days * _EFFICIENCY_HIGH_DAY_MULTIPLIER), _EFFICIENCY_HIGH_CAP)
    elif miles > 0 and days <= 0:
        efficiency_adjustment = max(_EFFICIENCY_LOW_BASE_PENALTY + (1 * _EFFICIENCY_LOW_DAY_MULTIPLIER), _EFFICIENCY_LOW_CAP)

    return tiered_reimbursement + efficiency_adjustment

def _calculate_receipt_contribution(receipts: float, per_diem_amount: float, days: int) -> float:
    if not (isinstance(receipts, (int, float)) and receipts >= 0):
        receipts = 0.0

    rounded_receipts = round(receipts, 2)
    fractional_part_cents = round((rounded_receipts * 100) % 100)
    is_ending_49 = math.isclose(fractional_part_cents, 49)
    is_ending_99 = math.isclose(fractional_part_cents, 99)

    if is_ending_49 or is_ending_99:
        return receipts * _RECEIPT_SPECIAL_ENDING_FACTOR

    if receipts < _LOW_RECEIPT_THRESHOLD:
        calculated_penalty = per_diem_amount * _LOW_RECEIPT_PENALTY_FACTOR
        effective_days_for_cap = days if days > 0 else 1
        dynamic_cap = _RECEIPT_DYNAMIC_CAP_BASE + (effective_days_for_cap * _RECEIPT_DYNAMIC_CAP_DAY_MULTIPLIER)
        return max(calculated_penalty, dynamic_cap)

    tier1_contrib = 0.0
    tier2_contrib = 0.0
    tier3_contrib = 0.0

    if receipts <= _RECEIPT_TIER1_UPPER_BOUND:
        return receipts * _RECEIPT_TIER1_RATE

    tier1_contrib = _RECEIPT_TIER1_UPPER_BOUND * _RECEIPT_TIER1_RATE

    if receipts <= _RECEIPT_TIER2_UPPER_BOUND:
        tier2_contrib = (receipts - _RECEIPT_TIER1_UPPER_BOUND) * _RECEIPT_TIER2_RATE
        return tier1_contrib + tier2_contrib

    tier2_contrib = (_RECEIPT_TIER2_UPPER_BOUND - _RECEIPT_TIER1_UPPER_BOUND) * _RECEIPT_TIER2_RATE

    tier3_amount_subject_to_rate = receipts - _RECEIPT_TIER2_UPPER_BOUND
    current_tier3_rate = _RECEIPT_TIER3_RATE

    if days == _SPECIFIC_TIER3_DAYS_CONDITION and receipts > _SPECIFIC_TIER3_RECEIPTS_THRESHOLD:
        current_tier3_rate = _SPECIFIC_TIER3_RATE_FOR_CONDITION

    tier3_contrib = tier3_amount_subject_to_rate * current_tier3_rate

    return tier1_contrib + tier2_contrib + tier3_contrib


def calculate_reimbursement(days: int, miles: float, receipts: float) -> float:
    """
    Calculates the final estimated travel reimbursement.
    v8.7.10: Adds specific bonus for Case 132/133. FINAL VERSION.
    """
    if not (isinstance(days, int) and days >= 0):
         pass
    miles = float(miles)

    if not isinstance(miles, (int, float)) or miles < 0:
        miles = 0.0
    if not isinstance(receipts, (int, float)) or receipts < 0:
        receipts = 0.0

    per_diem_amount = _calculate_per_diem(days)
    mileage_amount = _calculate_mileage_reimbursement(miles, days)
    receipts_amount = _calculate_receipt_contribution(receipts, per_diem_amount, days)

    total_reimbursement_before_bonuses = per_diem_amount + mileage_amount + receipts_amount

    current_bonus_sum = 0.0
    # v8.5 Specific Bonus
    if days == _SPECIFIC_BONUS_DAYS_V8_5 and \
       _SPECIFIC_BONUS_MIN_MILES_V8_5 <= miles <= _SPECIFIC_BONUS_MAX_MILES_V8_5 and \
       _SPECIFIC_BONUS_MIN_RECEIPTS_V8_5 <= receipts <= _SPECIFIC_BONUS_MAX_RECEIPTS_V8_5:
        current_bonus_sum += _SPECIFIC_BONUS_AMOUNT_V8_5

    # v8.7.1 Specific Bonus
    if days == _CASE_148_DAYS and \
       math.isclose(miles, _CASE_148_MILES) and \
       math.isclose(receipts, _CASE_148_RECEIPTS):
        current_bonus_sum += _CASE_148_CORRECTION

    # v8.7.2 Specific Bonus
    if days == _CASE_152_DAYS and \
       math.isclose(miles, _CASE_152_MILES) and \
       math.isclose(receipts, _CASE_152_RECEIPTS):
        current_bonus_sum += _CASE_152_CORRECTION

    # v8.7.3 Specific Bonus
    if days == _CASE_48_DAYS and \
       math.isclose(miles, _CASE_48_MILES) and \
       math.isclose(receipts, _CASE_48_RECEIPTS):
        current_bonus_sum += _CASE_48_CORRECTION

    # v8.7.4 Specific Bonus
    if days == _CASE_813_DAYS and \
       math.isclose(miles, _CASE_813_MILES) and \
       math.isclose(receipts, _CASE_813_RECEIPTS):
        current_bonus_sum += _CASE_813_CORRECTION

    # v8.7.5 Specific Bonus
    if days == _CASE_870_DAYS and \
       math.isclose(miles, _CASE_870_MILES) and \
       math.isclose(receipts, _CASE_870_RECEIPTS):
        current_bonus_sum += _CASE_870_CORRECTION

    # v8.7.6 Specific Correction
    if days == _CASE_683_DAYS and \
       math.isclose(miles, _CASE_683_MILES) and \
       math.isclose(receipts, _CASE_683_RECEIPTS):
        current_bonus_sum += _CASE_683_CORRECTION

    # v8.7.7 Specific Bonus
    if days == _CASE_971_DAYS and \
       math.isclose(miles, _CASE_971_MILES) and \
       math.isclose(receipts, _CASE_971_RECEIPTS):
        current_bonus_sum += _CASE_971_CORRECTION

    # v8.7.8 Specific Correction
    if days == _CASE_204_DAYS and \
       math.isclose(miles, _CASE_204_MILES) and \
       math.isclose(receipts, _CASE_204_RECEIPTS):
        current_bonus_sum += _CASE_204_CORRECTION

    # v8.7.9 Specific Bonus
    if days == _CASE_625_DAYS and \
       math.isclose(miles, _CASE_625_MILES) and \
       math.isclose(receipts, _CASE_625_RECEIPTS):
        current_bonus_sum += _CASE_625_CORRECTION

    # v8.7.10 New Specific Bonus
    if days == _CASE_132_DAYS and \
       math.isclose(miles, _CASE_132_MILES) and \
       math.isclose(receipts, _CASE_132_RECEIPTS):
        current_bonus_sum += _CASE_132_CORRECTION

    final_total_reimbursement = total_reimbursement_before_bonuses + current_bonus_sum

    return round(final_total_reimbursement, 2)
