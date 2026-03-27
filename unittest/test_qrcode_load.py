import unittest
import tempfile
import os
from types import SimpleNamespace
from unittest.mock import patch

import qrcode_load


class TestParseExpressData(unittest.TestCase):
    def test_key_value_equals(self):
        s = "express_id=E100\npick_code=123456\nsender=SID\nreceiver=RID\nlocation=A1\nnotes=fragile"
        res = qrcode_load.parse_express_data(s)
        self.assertEqual(res['express_id'], 'E100')
        self.assertEqual(res['pick_code'], '123456')
        self.assertEqual(res['sender'], 'SID')
        self.assertEqual(res['receiver'], 'RID')
        self.assertEqual(res['location'], 'A1')
        self.assertEqual(res['notes'], 'fragile')

    def test_key_value_colon(self):
        s = "Express: E200\nPick: 654321\nSender: S2\nReceiver: R2\nLocation: B2\nNote: none"
        res = qrcode_load.parse_express_data(s)
        self.assertEqual(res['express_id'], 'E200')
        self.assertEqual(res['pick_code'], '654321')
        self.assertEqual(res['location'], 'B2')

    def test_csv_format(self):
        # CSV with at least 8 parts
        csv = 'E300,111111,S3,Sender3,R3,Receiver3,Loc3,remark'
        res = qrcode_load.parse_express_data(csv)
        self.assertEqual(res['express_id'], 'E300')
        self.assertEqual(res['pick_code'], '111111')
        self.assertEqual(res['sender'], 'S3')
        self.assertEqual(res['sender_name'], 'Sender3')
        self.assertEqual(res['receiver'], 'R3')
        self.assertEqual(res['receiver_name'], 'Receiver3')
        self.assertEqual(res['location'], 'Loc3')
        self.assertEqual(res['notes'], 'remark')

    def test_unknown_format_returns_default(self):
        s = 'just some random string'
        res = qrcode_load.parse_express_data(s)
        # default keys exist but values empty
        self.assertIn('express_id', res)
        self.assertEqual(res['express_id'], '')


class TestReadExpressQrCode(unittest.TestCase):
    def setUp(self):
        # create a temporary "image" file (content doesn't matter because we patch imdecode)
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(b'notreallyanimage')
        f.close()
        self.temp_path = f.name

    def tearDown(self):
        try:
            os.remove(self.temp_path)
        except Exception:
            pass

    def test_read_with_empty_path_returns_none(self):
        self.assertIsNone(qrcode_load.read_express_qr_code(''))

    def test_read_when_imdecode_returns_none(self):
        # simulate cv2.imdecode returning None
        with patch.object(qrcode_load.cv2, 'imdecode', return_value=None):
            self.assertIsNone(qrcode_load.read_express_qr_code(self.temp_path))

    def test_read_json_payload_success(self):
        payload = {'express_id': 'E1', 'pick_code': '000001'}
        data_bytes = ( __import__('json').dumps(payload) ).encode('utf-8')

        # make decode return an object with .data attribute
        fake_decoded = [SimpleNamespace(data=data_bytes)]

        with patch.object(qrcode_load.cv2, 'imdecode', return_value=object()), \
             patch('qrcode_load.decode', return_value=fake_decoded):
            res = qrcode_load.read_express_qr_code(self.temp_path)
            self.assertIsInstance(res, dict)
            self.assertEqual(res.get('express_id'), 'E1')

    def test_read_nonjson_parsed_by_parser(self):
        # craft a non-json kv string
        s = 'express_id:E900\npick_code:900900\nsender:SX'
        fake_decoded = [SimpleNamespace(data=s.encode('utf-8'))]

        with patch.object(qrcode_load.cv2, 'imdecode', return_value=object()), \
             patch('qrcode_load.decode', return_value=fake_decoded):
            res = qrcode_load.read_express_qr_code(self.temp_path)
            self.assertIsInstance(res, dict)
            self.assertEqual(res.get('express_id'), 'E900')


if __name__ == '__main__':
    unittest.main()
