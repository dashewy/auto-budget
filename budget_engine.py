from budget_utils import SheetUpdater, TEST_BUDGET
import sys
import json


def run(budget, transaction=None):
    
    runner = SheetUpdater(budget, transaction)
    
    try: 
        runner.updater()
        return print(f'Successfull update, {transaction.get('amount', 'FAILED')}, added')
    except Exception as e:
        return print(f'Sheet not updated, ERROR: {e}')
        
def clear(budget):
    
    resetter = SheetUpdater(budget)
    
    try:
        cleared = resetter.reset()        
        if resetter.reset_check():
            return print('Successfully cleared dynamic')
        else:
            return print('Check system')
    
    except Exception as e:
        return print(f'Error: {e}')
    

# if __name__ == '__main__':
    
#     test_hash = {'card': 'apple', 'merchant': "trader joes", 'name': 'User', 'amount': 176.76}
    
#     # run(TEST_BUDGET, test_hash)
#     # clear(TEST_BUDGET)

# For apple atuomation

# from budget_engine import run (shortcut dict not coming over as json coerce below)
# from budget_engine import run, json, TEST_BUDGET

# try:
#       data = json.loads(sys.argv[2])
#       run(TEST_BUDGET, data)
# except IndexError:
#       print("check index")