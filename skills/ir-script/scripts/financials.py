#!/usr/bin/env python3
"""Explicit monthly revenue scenario; not cash flow, valuation or tax advice."""
import argparse
from decimal import Decimal, InvalidOperation, ROUND_CEILING
import json
from pathlib import Path


def amount(value, name):
    if isinstance(value, bool):
        raise ValueError(name + ': boolean is not a number')
    try:
        n = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(name + ': not a number') from exc
    if not n.is_finite() or n < 0:
        raise ValueError(name + ': must be finite and nonnegative')
    return n


def scenario(data):
    months = data['months']
    if type(months) is not int or not 1 <= months <= 120:
        raise ValueError('months: expected integer 1..120')
    tax = amount(data['vat_rate'], 'vat_rate')
    fixed = amount(data['monthly_fixed_cost'], 'monthly_fixed_cost')
    salary = amount(data['monthly_team_pay'], 'monthly_team_pay')
    totals = [Decimal(0)] * months
    variable = [Decimal(0)] * months
    plans = data['plans']
    if not isinstance(plans, list) or not plans:
        raise ValueError('plans required')
    breakeven = {}
    for p in plans:
        name = p['name']
        if not isinstance(name, str) or not name.strip() or name in breakeven:
            raise ValueError('plan name must be unique text')
        period = p['price_period_months']
        if type(period) is not int or period < 1:
            raise ValueError('price_period_months must be a positive integer')
        price = amount(p['tax_inclusive_price'], 'price') / (1+tax) / period
        cost = amount(p['monthly_variable_cost'], 'variable_cost')
        counts = p['active_by_month']
        if len(counts) != months or any(type(n) is not int or n < 0 for n in counts):
            raise ValueError('active_by_month must contain nonnegative integers for all months')
        for i, n in enumerate(counts):
            totals[i] += price*n; variable[i] += cost*n
        margin = price-cost
        breakeven[name] = int(((fixed+salary)/margin).to_integral_value(rounding=ROUND_CEILING)) if margin > 0 else None
    fmt = lambda n: str(n.quantize(Decimal('.01')))
    return {'basis':'Scenario: net of entered VAT; annual price allocated evenly per active month.',
            'excluded':'Cash receipts, deferred revenue, refunds, acquisition costs unless in fixed cost; no accounting opinion.',
            'monthly_net_revenue':[fmt(n) for n in totals],
            'cumulative_net_revenue':fmt(sum(totals)),
            'ending_annualized_revenue':fmt(totals[-1]*12),
            'cumulative_contribution':fmt(sum(totals)-sum(variable)),
            'cumulative_result':fmt(sum(totals)-sum(variable)-(fixed+salary)*months),
            'single_plan_breakeven_active_customers':breakeven}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('input', type=Path)
    args = ap.parse_args()
    try:
        print(json.dumps(scenario(json.loads(args.input.read_text(encoding='utf-8'))), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        ap.exit(2, str(exc)+'\n')
