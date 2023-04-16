from unittest import TestCase, mock
from traffic_man.google.orig_dest_optimizer import OrigDestOptimizer

class TestOrigDestOptimizer(TestCase):

    ### --------------------- OrigDestOptimizer.__init__() ------------------
    def test_init_confirm_default_values(self):
        test_list = ["list_element1", "list_element2"]
        test_obj = OrigDestOptimizer(test_list)
        self.assertEqual(test_obj.orig_dest_data, test_list)
        self.assertEqual(test_obj.dest_limit, 25)
        self.assertEqual(test_obj.element_limit, 100)
    
    ### --------------------- OrigDestOptimizer._shape_data() ------------------
    def test_shape_data_works(self):
        test_orig_dest_list = [["orig1", "dest1"], ["orig1", "dest2"], ["orig2", "dest3"]]
        test_obj = OrigDestOptimizer(test_orig_dest_list)
        check_val = test_obj._shape_data()
        self.assertEqual(check_val, [[['orig1'], 2, [['dest1', 'dest2']]], [['orig2'], 1, [['dest3']]]])

    ### --------------------- OrigDestOptimizer._dest_breakdown() ------------------
    def test_dest_breakdown_works(self):
        test_shaped_data = [[['orig1'], 3, [['dest1', 'dest2', 'dest3']]], [['orig2'], 1, [['dest4']]]]
        test_obj = OrigDestOptimizer(["fake", "list"], dest_limit=2)
        check_val = test_obj._dest_breakdown(test_shaped_data)
        self.assertEqual(check_val, [[['orig1'], 1, [['dest3']]], [['orig1'], 2, [['dest1', 'dest2']]], [['orig2'], 1, [['dest4']]]])

    ### --------------------- OrigDestOptimizer._group_orig_dest() ------------------
    def test_group_orig_dest_hit_dest_limit(self):
        test_dest_list_breakdown = [
            [['orig1'], 3, [['dest1', 'dest2', 'dest3']]],
            [['orig1'], 1, [['dest4']]],
            [['orig2'], 2, [['dest5', 'dest6']]],
            [['orig3'], 2, [['dest7', 'dest8']]],
            [['orig4'], 2, [['dest9', 'dest10']]]
            ]
        test_obj = OrigDestOptimizer(["fake", "list"], dest_limit=3, element_limit=6)
        check_val = test_obj._group_orig_dest(test_dest_list_breakdown)
        self.assertEqual(check_val, 
            [
                [['orig1'], 3, [['dest1', 'dest2', 'dest3']]],
                [['orig4', 'orig1'], 3, [['dest9', 'dest10'], ['dest4']]],
                [['orig3'], 2, [['dest7', 'dest8']]],
                [['orig2'], 2, [['dest5', 'dest6']]]
            ]
        )
    
    def test_group_orig_dest_hit_element_limit(self):
        test_dest_list_breakdown = [
            [['orig1'], 3, [['dest1', 'dest2', 'dest3']]],
            [['orig1'], 1, [['dest4']]],
            [['orig2'], 2, [['dest5', 'dest6']]],
            [['orig3'], 2, [['dest7', 'dest8']]],
            [['orig4'], 2, [['dest9', 'dest10']]]
            ]
        test_obj = OrigDestOptimizer(["fake", "list"], dest_limit=4, element_limit=7)
        check_val = test_obj._group_orig_dest(test_dest_list_breakdown)
        self.assertEqual(check_val, 
            [
                [['orig1'], 3, [['dest1', 'dest2', 'dest3']]],
                [['orig4', 'orig1'], 3, [['dest9', 'dest10'], ['dest4']]],
                [['orig3'], 2, [['dest7', 'dest8']]],
                [['orig2'], 2, [['dest5', 'dest6']]]
            ]
        )

    ### --------------------- OrigDestOptimizer._verify_result() ------------------
    def test_verify_result_successfully_verified(self):
        orig_dest_list = [['orig1', 'dest1'], ['orig1', 'dest2'], ['orig1', 'dest3'], ['orig2', 'dest4'], ['orig3', 'dest1']]
        final_data = [
            [['orig1'], 2, [['dest1', 'dest2']]],
            [['orig1', 'orig2'], 2, [['dest3'], ['dest4']]],
            [['orig3'], 1, [['dest1']]]
        ]

        test_obj = OrigDestOptimizer(orig_dest_list)
        check_val = test_obj._verify_result(final_data)
        self.assertIs(check_val, True)

    def test_verify_result_fail(self):
        orig_dest_list = [['orig1', 'dest1'], ['orig1', 'dest2'], ['orig1', 'dest3'], ['orig2', 'dest4'], ['orig3', 'dest1']]
        final_data = [
            [['orig1'], 2, [['dest1', 'dest2']]],
            [['orig1', 'orig2'], 2, [['dest3'], ['dest4']]],
            [['orig3'], 1, [['dest8']]]
        ]

        test_obj = OrigDestOptimizer(orig_dest_list)
        check_val = test_obj._verify_result(final_data)
        self.assertIs(check_val, False)


    ### --------------------- OrigDestOptimizer.get_orig_dest_list() ------------------
    def test_get_orig_dest_list_except_shape_data(self):
        with mock.patch('traffic_man.google.orig_dest_optimizer.OrigDestOptimizer._shape_data', side_effect=Exception('fake exception')) as mock_shape_data:
            test_obj = OrigDestOptimizer(["fake", "list"])
            check_val = test_obj.get_orig_dest_list()
            self.assertIs(check_val, None)
    
    def test_get_orig_dest_list_except_dest_breakdown(self):
        with mock.patch('traffic_man.google.orig_dest_optimizer.OrigDestOptimizer._shape_data', return_value=["fake", "shaped","data"]) as mock_shape_data:
            with mock.patch('traffic_man.google.orig_dest_optimizer.OrigDestOptimizer._dest_breakdown', side_effect=Exception("fake exception")) as mock_dest_breakdown:
                test_obj = OrigDestOptimizer(["fake", "list"])
                check_val = test_obj.get_orig_dest_list()
                self.assertIs(check_val, None)

    def test_get_orig_dest_list_except_group_orig_dest(self):
        with mock.patch('traffic_man.google.orig_dest_optimizer.OrigDestOptimizer._shape_data', return_value=["fake", "shaped","data"]) as mock_shape_data:
            with mock.patch('traffic_man.google.orig_dest_optimizer.OrigDestOptimizer._dest_breakdown', return_value=["fake", "dest", "breakdown"]) as mock_dest_breakdown:
                with mock.patch('traffic_man.google.orig_dest_optimizer.OrigDestOptimizer._group_orig_dest', side_effect=Exception("fake exception")) as mock_group_orig_dest:
                    test_obj = OrigDestOptimizer(["fake", "list"])
                    check_val = test_obj.get_orig_dest_list()
                    self.assertIs(check_val, None)

    def test_get_orig_dest_list_fail_verify(self):
        with mock.patch('traffic_man.google.orig_dest_optimizer.OrigDestOptimizer._shape_data', return_value=["fake", "shaped","data"]) as mock_shape_data:
            with mock.patch('traffic_man.google.orig_dest_optimizer.OrigDestOptimizer._dest_breakdown', return_value=["fake", "dest", "breakdown"]) as mock_dest_breakdown:
                with mock.patch('traffic_man.google.orig_dest_optimizer.OrigDestOptimizer._group_orig_dest', return_value=["fake","group","list"]) as mock_group_orig_dest:
                    with mock.patch('traffic_man.google.orig_dest_optimizer.OrigDestOptimizer._verify_result', return_value=False) as mock_verify:
                        test_obj = OrigDestOptimizer(["fake", "list"])
                        check_val = test_obj.get_orig_dest_list()
                        self.assertIs(check_val, None)

    def test_get_orig_dest_list_success(self):
        with mock.patch('traffic_man.google.orig_dest_optimizer.OrigDestOptimizer._shape_data', return_value=["fake", "shaped","data"]) as mock_shape_data:
            with mock.patch('traffic_man.google.orig_dest_optimizer.OrigDestOptimizer._dest_breakdown', return_value=["fake", "dest", "breakdown"]) as mock_dest_breakdown:
                with mock.patch('traffic_man.google.orig_dest_optimizer.OrigDestOptimizer._group_orig_dest', return_value=["fake","group","list"]) as mock_group_orig_dest:
                    with mock.patch('traffic_man.google.orig_dest_optimizer.OrigDestOptimizer._verify_result', return_value=True) as mock_verify:
                        test_obj = OrigDestOptimizer(["fake", "list"])
                        check_val = test_obj.get_orig_dest_list()
                        self.assertEqual(check_val, ["fake","group","list"])