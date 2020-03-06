import typing
from io import BytesIO, BufferedReader


class Integer(int):
    length: int

    @classmethod
    def serialize(cls, number: int) -> bytes:
        return number.to_bytes(cls.length, "big")

    @classmethod
    def deserialize(cls, number: BytesIO) -> int:
        return int.from_bytes(number.read(cls.length), "big")


class ByteInt(Integer):
    length: int = 1


class Short(Integer):
    length: int = 2


class Int(Integer):
    length: int = 4


class Long(Integer):
    length: int = 8


class String(str):
    # Strings are encoded with their length as the first two bytes. This matches Java's built
    # in string serialization.
    size_length = 2

    @classmethod
    def serialize(cls, string: str) -> bytes:
        return len(string).to_bytes(2, "big") + bytes(string, "utf-8")

    @classmethod
    def deserialize(cls, string: BytesIO) -> str:
        length = int.from_bytes(string.read(cls.size_length), "big")
        return string.read(length).decode("utf-8")


class List:
    # The list is serialized with the first 4 bytes containing the length of the list
    size_length = 4

    @classmethod
    def serialize(cls, list_: list, type_) -> bytes:
        length = len(list_).to_bytes(cls.size_length, "big")
        items = bytes()
        for x in list_:
            items += type_.serialize(x)
        return length + items

    @classmethod
    def deserialize(cls, list_: BytesIO, type_) -> typing.List:
        # We need to know the type of the objects contained in the list,
        # otherwise we'd have no idea how to deserialize it.

        # We wrap the BytesIO in a BufferedReader to get the .peek() method.
        list_ = BufferedReader(list_)

        length = int.from_bytes(list_.read(cls.size_length), "big")
        items = []
        while list_.peek(1) != b"":
            i = type_.deserialize(list_)
            if i == b"":
                break
            items.append(i)

        return items


def serialize_object(item):
    """
    This functions accepts an instance of a class whose attributes have all been
    annotated, and all the annotations are from the set defined in this module.
    """
    bytes_ = bytes()

    for attribute in item.__dict__:
        clazz = item.__annotations__[attribute]
        if issubclass(clazz, typing.List):
            clazz = clazz.__args__[0]
            print((item.__getattribute__(attribute)))
            bytes_ += List.serialize(item.__getattribute__(attribute), clazz)
        else:
            bytes_ += clazz.serialize(item.__getattribute__(attribute))

    return bytes_
