# Budget Automater

Automatically log card transactions into a Google Sheet budget. Designed to run from an **Apple Shortcut** — pass in a transaction hash (merchant, amount, card, etc.) and the script categorizes the spend and updates the correct row in your sheet.

## How it works

1. Your Shortcut captures transaction details (e.g. from a bank notification or manual input).
2. The Shortcut runs this Python script with a **transaction hash** — a small dictionary of transaction fields.
3. The script matches the merchant name against category regex patterns.
4. The matching budget category’s **Expense Amount** cell is incremented in Google Sheets.

```
Apple Shortcut → transaction hash → budget_engine.run() → Google Sheet updated
```

## Project structure

| File | Purpose |
|------|---------|
| `budget_engine.py` | Entry point — `run()` to log a transaction, `clear()` to reset dynamic categories |
| `budget_utils.py` | `SheetUpdater` class — Google Sheets auth, categorization, and cell updates |
| `budget_regression.py` | Unit tests for bucketing and sheet operations |
| `requirements.txt` | Python dependencies |

## Setup

### 1. Install dependencies

```bash
python3 -m venv budget_boy
source budget_boy/bin/activate
pip install -r requirements.txt
```

### 2. Google Sheets API

1. Create a [Google Cloud service account](https://console.cloud.google.com/iam-admin/serviceaccounts) and download its JSON key file.
2. Save the key somewhere on your Mac (e.g. `~/credentials/budget-service-account.json`).
3. Share your budget Google Sheet with the service account email (Editor access).

### 3. Environment variables

Create a `.env` file in the project root (this file is gitignored — do not commit it):

```env
CREDS_PATH=credentials/budget-service-account.json
BUDGET=Your Budget Sheet Name
TEST_BUDGET=Your Test Budget Sheet Name

GROCERY_REGEX=(?i)trader joe|whole foods|costco
FOOD_OUT_REGEX=(?i)mcdonald|chipotle|doordash
TRANSPORTATION_REGEX=(?i)wawa|shell|uber
HOME_REGEX=(?i)target|home depot|amazon
```

| Variable | Description |
|----------|-------------|
| `CREDS_PATH` | Path to the service account JSON, relative to your home directory (`~`) |
| `BUDGET` | Name of the production Google Sheet to update |
| `TEST_BUDGET` | Name of a test sheet used by the regression suite |
| `GROCERY_REGEX` | Regex matched against merchant name → **Groceries** |
| `FOOD_OUT_REGEX` | Regex → **Food Out** |
| `TRANSPORTATION_REGEX` | Regex → **Transportation** |
| `HOME_REGEX` | Regex → **Home** |

Merchants that match no pattern are bucketed into **Misc**.

### 4. Google Sheet layout

The first worksheet tab is used by default. Row 1 must include these headers:

| Money Out | Income Amount | Expense Amount |
|-----------|---------------|----------------|
| Groceries | … | $0.00 |
| Food Out | … | $0.00 |
| Transportation | … | $0.00 |
| Home | … | $0.00 |
| dynamic | … | … |
| … | … | … |
| Misc | … | $0.00 |
| Total Dynamic | … | $0.00 |

- **Money Out** — category label (must include `Groceries`, `Food Out`, `Transportation`, `Home`, `Misc`, `dynamic`, and `Total Dynamic`).
- **Expense Amount** — running total for each category; this is what gets updated.
- The `dynamic` row is a separator. Rows between `dynamic` and `Misc` are cleared when you call `clear()`.

## Transaction hash

A transaction hash is a Python dict passed to `run()`:

```python
{
    'card': 'apple',           # optional — for your own tracking
    'merchant': 'trader joes', # required — used for category matching
    'name': 'User',            # optional
    'amount': 176.76           # required — charge amount (number)
}
```

Only `merchant` and `amount` are required for the sheet update logic.

## Apple Shortcut integration

If using Juno on Iphone select run code, and paste this into the code section. 
Make sure files are on phone in correct location. 
Easier to put creds in same folder in juno and update creds path in .env and drop os.path.expanduser() for g_cred.

Note: you can also use Juno run file selection, and place these into a new script file, this seems more consistent. 
Make sure to update the index of the argument `sys.argc[1]`.

```python
from budget_engine import run, json, TEST_BUDGET

try:
      data = json.loads(sys.argv[2])
      run(TEST_BUDGET, data)
except IndexError:
      print("check index")
```
For reseting the dynamic columns.
```python
from budget_engine import clear, TEST_BUDGET

clear(TEST_BUDGET)
```
## Usage

### Log a transaction

```python
from budget_engine import run
from budget_utils import BUDGET

transaction = {
    'card': 'Visa',
    'merchant': 'trader joes',
    'name': 'Your Name',
    'amount': 42.50,
}
run(BUDGET, transaction)
```

### Reset dynamic expense categories, and charge log

Zeros out **Expense Amount** for every category between the `dynamic` and `Misc` rows (useful at the start of a new budget period) as well as the charge log:

Using this code, it will also run reset_check() to ensure that charges and dynamic is empty.
```python
from budget_engine import clear
from budget_utils import BUDGET

clear(BUDGET)
```

## Tests

Run the regression suite against your test sheet (`TEST_BUDGET` in `.env`):

```bash
source budget_boy/bin/activate
python budget_regression.py
```

Tests cover merchant bucketing (regex → category) and live sheet read/write against the test budget.

## Categories

| Category | Matched by |
|----------|------------|
| Groceries | `GROCERY_REGEX` |
| Food Out | `FOOD_OUT_REGEX` |
| Transportation | `TRANSPORTATION_REGEX` |
| Home | `HOME_REGEX` |
| Misc | default when no regex matches |

## Charge log

Appends a new charge hash to charges, this contians the full transaction hash with a new date key, which uses the current date. 
Called inside updater, can be removed if not wanted. This depends on a charges column being present. Also in reset where you can 
clear out all charges when you reset your dynamic spend.

## TODO

- make google sheet prettier
- update unittest to test more regex cases for real world merchant name data
- explore gspread.find() to attempt to clear index dependencies - works better switch up helper methods to use this.
- contiue live testing, name does not seem to be `User_name` so far
- check concurrent user issues
