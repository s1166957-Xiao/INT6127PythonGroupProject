import unittest
from unittest.mock import patch
import tkinter as tk

import area_dialog


class FakeDB:
    def __init__(self, areas=None):
        # areas: list of tuples as expected by load_areas
        self.areas = areas or []
        self.added = []
        self.updated = []
        self.deleted = {}

    def get_all_areas(self):
        return list(self.areas)

    def add_area(self, area_id, area_name, capacity, description):
        # simulate failure if area_id already exists
        if any(a[0] == area_id for a in self.areas):
            return False
        self.areas.append((area_id, area_name, capacity, 0, '', description))
        self.added.append((area_id, area_name, capacity, description))
        return True

    def update_area(self, area_id, area_name, capacity, description):
        for i, a in enumerate(self.areas):
            if a[0] == area_id:
                self.areas[i] = (area_id, area_name, capacity, a[3], a[4], description)
                self.updated.append((area_id, area_name, capacity, description))
                return True
        return False

    def delete_area(self, area_id):
        for i, a in enumerate(self.areas):
            if a[0] == area_id:
                del self.areas[i]
                return True, f"Area {area_id} deleted"
        return False, "Area not found"


class TestAreaDialog(unittest.TestCase):
    def setUp(self):
        # create root and hide it to avoid visible windows
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_validate_input_missing_and_invalid(self):
        db = FakeDB()
        dlg = area_dialog.AreaDialog(self.root, db)

        # empty fields -> invalid
        dlg.area_id_var.set("")
        dlg.area_name_var.set("")
        dlg.capacity_var.set("")
        with patch('area_dialog.messagebox.showerror') as mock_err:
            self.assertFalse(dlg.validate_input())
            mock_err.assert_called()

        # invalid capacity -> showerror
        dlg.area_id_var.set('A1')
        dlg.area_name_var.set('Area 1')
        dlg.capacity_var.set('not-a-number')
        with patch('area_dialog.messagebox.showerror') as mock_err:
            self.assertFalse(dlg.validate_input())
            mock_err.assert_called()

        # zero or negative capacity
        dlg.capacity_var.set('0')
        with patch('area_dialog.messagebox.showerror') as mock_err:
            self.assertFalse(dlg.validate_input())
            mock_err.assert_called()

        # valid
        dlg.capacity_var.set('10')
        with patch('area_dialog.messagebox.showerror') as mock_err:
            self.assertTrue(dlg.validate_input())
            mock_err.assert_not_called()

    def test_load_areas_populates_tree(self):
        areas = [
            ('R1', 'Region One', 5, 1, '货位 1', 'desc1'),
            ('R2', 'Region Two', 3, 2, '货位 1,货位 2', 'desc2')
        ]
        db = FakeDB(areas=areas)
        dlg = area_dialog.AreaDialog(self.root, db)

        # tree should have two items
        items = dlg.tree.get_children()
        self.assertEqual(len(items), 2)
        vals = [dlg.tree.item(i)['values'][0] for i in items]
        self.assertIn('R1', vals)
        self.assertIn('R2', vals)

    def test_add_area_success_and_failure(self):
        db = FakeDB()
        dlg = area_dialog.AreaDialog(self.root, db)

        dlg.area_id_var.set('A100')
        dlg.area_name_var.set('Area100')
        dlg.capacity_var.set('4')
        dlg.description_var.set('Desc')

        with patch('area_dialog.messagebox.showinfo') as mock_info, \
             patch('area_dialog.messagebox.showerror') as mock_err:
            dlg.add_area()
            mock_info.assert_called()
            self.assertIn(('A100', 'Area100', 4, 'Desc'), db.added)

        # try to add again -> failure
        dlg.area_id_var.set('A100')
        dlg.area_name_var.set('Area100')
        dlg.capacity_var.set('4')
        dlg.description_var.set('Desc')
        with patch('area_dialog.messagebox.showerror') as mock_err:
            dlg.add_area()
            mock_err.assert_called()

    def test_update_area_no_selection_shows_warning(self):
        areas = [('X1', 'X', 2, 0, '', 'd')]
        db = FakeDB(areas=areas)
        dlg = area_dialog.AreaDialog(self.root, db)

        # ensure nothing selected
        dlg.tree.selection_remove(dlg.tree.selection())
        with patch('area_dialog.messagebox.showwarning') as mock_warn:
            dlg.update_area()
            mock_warn.assert_called()

    def test_delete_area_flow(self):
        areas = [('D1', 'Del', 2, 0, '', 'd')]
        db = FakeDB(areas=areas)
        dlg = area_dialog.AreaDialog(self.root, db)

        # select the first item
        first = dlg.tree.get_children()[0]
        dlg.tree.selection_set(first)

        # confirm deletion -> True
        with patch('area_dialog.messagebox.askyesno', return_value=True) as mock_confirm, \
             patch('area_dialog.messagebox.showinfo') as mock_info:
            dlg.delete_area()
            mock_confirm.assert_called()
            mock_info.assert_called()

        # attempt delete when not exists -> askyesno True but db returns False
        # insert a new fake item and set db to not find it
        dlg.tree.insert('', 'end', values=('NOT_EXISTS', 'N', 1, 0, '', 'd'))
        new_item = dlg.tree.get_children()[-1]
        dlg.tree.selection_set(new_item)
        # patch db.delete_area to return failure
        with patch.object(db, 'delete_area', return_value=(False, 'fail')) as mock_del, \
             patch('area_dialog.messagebox.askyesno', return_value=True), \
             patch('area_dialog.messagebox.showerror') as mock_err:
            dlg.delete_area()
            mock_err.assert_called()


if __name__ == '__main__':
    unittest.main()
