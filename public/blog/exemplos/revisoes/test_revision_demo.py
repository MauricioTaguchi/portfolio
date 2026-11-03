import unittest
from revision_demo import Conflict, History


class RevisionTests(unittest.TestCase):
    def setUp(self):
        self.h = History(b'original')
        self.h.apply(b'changed', expected=1)

    def test_restore_advances_revision(self):
        self.h.restore(1, expected=2, key='one')
        self.assertEqual(self.h.head.revision, 3)
        self.assertEqual(self.h.head.content, b'original')

    def test_retry_returns_same_receipt(self):
        first = self.h.restore(1, expected=2, key='one')
        self.assertEqual(self.h.restore(1, expected=2, key='one'), first)
        self.assertEqual(self.h.head.revision, 3)

    def test_receipt_survives_later_change(self):
        first = self.h.restore(1, expected=2, key='one')
        self.h.apply(b'later', expected=3)
        self.assertEqual(self.h.restore(1, expected=2, key='one'), first)
        self.assertEqual(self.h.head.revision, 4)
        self.assertEqual(self.h.head.content, b'later')

    def test_key_reuse_with_other_arguments_fails(self):
        self.h.restore(1, expected=2, key='one')
        with self.assertRaises(Conflict):
            self.h.restore(2, expected=3, key='one')
        self.assertEqual(self.h.head.revision, 3)

    def test_stale_expectation_fails(self):
        with self.assertRaises(Conflict):
            self.h.restore(1, expected=1, key='one')
        self.assertEqual(self.h.head.revision, 2)

    def test_unknown_snapshot_does_not_change_head(self):
        with self.assertRaises(ValueError):
            self.h.restore(9, expected=2, key='one')
        self.assertEqual(self.h.head.revision, 2)

    def test_empty_key_is_rejected(self):
        with self.assertRaises(ValueError):
            self.h.restore(1, expected=2, key=' ')
        self.assertEqual(self.h.head.revision, 2)

    def test_same_content_can_have_different_revisions(self):
        first_digest = History(b'original').head.digest
        self.h.restore(1, expected=2, key='one')
        self.assertEqual(self.h.head.digest, first_digest)
        self.assertEqual(self.h.head.revision, 3)

if __name__ == '__main__':
    unittest.main()
