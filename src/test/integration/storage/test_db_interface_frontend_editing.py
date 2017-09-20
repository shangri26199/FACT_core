import unittest
from tempfile import TemporaryDirectory

from helperFunctions.config import get_config_for_testing
from storage.MongoMgr import MongoMgr
from storage.db_interface_backend import BackEndDbInterface
from storage.db_interface_frontend import FrontEndDbInterface
from storage.db_interface_frontend_editing import FrontendEditingDbInterface
from test.common_helper import create_test_firmware

TMP_DIR = TemporaryDirectory(prefix="faf_test_")


class TestStorageDbInterfaceFrontendEditing(unittest.TestCase):

    def setUp(self):
        self._config = get_config_for_testing(TMP_DIR)
        self.mongo_server = MongoMgr(config=self._config)
        self.db_frontend_editing = FrontendEditingDbInterface(config=self._config)
        self.db_frontend_interface = FrontEndDbInterface(config=self._config)
        self.db_backend_interface = BackEndDbInterface(config=self._config)

    def tearDown(self):
        self.db_backend_interface.client.drop_database(self._config.get('data_storage', 'main_database'))
        self.db_frontend_editing.shutdown()
        self.db_backend_interface.shutdown()
        self.mongo_server.shutdown()

    def test_add_comment(self):
        test_fw = create_test_firmware()
        self.db_backend_interface.add_object(test_fw)
        comment, author, uid, time = "this is a test comment!", "author", test_fw.get_uid(), 1234567890
        self.db_frontend_editing.add_comment_to_object(uid, comment, author, time)
        test_fw = self.db_backend_interface.get_object(uid)
        self.assertEqual(
            test_fw.comments[0],
            {"time": str(time), "author": author, "comment": comment}
        )

    def test_get_latest_comments(self):
        comments = [
            {"time": "1234567890", "author": "author1", "comment": "test comment"},
            {"time": "1234567899", "author": "author2", "comment": "test comment2"}
        ]
        test_fw = self._add_test_fw_with_comments_to_db()
        latest_comments = self.db_frontend_interface.get_latest_comments()
        comments.sort(key=lambda x: x["time"], reverse=True)
        for i in range(len(comments)):
            time, author, comment, uid = comments[i]["time"], comments[i]["author"], comments[i]["comment"], test_fw.get_uid()
            self.assertEqual(latest_comments[i]["time"], time)
            self.assertEqual(latest_comments[i]["author"], author)
            self.assertEqual(latest_comments[i]["comment"], comment)
            self.assertEqual(latest_comments[i]["uid"], uid)

    def test_remove_element_from_array_in_field(self):
        test_fw = self._add_test_fw_with_comments_to_db()
        retrieved_fw = self.db_backend_interface.get_object(test_fw.get_uid())
        self.assertEqual(len(retrieved_fw.comments), 2, "comments were not saved correctly")

        self.db_frontend_editing.remove_element_from_array_in_field(test_fw.get_uid(), "comments", {"time": "1234567899"})
        retrieved_fw = self.db_backend_interface.get_object(test_fw.get_uid())
        self.assertEqual(len(retrieved_fw.comments), 1, "comment was not deleted")

    def test_delete_comment(self):
        test_fw = self._add_test_fw_with_comments_to_db()
        retrieved_fw = self.db_backend_interface.get_object(test_fw.get_uid())
        self.assertEqual(len(retrieved_fw.comments), 2, "comments were not saved correctly")

        self.db_frontend_editing.delete_comment(test_fw.get_uid(), "1234567899")
        retrieved_fw = self.db_backend_interface.get_object(test_fw.get_uid())
        self.assertEqual(len(retrieved_fw.comments), 1, "comment was not deleted")

    def _add_test_fw_with_comments_to_db(self):
        test_fw = create_test_firmware()
        comments = [
            {"time": "1234567890", "author": "author1", "comment": "test comment"},
            {"time": "1234567899", "author": "author2", "comment": "test comment2"}
        ]
        test_fw.comments.extend(comments)
        self.db_backend_interface.add_object(test_fw)
        return test_fw
