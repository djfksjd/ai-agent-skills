#!/usr/bin/env python3
"""Explicit monthly-recognition scenario, not financial or tax advice."""
from __future__ import annotations
import argparse
import json
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from pathlib import Path


def amount(value) -> Decimal:
    if isinstance(value, bool): raise ValueError("Boolean is not an amount")
    try: result = Decimal(str(value))
    except InvalidOperation as exc: raise ValueError("Invalid amount") from exc
    if not result.is_finite() or result < 0: raise ValueError("Amounts must be finite and nonnegative")
    return result


def break_even(monthly_fixed, price_including_tax, tax_rate, monthly_variable, cycle_months=1):
    fixed, price, tax, variable, cycle = map(amount, (monthly_fixed, price_including_tax, tax_rate, monthly_variable, cycle_months))
    if cycle <= 0 or cycle != cycle.to_integral_value(): raise ValueError("cycle_months must be a positive integer")
    contribution = price / (1 + tax) / cycle - variable
    if contribution <= 0: return None
    return int((fixed / contribution).to_integral_value(rounding=ROUND_CEILING))


def calculate(data: dict) -> dict:
    months = data.get("months", 12)
    if type(months) is not int or not 1 <= months <= 120: raise ValueError("months must be 1..120")
    fixed = amount(data["monthly_fixed_cost"])
    plans = data["plans"]
    if not isinstance(plans, list) or not plans: raise ValueError("plans must be a nonempty list")
    revenue, variable = [Decimal(0)] * months, [Decimal(0)] * months
    names, bep = set(), {}
    for p in plans:
        name = p["name"]
        if not isinstance(name, str) or not name or name in names: raise ValueError("Plan names must be unique")
        names.add(name)
        customers = p["active_customers"]
        if not isinstance(customers, list) or len(customers) != months or any(type(n) is not int or n < 0 for n in customers):
            raise ValueError("Use nonnegative integer active customers for every month")
        price, tax, cycle, cost = map(amount, (p["price_including_tax"], p["tax_rate"], p["cycle_months"], p["monthly_variable_per_customer"]))
        if not cycle or cycle != cycle.to_integral_value(): raise ValueError("cycle_months must be a positive integer")
        net = price / (1 + tax) / cycle
        for m, n in enumerate(customers): revenue[m] += net * n; variable[m] += cost * n
        bep[name] = break_even(fixed, price, tax, cost, cycle)
    rows = [{"month": m+1, "revenue_ex_tax": str(revenue[m].quantize(Decimal('.01'))),
             "variable_cost": str(variable[m].quantize(Decimal('.01'))),
             "contribution": str((revenue[m]-variable[m]).quantize(Decimal('.01'))),
             "operating_result": str((revenue[m]-variable[m]-fixed).quantize(Decimal('.01')))} for m in range(months)]
    return {"basis": "User-supplied scenario; prices evenly allocated over contract months, tax excluded from revenue",
            "limitations": "Not cash flow, deferred revenue accounting or a forecast. No automatic churn/CAC/payroll assumptions; include them explicitly in inputs.",
            "months": rows, "cumulative_revenue_ex_tax": str(sum(revenue).quantize(Decimal('.01'))),
            "cumulative_operating_result": str((sum(revenue)-sum(variable)-fixed*months).quantize(Decimal('.01'))),
            "ending_month_revenue_annualized": str((revenue[-1]*12).quantize(Decimal('.01'))),
            "single_plan_break_even_customers": bep}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("input", type=Path); args = p.parse_args()
    try: print(json.dumps(calculate(json.loads(args.input.read_text(encoding="utf-8"))), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, OSError) as exc: p.exit(2, f"ERROR: {exc}\n")


if __name__ == "__main__": main()
