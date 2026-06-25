import unittest
from budget_utils import SheetUpdater, TEST_BUDGET

class BudgetTester(unittest.TestCase):
    
    # regex testing, bucketer
    def test_home_bucketer(self):
      home = SheetUpdater("any_sheet", {"merchant": "Target Store"})
      self.assertEqual(home.bucketer(), "Home")

    def test_grocery_bucketer(self):
      grocery = SheetUpdater("any_sheet", {"merchant": "trader Joe's"})
      self.assertEqual(grocery.bucketer(), "Groceries")   
      
    def test_food_out_bucketer(self):
      food_out = SheetUpdater("any_sheet", {"merchant": "McDonald's"})
      self.assertEqual(food_out.bucketer(), "Food Out") 

    def test_transportation_bucketer(self):
      transportation = SheetUpdater("any_sheet", {"merchant": "WaWa Fuel"})
      self.assertEqual(transportation.bucketer(), "Transportation") 
      
    def test_misc_bucketer(self):
      misc = SheetUpdater("any_sheet", {"merchant": "Santa Cruz"})
      self.assertEqual(misc.bucketer(), "Misc") 
        
    # testing updater  
    def test_updater(self):
        transportation_update = SheetUpdater(TEST_BUDGET, {"merchant": 'Wawa Fuel', "amount": 23.28}).updater()
        self.assertEqual(SheetUpdater(TEST_BUDGET, {"merchant": 'misc', "amount": 0}).get_value('Transportation'), "$23.28")
        
    # also notice this clears the sheet so ^ SHOULD always be valid - when running with test suite not unittest.main()
    # test reset & reset_check
    def test_reset(self):
        reset = SheetUpdater(TEST_BUDGET).reset()
        self.assertTrue(SheetUpdater(TEST_BUDGET).reset_check())


if __name__ == '__main__':
    # unittest.main() 
    # need to run in order
    suite = unittest.TestSuite()
    suite.addTest(BudgetTester('test_home_bucketer'))
    suite.addTest(BudgetTester('test_grocery_bucketer'))
    suite.addTest(BudgetTester('test_food_out_bucketer'))
    suite.addTest(BudgetTester('test_transportation_bucketer'))
    suite.addTest(BudgetTester('test_misc_bucketer'))
    suite.addTest(BudgetTester('test_updater'))
    suite.addTest(BudgetTester('test_reset'))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)