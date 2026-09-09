# ECD Loan Calculator

An interactive repayment and affordability calculator for **Rhiza Ventures' SeedFund Connect** ECD growth loans — built as a web demo around [`ecd_loan_calculator (1).py`](<ecd_loan_calculator (1).py>).

It works out monthly repayments and affordability for informal ECD (Early Childhood Development) growth loans, including the National Credit Act fees (once-off initiation fee + monthly service fee), and right-sizes a request against what an applicant can realistically pay.

## Contents

- [`index.html`](index.html) — the web interface. Static HTML/CSS/JS, no build step, no dependencies. It ports the Python script's math (`pmt`, `max_loan`, grace-period interest capitalisation, the months-to-repay log formula, and the OK / RIGHT-SIZE / DECLINE verdict logic) line-for-line into JavaScript, so every figure matches what the CLI script prints.
- [`ecd_loan_calculator (1).py`](<ecd_loan_calculator (1).py>) — the original command-line calculator. Run it directly (`python "ecd_loan_calculator (1).py"`) or interactively (`--interactive`).

## Running locally

The web interface needs no server or build step — open `index.html` directly in a browser, or serve the folder:

```
python -m http.server 8000
```

then visit `http://localhost:8000`.

## Deploying to Vercel

This is a static site, so Vercel needs no build command or output directory — just import the repo and deploy. `index.html` at the project root is served as-is.

## Features demoed

- Live repayment summary: all-in monthly payment, total interest, total fees, total repayable, cost of credit.
- Affordability verdicts (OK / right-size / decline) with the same reasoning the script prints, including the "capacity doesn't cover the service fee" edge case.
- A balance-over-term chart, a max-loan-by-term chart, and a principal/interest/fees cost breakdown.
- A full amortisation schedule table.
- Four preset scenarios spanning the verdict range, plus every input from the script (loan amount, rate, term, grace period, initiation fee financed/upfront, service fee, repayment capacity).
