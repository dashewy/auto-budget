from budget_utils import SheetUpdater, TEST_BUDGET
import sys


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

# from budget_engine import run
# try:
#     run(TEST_BUDGET, sys.argv[2])
# except IndexError:
#     print('check index')