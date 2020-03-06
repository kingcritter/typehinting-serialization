# Typehinting Serialization Test

## Backstory 

I had to write some (fairly simple) custom serialization code at work, and a coworker suggested using python typehints to mark the byte length of various fields, and then automatically serializing based on those.

My initial reaction was "that's brilliant" but then I started thinking about it and having doubts about whether it was a kosher thing to do, or just an abuse of the typehinting feature.

 Some of my doubts were assuaged by [PEP 520](https://www.python.org/dev/peps/pep-0520/) which provided a guarantee that you could access attributes in the order they were defined, and the PEP specifically calls out serialization as a motivating use-case. 
 
 That has nothing *directly* to do with typehinting, but it was a prerequisite and at least it shows that the Python developers think auto-serialization is a valid idea.
 
 I never ended up implementing it at work, so I decided to investigate this idea in my free time, and these are the results.
 
 ## Building Blocks
 
 Every object has a `__dict__` field, which is a dictionary (as of Python 3.6, an ordered dictionary) that holds the instance's `self` attributes. Classes and functions, if annotated, have an `__annotations__` attribute that maps attribute names to their type. Be aware, however, that for classes the annotations have to be defined at the class level. 
 
 ```python
from typing import List
class X: 
    one: str
    two: int
    three: List[int]
    def __init__(self): 
        self.one = "foo" 
        self.two = 42 
        self.three = [1, 2, 3]
x = X()
print(x.__dict__)
print(x.__annotations__)
```

Running the above prints out:

```
{'one': 'foo', 'two': 42, 'three': [1, 2, 3]}
{'one': str, 'two': int, 'three': typing.List[int]}
```

Since the annotations are at the class level, `X.__annotations__` would produce the same output.

## The Basic Idea

The basic idea is that I'll have classes for the data types I want to serialize, and these classes will have some kind of `serialize()`/`deserialize()` functions.

E.g. I'll have classes for the various integer types like short, int, long; a class for strings; a class for lists... you get the picture.

So let's get coding!

## Coding

A few things jumped out at me right off the bat.

1. all the attributes and methods of these type classes could be at the class level; they'd never be instantiated
2. the integer classes (short, int, long) were all the same thing aside from byte length, so they could be subclasses of a common integer class
   * maybe I could get fancy and use subscription to denote byte length, but I wasn't sure how that would work exactly 
 3. I'd have to handle types within types; e.g. a List of Strings
 
 I decided that each type class would have two methods: `serialize(item: T) -> bytes` and `deserialize(item: bytes) -> T`, where `T` is the python object we're serializing.
 
 However, when I got to implementing `deserialize` for my List type, I realized I had two problems:
 
 1. I'd need to accept a second parameter, `type_`, because otherwise I'd have no idea which deserializer to call for each item
 2. There was no way to tell in advance how many bytes a complicated object, like a String, would deserialize into, so I couldn't just slice the list item-by-item and pass the slices into the deserializers. 
 
 To solve issue #2, I decided to switch all the deserializers to accept `io.BytesIO` objects, which have read methods. This meant I could pass the entire contents of the list to a deserialize function, would read what it needed to, and the next deserializer would start where the last one left off. 
 
 I soon found out that I needed to wrap the `BytesIO` object in a `BufferedReader` so I could use `.peek(1)` to see if I was out of bytes to read.
 
 ## Current Status:
 
 It works, but typehinting isn't acting right; not sure if it's a limitation of Pycharm or a problem with how I'm doing things. For example, my `Integer` class subclasses `int`, and `Long` subclasses Integer.
 
 When writing the following...
 
 ```python
class X:
    one: s.Long
    def __init__(self):
        self.one = 123456789
```

...Pycharm gives the typehinting error: `Expected type 'Long', got 'int' instead`. Some quick googling suggests that I want to use `typing.Type[s.Long]`. But that doesn't work.

I also want to see if I can either subclass `typing.List` or make my `List` class subscriptable, so I don't need to use `typing.List` and have the list-specific logic in  `serialize_object`.