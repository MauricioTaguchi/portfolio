# Content is not revision

An in-memory teaching model, separate from DataFlow's implementation. Python 3.11 or later; no third-party packages.

```sh
python -B -m unittest -v
python -B revision_demo.py
```

Expected output: `Restored original content as revision 3; replay kept head at revision 4.`

The sequence creates revision 1, applies revision 2 and restores the content of revision 1 as revision 3. After a later change, replaying the same request returns the captured receipt without changing revision 4.

Eight tests cover revision advancement, replay, key conflicts, stale expected versions, unknown targets, empty keys and content identity. They do not verify transactions, multiple processes, persistence, authorization, crash recovery, retention or corruption. Keys here belong to one instance; a production design must define scope by actor, resource and operation.

Project reference: https://github.com/MauricioTaguchi/data-analytics-platform/blob/main/docs/AUDIT_RECEIPTS.md
