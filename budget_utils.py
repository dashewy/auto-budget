import pandas as pd
import gspread 
import re
import os
from datetime import datetime
from dotenv import load_dotenv 

load_dotenv()

PATH = os.getenv("CREDS_PATH")
BUDGET = os.getenv('BUDGET')
TEST_BUDGET = os.getenv("TEST_BUDGET")

full_path = os.path.expanduser(f"~/{PATH}")
g_cred = gspread.service_account(full_path) 
                                    

class SheetUpdater:
    
    def __init__(self, budget_sheet, transaction=None, headers: list = ['Money Out', 'Income Amount', 'Expense Amount', 'Charges'], page: int=0):
        
        self.transaction = transaction
        self.budget_sheet = budget_sheet
        self.headers = headers
        self.page = page
        self.grocery_regex = os.getenv("GROCERY_REGEX")
        self.food_out_regex = os.getenv("FOOD_OUT_REGEX")
        self.transportation_regex = os.getenv("TRANSPORTATION_REGEX")
        self.home_regex = os.getenv("HOME_REGEX")

    @staticmethod
    def to_number(num):
        if isinstance(num, float) or isinstance(num, int):
            return num
        else:
            return float(num.replace('$', '').replace(',', ''))
            
    @staticmethod
    def to_dollar(num):
        return f'${num:,.2f}'
    
    def get_value(self, cat):
        
        df = self.to_df()
        
        current_series = df.query("`Money Out` == @cat")
        idx = current_series.index[0] 
               
        sheet = self.get_sheet()
        row, col = self.expense_cell(idx, sheet)
        
        return sheet.cell(row, col).value
    
    # may want to look into sheet.find for this
    def cols(self, sheet, header_row=1):
        headers = sheet.row_values(header_row)
        return {
            'money_out': headers.index("Money Out") + 1,
            'expense': headers.index('Expense Amount') + 1
        }
    
    def expense_cell(self, idx, sheet):
        return idx + 2, self.cols(sheet).get('expense')
    # sheet.find ^
    
    def get_sheet(self):
        
        total_sheet = g_cred.open(self.budget_sheet)
        budget_list = total_sheet.worksheets()
        
        current_budget = budget_list[self.page]
        
        return current_budget

    def to_df(self):
        
        sheet = self.get_sheet()
        
        budget_dict = sheet.get_all_records(expected_headers=self.headers)

        budget_df = pd.DataFrame(budget_dict)
        
        return budget_df
        
    def bucketer(self):
                    
        cat_table = [
            (self.grocery_regex, 'Groceries'),
            (self.food_out_regex, 'Food Out'),
            (self.transportation_regex, 'Transportation'),
            (self.home_regex, 'Home')
        ]
        # make sure defualt does not pass regex
        merchant = self.transaction.get('merchant', 'Not Found') 
        
        for pattern, val in cat_table:
            
            if re.search(pattern, merchant):
                return val

        return 'Misc'

    def updater(self, test=False):
        
        if not self.transaction:
            raise ValueError('Transaction required for updates')
        
        charge = SheetUpdater.to_number(self.transaction.get('amount', False))
        category = self.bucketer()
        df = self.to_df()
        
        if not charge:
            raise ValueError('No charge amount present')
        # use @ instead of f string to reference, use `` for literal column
        current_series = df.query("`Money Out` == @category")
        
        if current_series.empty:
            raise ValueError(f'No cat: {category}')
        
        idx = current_series.index[0]
        current_amount = SheetUpdater.to_number(current_series.at[idx, 'Expense Amount'])
        updated_value = SheetUpdater.to_dollar(current_amount + charge)
        
        sheet = self.get_sheet()
        row, col = self.expense_cell(idx, sheet)
        sheet.update_cell(row, col, updated_value)
        
        self.charge_log(date=test, sheet=sheet)
        
        return True
   
    def reset(self):
        # need to always keep misc at the bottom for this to be more explcit, and have dynamic seperator
        df = self.to_df()
        sheet = self.get_sheet()
        dynamic_series = df.query("`Money Out` == 'dynamic'")
        misc_series = df.query("`Money Out` == 'Misc'")
        # clear charges col
        charges = sheet.find('Charges')
        charge_idx = charges.col
        
        charge_start = gspread.utils.rowcol_to_a1(2, charge_idx)
        charge_end = gspread.utils.rowcol_to_a1(sheet.row_count, charge_idx)
        
        sheet.batch_clear([f'{charge_start}:{charge_end}'])
        
        if dynamic_series.empty or misc_series.empty:
            raise ValueError(f'No dynamic separator OR missing Misc')

        dynamic_idx = dynamic_series.index[0]
        misc_idx = misc_series.index[0]
        expense_col = self.cols(sheet).get('expense')
        
        wiped_cells = [gspread.Cell(i + 2, expense_col, "$0") for i in range(dynamic_idx + 1, misc_idx + 1)]
            
        sheet.update_cells(wiped_cells, value_input_option='USER_ENTERED')
        
        
    def reset_check(self):
        
        new_df = self.to_df()
        # <--- gspread -> pandas isna("") = False
        new_df['Charges'] = new_df.Charges.replace("", None) 
        total_dynamic_series = new_df.query("`Money Out` == 'Total Dynamic'")
        
        td_idx = total_dynamic_series.index[0]
        
        if SheetUpdater.to_number(total_dynamic_series.at[td_idx, 'Expense Amount']) == 0 and new_df.Charges.isna().all():
            return True
        
        else:
            return False
    # for easy unittesting keep date under control flow
    def charge_log(self, date=False, sheet=None):
        # had to flip to make test in updater, test=True -> no date
        if not date:
            self.transaction['date'] = str(datetime.now().strftime("%Y-%m-%d"))
        # lowers api calls, used in updater which already runs get_sheet() twice
        if not sheet:
            sheet = self.get_sheet()
            
        # .find() works way better
        header_cell = sheet.find('Charges')
        
        if not header_cell:
            # most likley picked up in the init but leave for now
            raise ValueError("No header names 'Charges'")
        
        col_idx = header_cell.col
        col_val = sheet.col_values(col_idx)
        
        sheet.update_cell(len(col_val) + 1, col_idx, str(self.transaction))
        
    

if __name__ == '__main__':
        
    test_hash = {'card': 'Visa', 'merchant': 'other', 'name': 'User', 'amount': 20.32}
    
    test_case = SheetUpdater(TEST_BUDGET, test_hash)
    print(test_case.reset_check())
    
    # print(test_case.updater())
    # print(test_case.reset()
    # print(test_case.get_value('Misc'))
    
    # this gets the savings, can use in apple shortcuts 
    # print(SheetUpdater(TEST_BUDGET).get_value('Total Savings'))
    # test_case.charge_log()