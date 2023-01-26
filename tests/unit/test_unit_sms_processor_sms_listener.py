import unittest, mock
from traffic_man.sms_processor.sms_listener import SMSListener

class TestSMSListener(unittest.TestCase):
    ### ---------------- SMSListener.get_message() ----------------
    def test_unit_get_message_except_xreadgroup(self):
        mock_redis_con = mock.Mock()
        mock_redis_con.xreadgroup.side_effect = Exception("xreadgroup exception")

        mock_kill_q = mock.Mock()
        mock_kill_q.empty.side_effect = [True, False]

        mock_inbound_sms_q = mock.Mock()
        SMSListener.get_message(mock_redis_con, "fake_stream_key", "fake_cons_grp", "fake_cons_name", 1, 1000, mock_inbound_sms_q, mock_kill_q )
        self.assertEqual(mock_inbound_sms_q.put.call_count, 0)

    def test_unit_get_message_two_messages(self):
        test_stream_data = [
            [ 'fake_stream_key', 
                [
                    ('msg-id1', {'msg-key1': 'msg-val1', 'msg-key2': 'msg-val2'}),
                    ('msg-id2', {'msg-key1': 'msg-val1', 'msg-key2': 'msg-val2'}),
                ]
            ]
        ]
        
        mock_redis_con = mock.Mock()
        mock_redis_con.xreadgroup.return_value = test_stream_data

        mock_kill_q = mock.Mock()
        mock_kill_q.empty.side_effect = [True, False]

        mock_inbound_sms_q = mock.Mock()
        SMSListener.get_message(mock_redis_con, "fake_stream_key", "fake_cons_grp", "fake_cons_name", 2, 1000, mock_inbound_sms_q, mock_kill_q )
        self.assertEqual(mock_inbound_sms_q.put.call_count, 2)

        