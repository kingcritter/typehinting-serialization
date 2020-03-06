import serialization as s
import pytest
from io import BytesIO
import typing


def test_ByteInt_serialization():
    assert s.ByteInt.serialize(0) == int(0).to_bytes(1, "big")
    assert s.ByteInt.serialize(42) == int(42).to_bytes(1, "big")
    assert s.ByteInt.serialize(255) == int(255).to_bytes(1, "big")


def test_ByteInt_serialization_underflow():
    with pytest.raises(OverflowError):
        s.ByteInt.serialize(-1)


def test_ByteInt_serialization_overflow():
    with pytest.raises(OverflowError):
        s.ByteInt.serialize(256)


def test_ByteInt_deserialization():
    n = BytesIO(int(42).to_bytes(1, "big"))
    assert s.ByteInt.deserialize(n) == 42


def test_Short_serialization():
    assert s.Short.serialize(0) == int(0).to_bytes(2, "big")
    assert s.Short.serialize(1234) == int(1234).to_bytes(2, "big")
    assert s.Short.serialize(65535) == int(65535).to_bytes(2, "big")


def test_Short_serialization_underflow():
    with pytest.raises(OverflowError):
        s.Short.serialize(-1)


def test_Short_serialization_overflow():
    with pytest.raises(OverflowError):
        s.Short.serialize(65536)


def test_Short_deserialization():
    n = 1234
    n_bytes = BytesIO(int(n).to_bytes(2, "big"))
    assert s.Short.deserialize(n_bytes) == n


def test_Int_serialization():
    assert s.Int.serialize(0) == int(0).to_bytes(4, "big")
    assert s.Int.serialize(1234) == int(1234).to_bytes(4, "big")
    assert s.Int.serialize(4294967295) == int(4294967295).to_bytes(4, "big")


def test_Int_serialization_underflow():
    with pytest.raises(OverflowError):
        s.Int.serialize(-1)


def test_Int_serialization_overflow():
    with pytest.raises(OverflowError):
        s.Int.serialize(4294967296)


def test_Int_deserialization():
    n = 1234
    n_bytes = BytesIO(int(n).to_bytes(4, "big"))
    assert s.Int.deserialize(n_bytes) == n


def test_Long_serialization():
    assert s.Long.serialize(0) == int(0).to_bytes(8, "big")
    assert s.Long.serialize(3453473354) == int(3453473354).to_bytes(8, "big")
    assert s.Long.serialize(18446744073709551615) == int(18446744073709551615).to_bytes(
        8, "big"
    )


def test_Long_serialization_underflow():
    with pytest.raises(OverflowError):
        s.Long.serialize(-1)


def test_Long_serialization_overflow():
    with pytest.raises(OverflowError):
        s.Long.serialize(18446744073709551616)


def test_Long_deserialization():
    n = 123456789
    n_bytes = BytesIO(int(n).to_bytes(8, "big"))
    assert s.Long.deserialize(n_bytes) == n


def test_String_serialization():
    x = "foobar"
    assert s.String.serialize(x) == len(x).to_bytes(2, "big") + bytes(x, "utf-8")


def test_String_deserialization():
    x = "foobar"
    x_bytes = BytesIO(len(x).to_bytes(2, "big") + bytes(x, "utf-8"))
    assert s.String.deserialize(x_bytes) == x


def test_serialize_List_of_Ints():
    x = [1, 1234, 123456]
    x_bytes = len(x).to_bytes(4, "big") + b"".join([x.to_bytes(4, "big") for x in x])
    assert s.List.serialize(x, s.Int) == x_bytes


def test_deserialize_List_of_Ints():
    x = [1, 1234, 123456]
    x_bytes = len(x).to_bytes(4, "big") + b"".join([x.to_bytes(4, "big") for x in x])
    assert s.List.deserialize(BytesIO(x_bytes), s.Int) == x


def test_serialize_List_of_Strings():
    x = ["one", "two", "three"]
    x_bytes = len(x).to_bytes(4, "big") + b"".join(
        [len(x).to_bytes(2, "big") + bytes(x, "utf-8") for x in x]
    )
    assert s.List.serialize(x, s.String) == x_bytes


def test_serialize_object():
    class X:
        one: s.Long
        two: typing.List[s.String]
        three: s.ByteInt

        def __init__(self):
            self.one = 123456789
            self.two = ["one", "two", "three"]
            self.three = 99

    x = X()
    x_bytes = (
        x.one.to_bytes(8, "big")
        + int(3).to_bytes(4, "big")
        + b"".join([len(x).to_bytes(2, "big") + bytes(x, "utf-8") for x in x.two])
        + x.three.to_bytes(1, "big")
    )
    assert s.serialize_object(x) == x_bytes
