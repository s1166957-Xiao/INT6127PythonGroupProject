import os
import tempfile
import unittest

from database import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        # create a temporary file for the sqlite database
        fd, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        # ensure no leftover excel files affect migration
        self._orig_user_xlsx = os.path.exists('user.xlsx')
        self._orig_express_xlsx = os.path.exists('express.xlsx')

        # instantiate manager with temp file
        self.db = DatabaseManager(db_file=self.db_path)

    def tearDown(self):
        try:
            self.db.disconnect()
        except Exception:
            pass
        try:
            os.remove(self.db_path)
        except Exception:
            pass

    def test_add_and_get_user(self):
        # initially no users
        users = self.db.get_all_users()
        self.assertIsInstance(users, list)

        # add a user
        ok = self.db.add_user('U1', 'Alice')
        self.assertTrue(ok)

        users = self.db.get_all_users()
        self.assertIn(('U1', 'Alice'), users)

        # update user
        ok = self.db.update_user('U1', 'AliceNew')
        self.assertTrue(ok)
        users = self.db.get_all_users()
        self.assertIn(('U1', 'AliceNew'), users)

        # delete user
        ok = self.db.delete_user('U1')
        self.assertTrue(ok)
        users = self.db.get_all_users()
        self.assertNotIn(('U1', 'AliceNew'), users)

    def test_area_operations_and_capacity_info(self):
        # default areas A/B/C should exist after initialization
        areas = self.db.get_all_areas()
        self.assertTrue(any(a[0] == 'A' for a in areas))

        # add new area
        ok = self.db.add_area('Z', 'Zone Z', 10, 'test zone')
        self.assertTrue(ok)
        areas = self.db.get_all_areas()
        self.assertTrue(any(a[0] == 'Z' for a in areas))

        # get area capacity info
        info = self.db.get_area_capacity_info('Z')
        self.assertIsNotNone(info)
        self.assertEqual(info[0], 'Z')

        # update area
        ok = self.db.update_area('Z', 'Zone ZZ', 20, 'updated')
        self.assertTrue(ok)
        info = self.db.get_area_capacity_info('Z')
        self.assertEqual(info[2], 20)

    def test_add_express_and_pickup_and_search(self):
        # prepare users and area
        self.db.add_user('S1', 'Sender')
        self.db.add_user('R1', 'Receiver')
        self.db.add_area('Y', 'AreaY', 5, '')

        # add express
        ok = self.db.add_express('EX1', '999999', 'S1', 'R1', 'Y', 'loc1', 'note', '在库')
        self.assertTrue(ok)

        # get by pick code
        rec = self.db.get_express_by_pick_code('999999')
        self.assertIsNotNone(rec)
        self.assertEqual(rec[0], 'EX1')

        # search
        results = self.db.search_express('EX1')
        self.assertTrue(len(results) >= 1)

        # update status to picked up
        ok = self.db.update_express_status('EX1', '已取件')
        self.assertTrue(ok)

        rec = self.db.get_express_by_pick_code('999999')
        self.assertEqual(rec[7], '已取件')

        # deleting area with express should fail
        ok, msg = self.db.delete_area('Y')
        self.assertFalse(ok)
        self.assertIn('无法删除', msg or '')

    def test_stats(self):
        # clear and add controlled data
        # add users and area
        self.db.add_user('S2', 'S2')
        self.db.add_user('R2', 'R2')
        self.db.add_area('Q', 'AreaQ', 100, '')

        # add several expresses
        for i in range(3):
            self.db.add_express(f'EXS{i}', f'P{i}000', 'S2', 'R2', 'Q', f'loc{i}', '', '在库')

        # one picked today
        self.db.add_express('EX_OUT', 'POUT', 'S2', 'R2', 'Q', 'locX', '', '在库')
        self.db.update_express_status('EX_OUT', '已取件')

        stats = self.db.get_express_stats()
        self.assertIn('in_storage', stats)
        self.assertIn('today_in', stats)
        self.assertIn('today_out', stats)
        # basic sanity checks
        self.assertGreaterEqual(stats['in_storage'], 3)


if __name__ == '__main__':
    unittest.main()
