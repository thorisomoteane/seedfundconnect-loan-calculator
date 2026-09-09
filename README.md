# ECD Loan Calculator

A small tool for **Rhiza Ventures' SeedFund Connect** to size, save and print ECD growth-loan assessments — built around [`ecd_loan_calculator (1).py`](<ecd_loan_calculator (1).py>).

It works out monthly repayments and affordability for informal ECD (Early Childhood Development) growth loans, including the National Credit Act fees (once-off initiation fee + monthly service fee), right-sizes a request against what an applicant can realistically pay, and produces a printable repayment summary for the ECD to keep.

Colours are drawn from the Rhiza Holdings brand handbook (Vibrant Orange, Mint/Teal, Sky Blue, Primary Dark Slate, and Golden Yellow — the handbook's own ECD-division colour, used here as the primary accent).

## Pages

- **`index.html` — New Application.** The calculator: enter an ECD's details and it works out the repayment schedule and an OK / right-size / decline verdict live. `Save application` stores it; `Print / save as PDF` opens a clean printable summary of whatever is currently on screen, saved or not. Open `index.html?id=<id>` to load a saved application back in for editing.
- **`applications.html` — Applications.** Every saved application on this device: applicant, amount, term, a verdict pill, and actions to open, print, or delete it.
- **`print.html` — Print report.** A print-formatted repayment summary (letterhead, key figures, verdict, full amortisation schedule, sign-off lines). Reached from either page; `window.print()` lets the browser's print dialog save it as a PDF.

Shared code lives in `assets/`:
- `assets/calc.js` — the calculation functions (ported line-for-line from the Python script), formatting helpers, and the `localStorage` read/write helpers for saved applications.
- `assets/style.css` — the shared design system (tokens, components, print styles).

## Data storage — browser-local only (for now)

Saved applications are kept in this browser's `localStorage`. That means:
- They're private to this device/browser — nothing is sent anywhere.
- Clearing browser data, or opening the site on another device, loses them.
- Two people using the tool don't see each other's saved applications.

This is intentional for the current demo stage. Moving to a shared store (e.g. a small database + API routes on Vercel) is a natural next step once this needs to be used by more than one person.

## Running locally

No server or build step needed — open `index.html` directly in a browser, or serve the folder:

```
python -m http.server 8000
```

then visit `http://localhost:8000`.

## Deploying to Vercel

Static site — Vercel needs no build command or output directory. Import the repo and deploy; `index.html` at the project root is served as-is, and `applications.html` / `print.html` are reachable at their own paths.

## Other files

- [`ecd_loan_calculator (1).py`](<ecd_loan_calculator (1).py>) — the original command-line calculator. Run it directly (`python "ecd_loan_calculator (1).py"`) or interactively (`--interactive`).
