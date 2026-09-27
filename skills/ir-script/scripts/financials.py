#!/usr/bin/env python3
"""Illustrative monthly revenue model; not cash flow, accounting or tax advice."""
from __future__ import annotations
from decimal import Decimal, ROUND_CEILING
import argparse,json,sys
from pathlib import Path

def dec(x):
    if isinstance(x,bool):raise ValueError('Boolean is not a financial input')
    try:d=Decimal(str(x))
    except Exception as e:raise ValueError('Invalid numeric input') from e
    if not d.is_finite() or d<0:raise ValueError('Financial inputs must be finite and nonnegative')
    return d

def calculate(data):
    months=data['months']
    if type(months) is not int or not 1<=months<=120:raise ValueError('months must be an integer from 1 to 120')
    vat=dec(data['vat_rate']);fixed=dec(data['monthly_fixed_cost']);payroll=dec(data['monthly_payroll'])
    revenue=[Decimal(0)]*months;variable=[Decimal(0)]*months;contributions={}
    products=data['products']
    if not isinstance(products,list) or not products:raise ValueError('products required')
    names=set()
    for p in products:
        if not isinstance(p['name'],str) or not p['name'].strip() or p['name'] in names:raise ValueError('Unique product name required')
        names.add(p['name']);period=p['price_period_months']
        if type(period) is not int or period<1:raise ValueError('price_period_months must be positive integer')
        price=dec(p['tax_inclusive_price'])/(1+vat)/period;cost=dec(p['monthly_variable_cost'])
        counts=p['active_customers']
        if not isinstance(counts,list) or len(counts)!=months:raise ValueError('One active_customer count per month required')
        contributions[p['name']]=price-cost
        for i,n in enumerate(counts):
            if type(n) is not int or n<0:raise ValueError('Customer counts must be nonnegative integers')
            revenue[i]+=price*n;variable[i]+=cost*n
    f=lambda x:float(x.quantize(Decimal('.01')))
    profits=[r-v-fixed-payroll for r,v in zip(revenue,variable)]
    return {'currency':data.get('currency','unspecified'),'basis':'Illustrative tax-exclusive, straight-line monthly allocation; not cash flow',
      'monthly_revenue':[f(x) for x in revenue],'monthly_variable_cost':[f(x) for x in variable],
      'monthly_result':[f(x) for x in profits],'cumulative_revenue':f(sum(revenue)),
      'cumulative_result':f(sum(profits)),'last_month_annualized_revenue':f(revenue[-1]*12),
      'single_product_break_even':{name:int(((fixed+payroll)/c).to_integral_value(rounding=ROUND_CEILING)) if c>0 else None for name,c in contributions.items()},
      'excluded':['cash receipts','deferred revenue','refunds','payment timing','acquisition costs unless included in fixed/variable inputs']}

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('input');x=a.parse_args()
    try:print(json.dumps(calculate(json.loads(Path(x.input).read_text(encoding='utf-8'))),ensure_ascii=False,indent=2,allow_nan=False));return 0
    except (ValueError,KeyError,TypeError,OSError) as e:print('ERROR: '+str(e),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
