from typing import TypeGuard

from musictool.note import Note


def is_frozenset_of_str(s: frozenset[object]) -> TypeGuard[frozenset[str]]:
    return all(isinstance(x, str) for x in s)


def is_frozenset_of_note(s: frozenset[object]) -> TypeGuard[frozenset[Note]]:
    return all(isinstance(x, Note) for x in s)
