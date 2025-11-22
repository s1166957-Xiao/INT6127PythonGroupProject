import unittest
import re
import types

import main


class TestModelsAndHelpers(unittest.TestCase):
    def test_person_str(self):
        p = main.Person('P001', 'Zhang San')
        self.assertIn('Zhang San', str(p))
        self.assertIn('P001', str(p))

    def test_express_str(self):
        sender = main.Person('S1', 'Sender')
        receiver = main.Person('R1', 'Receiver')
        e = main.Express('E001', '123456', sender, receiver, 'A-01', 'fragile', '在库')
        s = str(e)
        self.assertIn('E001', s)
        self.assertIn('123456', s)
        self.assertIn('Sender', s)
        self.assertIn('Receiver', s)

    def test_generate_express_id_format(self):
        # create a bare-bones instance (without running __init__)
        app = main.ExpressManagementSystem.__new__(main.ExpressManagementSystem)
        eid = main.ExpressManagementSystem.generate_express_id(app)
        # Should start with 'E' and contain digits
        self.assertTrue(eid.startswith('E'))
        self.assertTrue(re.match(r'^E\d+$', eid))

    def test_generate_pick_code_uniqueness(self):
        app = main.ExpressManagementSystem.__new__(main.ExpressManagementSystem)
        # simulate existing codes
        app.pick_code_dict = {str(i): f'E{i}' for i in range(100000, 100100)}

        # generate several codes and ensure none collide with existing ones
        codes = set()
        for _ in range(10):
            code = main.ExpressManagementSystem.generate_pick_code(app)
            self.assertIsInstance(code, str)
            self.assertEqual(len(code), 6)
            self.assertTrue(code.isdigit())
            self.assertNotIn(code, app.pick_code_dict)
            codes.add(code)

    def test_method_bindings_exist(self):
        # Verify that module-level functions were attached to the class
        expected = [
            'change_language', 'refresh_ui', 'create_all_tabs', 'apply_user_restrictions',
            'create_menu_bar', 'logout', 'exit_program', 'reset_security_key',
            'setup_in_tab', 'setup_out_tab', 'setup_query_tab', 'setup_list_tab',
            'add_express', 'change_theme', 'pick_up_express', 'query_express',
            'update_express_list', 'clear_in_fields', 'update_area_list', 'update_location_list',
            'update_storage_chart', 'show_area_dialog', 'setup_users_tab', 'sort_users',
            'update_users_list', 'on_user_select', 'add_user', 'modify_user', 'delete_user',
            'setup_stats_tab', 'update_stats', 'sort_treeview', 'read_qr_code', 'qr_read',
            'qr_read_for_pickup', 'qr_read_for_query'
        ]

        for name in expected:
            self.assertTrue(hasattr(main.ExpressManagementSystem, name), msg=f"Missing method: {name}")


if __name__ == '__main__':
    unittest.main()
