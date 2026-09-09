#!/usr/bin/env python3
"""
SeedFund Connect - ECD Loan Calculator
=======================================
A division of Rhiza Ventures.

Works out loan repayments and affordability for informal ECD growth loans,
including the National Credit Act fees (once-off initiation fee + monthly
service fee). Mirrors the on-screen calculator exactly.

HOW TO USE
----------
Option A (quick): edit the numbers in the INPUTS block below and run:
        python ecd_loan_calculator.py

Option B (interactive): run with --interactive and answer the prompts:
        python ecd_loan_calculator.py --interactive

No external libraries needed - just Python 3.
"""

import sys
from math import log

# =====================================================================
# INPUTS  --  edit these with the figures from the completed gap analysis
# =====================================================================
APPLICANT      = "Diepsloot Loving & Care Pre-School"

LOAN_AMOUNT    = 20000.0   # amount the ECD is asking for (Rand)
ANNUAL_RATE    = 0.0       # annual interest rate, percent (0 = no interest)
TERM_MONTHS    = 24        # repayment term in months
GRACE_MONTHS   = 0         # months before repayment starts (interest still accrues)

INITIATION_FEE = 1050.0    # once-off NCA initiation fee (Rand)
INIT_FINANCED  = True      # True = added to the loan (earns interest); False = paid upfront
SERVICE_FEE    = 58.66     # monthly NCA service fee (Rand), added to every payment

# For the affordability check:
MONTHLY_CAPACITY = 300.0   # what the ECD can realistically pay each month, all-in (Rand)
# =====================================================================


def pmt(principal, monthly_rate, n):
    """Standard reducing-balance instalment."""
    if n <= 0:
        return 0.0
    if monthly_rate == 0:
        return principal / n
    return principal * monthly_rate / (1 - (1 + monthly_rate) ** (-n))


def max_loan(payment, monthly_rate, n):
    """Maximum principal a given payment can service over n months."""
    if n <= 0 or payment <= 0:
        return 0.0
    if monthly_rate == 0:
        return payment * n
    return payment * (1 - (1 + monthly_rate) ** (-n)) / monthly_rate


def rand(x):
    return "R{:,.0f}".format(x)


def rand2(x):
    return "R{:,.2f}".format(x)


def repayment_report(amount, annual_rate, term, grace,
                     init_fee, init_financed, service_fee):
    i = annual_rate / 100 / 12
    financed = amount + (init_fee if init_financed else 0.0)

    # capitalise interest during the grace period
    start = financed
    for _ in range(grace):
        start += start * i
    pay_n = max(1, term - grace)
    instalment = pmt(start, i, pay_n)
    all_in = instalment + service_fee

    # build the schedule to total the interest
    balance = financed
    total_interest = 0.0
    schedule = []
    for m in range(1, term + 1):
        opening = balance
        interest = balance * i
        if m <= grace:
            instal = 0.0
            principal = -interest
            balance += interest
        else:
            instal = instalment
            principal = instal - interest
            balance -= principal
            if balance < 0.5:
                balance = 0.0
        total_interest += max(interest, 0.0)
        schedule.append((m, opening, instal, interest, principal,
                         service_fee, instal + service_fee, balance))

    total_service = service_fee * term
    total_fees = init_fee + total_service
    total_repayable = instalment * pay_n + total_service + (0 if init_financed else init_fee)
    cost_pct = (total_repayable - amount) / amount * 100 if amount > 0 else 0.0

    print("=" * 66)
    print("  REPAYMENT  -  " + APPLICANT)
    print("=" * 66)
    print("  Loan amount (to the ECD) . . . . . {:>14}".format(rand(amount)))
    print("  Interest rate  . . . . . . . . . . {:>13.2f}%".format(annual_rate))
    print("  Term . . . . . . . . . . . . . . . {:>10} months".format(term)
          + ("  ({} grace)".format(grace) if grace else ""))
    print("  Initiation fee . . . . . . . . . . {:>14}  ({})".format(
        rand(init_fee), "financed" if init_financed else "upfront"))
    print("  Monthly service fee  . . . . . . . {:>14}".format(rand2(service_fee)))
    print("-" * 66)
    print("  >> ALL-IN MONTHLY PAYMENT  . . . . {:>14}".format(rand2(all_in)))
    print("       base instalment  . . . . . . {:>14}".format(rand2(instalment)))
    print("       + service fee  . . . . . . . {:>14}".format(rand2(service_fee)))
    print("  Total interest . . . . . . . . . . {:>14}".format(rand(total_interest)))
    print("  Total fees (init + service). . . . {:>14}".format(rand(total_fees)))
    print("  Total repayable  . . . . . . . . . {:>14}".format(rand(total_repayable)))
    print("  Cost of credit . . . . . . . . . . {:>13.1f}% of amount lent".format(cost_pct))
    print("=" * 66)
    return schedule


def affordability_report(capacity, annual_rate, term, target,
                         init_fee, init_financed, service_fee):
    i = annual_rate / 100 / 12
    avail = capacity - service_fee                     # left after the service fee
    max_fin = max_loan(avail, i, term)                 # financed principal supported
    max_to_applicant = max(0.0, max_fin - (init_fee if init_financed else 0.0))

    print()
    print("=" * 66)
    print("  AFFORDABILITY  -  " + APPLICANT)
    print("=" * 66)
    print("  Monthly capacity (all-in)  . . . . {:>14}".format(rand(capacity)))
    print("  less monthly service fee . . . . . {:>14}".format(rand2(service_fee)))
    print("  = available for the loan . . . . . {:>14}".format(rand2(max(avail, 0))))
    print("-" * 66)
    if avail <= 0:
        print("  The capacity does not even cover the service fee.")
        print("  No capital can be repaid. Raise capacity or lower the fee.")
        print("=" * 66)
        return
    print("  >> MAX LOAN TO THE ECD ({:>2}m) . . . {:>14}".format(term, rand(max_to_applicant)))
    print()
    print("  Max loan to the ECD by term (net of fees):")
    for t in (12, 24, 36, 48, 60):
        mf = max_loan(avail, i, t)
        print("       {:>2} months . . . . . . . . . . {:>14}".format(
            t, rand(max(0.0, mf - (init_fee if init_financed else 0.0)))))

    # months to repay the requested amount
    target_fin = target + (init_fee if init_financed else 0.0)
    print()
    if target > 0:
        if i == 0:
            months = target_fin / avail
            print("  Months to repay {} request . . {:>7.1f} months".format(rand(target), months))
        elif avail <= target_fin * i:
            months = float("inf")
            print("  Months to repay {} request . . {:>10}".format(rand(target), "never"))
        else:
            months = -log(1 - target_fin * i / avail) / log(1 + i)
            print("  Months to repay {} request . . {:>7.1f} months".format(rand(target), months))

        print("-" * 66)
        if max_to_applicant >= target:
            print("  VERDICT: OK - the request fits within {} months.".format(term))
        elif months != float("inf") and months <= 60:
            print("  VERDICT: RIGHT-SIZE - request needs ~{:.0f} months; over {} months".format(months, term))
            print("           you can lend about {}.".format(rand(max_to_applicant)))
        else:
            print("  VERDICT: DECLINE / DEVELOP - request not serviceable in a")
            print("           sensible term. Right-size to about {}".format(rand(max_to_applicant)))
            print("           or lift repayment capacity first.")
    print("=" * 66)


def ask(prompt, default, cast=float):
    raw = input("  {} [{}]: ".format(prompt, default)).strip()
    if raw == "":
        return default
    if cast is bool:
        return raw.lower() in ("y", "yes", "true", "1", "add", "financed")
    return cast(raw)


def interactive():
    global APPLICANT
    print("\nSeedFund Connect - ECD Loan Calculator (interactive)\n")
    APPLICANT = input("  ECD / applicant name [{}]: ".format(APPLICANT)).strip() or APPLICANT
    amount = ask("Loan amount requested (R)", LOAN_AMOUNT)
    rate = ask("Annual interest rate (%)", ANNUAL_RATE)
    term = int(ask("Term (months)", TERM_MONTHS, int))
    grace = int(ask("Grace period (months)", GRACE_MONTHS, int))
    init = ask("Initiation fee (R)", INITIATION_FEE)
    fin = ask("Initiation financed? y/n", "y", bool)
    svc = ask("Monthly service fee (R)", SERVICE_FEE)
    cap = ask("Monthly repayment capacity (R)", MONTHLY_CAPACITY)
    print()
    repayment_report(amount, rate, term, grace, init, fin, svc)
    affordability_report(cap, rate, term, amount, init, fin, svc)


def main():
    if "--interactive" in sys.argv or "-i" in sys.argv:
        interactive()
        return
    repayment_report(LOAN_AMOUNT, ANNUAL_RATE, TERM_MONTHS, GRACE_MONTHS,
                     INITIATION_FEE, INIT_FINANCED, SERVICE_FEE)
    affordability_report(MONTHLY_CAPACITY, ANNUAL_RATE, TERM_MONTHS, LOAN_AMOUNT,
                         INITIATION_FEE, INIT_FINANCED, SERVICE_FEE)
    print("\n  Tip: run  'python ecd_loan_calculator.py --interactive'  to enter"
          "\n  a different ECD's figures without editing the file.\n")


if __name__ == "__main__":
    main()
