import unittest   # The testframework
import flashcards



 
def increment(i):
    return i + 1

def decrement(i):
    return i-1


class Test_TestIncrementDecrement(unittest.TestCase):
    def test_increment(self):
        self.assertEqual(increment(3), 4)
    
    def test_obj(self):
        self.assertEqual(flashcards.testobj, 1)
    
    def test_decrement(self):
        self.assertEqual(decrement(3), 2)

if __name__ == '__main__':
    unittest.main()

##awdaw