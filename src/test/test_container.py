import pytest

from simpledi import Container, auto, instance, cache, ListInstanceProvider


def test_lambda_providers():
    container = Container()
    container.foo = lambda c: 1
    container.bar = lambda c: 2
    container.baz = lambda c: c.foo + c.bar

    assert container.baz == 3


def test_cache_provider():
    def random():
        import random
        return random.random()

    container = Container()
    container.counter = lambda c: random()
    assert container.counter != container.counter

    container.counter = cache(lambda c: random())
    assert container.counter == container.counter


def test_instance_provider():
    container = Container()
    container.result = lambda c: c.func(2, 4)

    container.func = instance(lambda a, b: a + b)
    assert container.result == 6

    container.func = instance(lambda a, b: a * b)
    assert container.result == 8


def test_constructor_wiring():
    class Foo(object):
        def __init__(self, bar):
            self.bar = bar

    class Bar(object):
        def __init__(self, baz):
            self.baz = baz

    def baz(a_string):
        return a_string

    container = Container()
    container.foo = auto(Foo)
    container.bar = auto(Bar)
    container.baz = instance(baz)
    container.a_baz_dependency = instance('a baz thing')

    assert container.foo.bar.baz(container.a_baz_dependency) == 'a baz thing'


def test_list_instance_provider():
    class Foo(object):
        def __init__(self, numbers):
            self.numbers = numbers

        def sum(self):
            return sum(self.numbers)

    container = Container()
    container.foo = auto(Foo)
    container.numbers = ListInstanceProvider(
        lambda c: 1,
        instance(2),
        lambda c: c.three
    )
    container.three = instance(3)

    assert container.foo.sum() == 6


def test_empty_list_instance_provider():
    container = Container()
    container.members = ListInstanceProvider()
    container.get_provider('members').add(instance(1))
    container.get_provider('members').add(instance(2))

    assert container.members == [1, 2]


def test_missing_dependency():
    container = Container()
    container.foo = lambda c: c.bar
    container.bar = lambda c: c.baz
    container.baz = lambda c: c.a_missing_dependency

    try:
        container.foo
        pytest.fail("Should not be here")
    except Exception as e:
        assert 'foo -> bar -> baz -> a_missing_dependency (missing)' in str(e)


def test_cyclic_dependencies():
    container = Container()
    container.foo = lambda c: c.bar
    container.bar = lambda c: c.foo

    try:
        container.bar
        pytest.fail('Should not be here')
    except Exception as e:
        assert 'bar -> foo -> bar (cycle)' in str(e)


def test_wrong_provider_type():
    container = Container()

    try:
        container.a = 1
        pytest.fail('Should not get here')
    except Exception as e:
        pass
