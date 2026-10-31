import unittest
from mind_the_gap import plan


def workspace(number, windows=1, name=None, persistent=False):
    return dict(id=number, name=str(number) if name is None else name,
                windows=windows, ispersistent=persistent)


class NumberingPlan(unittest.TestCase):
    def test_closes_multiple_gaps_in_order(self):
        self.assertEqual(plan([workspace(i) for i in [1, 2, 5, 6, 7]]),
                         {5: 3, 6: 4, 7: 5})

    def test_trailing_empty_workspaces_are_not_gaps(self):
        self.assertEqual(plan([workspace(1), workspace(2), workspace(5, 0)]), {})

    def test_named_and_persistent_numbers_are_reserved(self):
        self.assertEqual(plan([workspace(1, 0, persistent=True),
                               workspace(2, name='Work'), workspace(5), workspace(7)]),
                         {5: 3, 7: 4})

    def test_special_workspaces_are_ignored(self):
        self.assertEqual(plan([workspace(-99), workspace(3)]), {3: 1})

    def test_empty_session(self):
        self.assertEqual(plan([]), {})


if __name__ == '__main__':
    unittest.main()
