import enum
import io

from dataclasses import dataclass

from .serialize import sexp_from_stream, sexp_to_stream


@dataclass
class Var:
    index: int

    def __repr__(self):
        return "x%d" % self.index


def int_from_bytes(blob):
    size = len(blob)
    if size == 0 or size > 16:
        return 0
    return int.from_bytes(blob, "big", signed=True)


def int_to_bytes(v):
    byte_count = (v.bit_length() + 8) >> 3
    if byte_count > 16:
        raise ValueError("int too large: %d" % v)
    if v == 0:
        return b''
    return v.to_bytes(byte_count, "big", signed=True)


ATOM_TYPES = enum.IntEnum("ATOM_TYPES", "VAR BLOB LIST KEYWORD")


class SExp:
    item: object
    type: ATOM_TYPES

    def __init__(self, v):

        if isinstance(v, SExp):
            self.item = v.item
            self.type = v.type
            return

        def to_sexp(v):
            if isinstance(v, SExp):
                return v
            return SExp(v)

        if isinstance(v, int):
            v = int_to_bytes(v)

        if isinstance(v, bytes):
            self.item = v
            self.type = ATOM_TYPES.BLOB
        elif isinstance(v, Var):
            self.item = v.index
            self.type = ATOM_TYPES.VAR
        elif hasattr(v, "__iter__"):
            self.item = [to_sexp(_) for _ in v]
            self.type = ATOM_TYPES.LIST
        else:
            raise ValueError("bad type for %s" % v)

    @classmethod
    def from_stream(class_, f):
        return sexp_from_stream(f, class_)

    @classmethod
    def from_blob(class_, blob):
        return class_.from_stream(io.BytesIO(blob))

    @classmethod
    def from_var_index(class_, index):
        return class_(Var(index))

    def is_var(self):
        return self.type == ATOM_TYPES.VAR

    def is_bytes(self):
        return self.type == ATOM_TYPES.BLOB

    def is_list(self):
        return self.type == ATOM_TYPES.LIST

    def var_index(self):
        if self.is_var():
            return self.item

    def as_int(self):
        if self.is_bytes():
            return int_from_bytes(self.as_bytes())

    def as_bytes(self):
        if self.is_bytes():
            return self.item

    def as_list(self):
        if self.is_list():
            return self.item

    def as_bin(self):
        f = io.BytesIO()
        self.stream(f)
        return f.getvalue()

    def stream(self, f):
        sexp_to_stream(self, f)

    def __iter__(self):
        return self.as_list().__iter__()

    def as_obj(self):
        type = self.type
        if type == ATOM_TYPES.VAR:
            return Var(index=self.var_index())
        if type == ATOM_TYPES.BLOB:
            return self.item
        if type == ATOM_TYPES.LIST:
            return [_.as_obj() for _ in self.item]
        assert 0

    def __repr__(self):
        t = "??"
        if self.is_var():
            t = "x%d" % self.item
        if self.is_bytes():
            t = repr(self.item)
        if self.is_list():
            t = repr([_.as_obj() for _ in self.item])
        return "SExp(%s)" % t

    def __eq__(self, other):
        try:
            other = SExp(other)
        except ValueError:
            return False
        return other.type == self.type and other.item == self.item
