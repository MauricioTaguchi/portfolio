"""An in-memory teaching model, not the DataFlow implementation (Python 3.11+)."""
from dataclasses import dataclass
import hashlib


@dataclass(frozen=True)
class Snapshot:
    revision: int
    content: bytes

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.content).hexdigest()


@dataclass(frozen=True)
class Receipt:
    previous_revision: int
    result_revision: int
    restored_from: int


class Conflict(ValueError):
    """The caller's expected revision or reused request key does not match."""


class History:
    def __init__(self, content: bytes):
        self._snapshots = [Snapshot(1, bytes(content))]
        self._receipts: dict[str, tuple[tuple[int, int], Receipt]] = {}

    @property
    def head(self) -> Snapshot:
        return self._snapshots[-1]

    def apply(self, content: bytes, *, expected: int) -> Snapshot:
        if expected != self.head.revision:
            raise Conflict('The current revision has changed.')
        self._snapshots.append(Snapshot(self.head.revision + 1, bytes(content)))
        return self.head

    def restore(self, target: int, *, expected: int, key: str) -> Receipt:
        if not key.strip():
            raise ValueError('A nonempty request key is required in this example.')
        request = (target, expected)
        if key in self._receipts:
            previous_request, receipt = self._receipts[key]
            if previous_request != request:
                raise Conflict('Request key reused with different arguments.')
            return receipt
        if expected != self.head.revision:
            raise Conflict('The current revision has changed.')
        if not 1 <= target <= len(self._snapshots):
            raise ValueError('Unknown target revision.')
        snapshot = self.apply(self._snapshots[target - 1].content, expected=expected)
        receipt = Receipt(expected, snapshot.revision, target)
        self._receipts[key] = (request, receipt)
        return receipt


def main() -> None:
    history = History(b'original')
    original_digest = history.head.digest
    history.apply(b'transformed', expected=1)
    receipt = history.restore(1, expected=2, key='restore-001')
    assert history.head.content == b'original'
    assert history.head.revision == 3
    assert history.head.digest == original_digest
    history.apply(b'next change', expected=3)
    replay = history.restore(1, expected=2, key='restore-001')
    assert replay == receipt
    assert history.head.revision == 4
    print('Restored original content as revision 3; replay kept head at revision 4.')


if __name__ == '__main__':
    main()
