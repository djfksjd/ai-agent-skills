#!/usr/bin/env python3
"""Explicit monthly revenue scenario, not cash flow, accounting advice or a forecast."""
from __future__ import annotations
import argparse
import json
from decimal import Decimal, ROUND_CEILING
from pathlib import Path


def number(value, name: str) -> Decimal:
    if isinstance(value, bool): raise ValueError(name + " must be numeric")
    d = Decimal(str(value))
    if not d.is_finite() or d < 0: raise ValueError(name + " must be finite and nonnegative")
    return d


def model(data: dict) -> dict:
    vat = number(data["vat_rate"], "vat_rate")
    fixed = number(data["monthly_fixed_cost"], "monthly_fixed_cost")
    pay = number(data.get("monthly_team_pay", 0), "monthly_team_pay")
    products = data["products"]
    if not isinstance(products, list) or not products: raise ValueError("products required")
    months = len(products[0]["active_customers"])
    if months < 1: raise ValueError("At least one month required")
    revenue, variable = [Decimal(0)] * months, [Decimal(0)] * months
    per_product = []
    for p in products:
        counts = p["active_customers"]
        if len(counts) != months: raise ValueError("Monthly customer series must have equal lengths")
        period = number(p["price_period_months"], "price_period_months")
        if period == 0: raise ValueError("price_period_months must be positive")
        net = number(p["price_including_vat"], "price") / (1 + vat) / period
        cost = number(p["monthly_variable_cost"], "variable_cost")
        margin = net - cost
        for i, v in enumerate(counts):
            count = number(v, "active_customers")
            if count != count.to_integral_value(): raise ValueError("Customer counts must be integers")
            revenue[i] += net * count; variable[i] += cost * count
        per_product.append({"name": p["name"], "monthly_net_price": float(net),
                            "single_product_break_even_customers": int(((fixed + pay) / margin).to_integral_value(rounding=ROUND_CEILING)) if margin > 0 else None})
    return {"monthly_net_revenue": [round(float(x), 2) for x in revenue],
            "cumulative_net_revenue": round(float(sum(revenue)), 2),
            "last_month_annualized_revenue": round(float(revenue[-1] * 12), 2),
            "modeled_operating_result": round(float(sum(revenue) - sum(variable) - (fixed + pay) * months), 2),
            "products": per_product,
            "limitations": "Assumed active customers; annual price allocated evenly by month. No cash receipts, deferred revenue, refunds, financing or tax/accounting determination. Add all acquisition/support/payroll costs explicitly."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try: print(json.dumps(model(json.loads(args.input.read_text(encoding="utf-8"))), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, OSError) as exc: parser.exit(1, str(exc) + "\n")
