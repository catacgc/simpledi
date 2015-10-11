from inspect import getargspec

"""
A basic implementation of a dependency injection container

Basic usage:

    class Foo(object):
        def __init__(bar, baz):
            self.sum = bar + baz

    container = new Container()
    container.foo = auto(Foo)
    container.bar = instance(1)
    container.baz = instance(3)

    container.foo.sum  # will print 4


"""


def auto(clz):
    return AutoProvider(clz)


def instance(obj):
    return lambda container: obj


def cache(provider):
    return CacheInstanceProvider(provider)


class Provider(object):
    """
    Base class that defines the protocol for a provider of an instance
    """

    def __call__(self, container):
        pass


class AutoProvider(Provider):
    """
    Builds the dependency by looking at the __init__ method arguments
    and trying to find dependencies in the container with the name of
    the arguments themselves
    """

    def __init__(self, clz):
        self.clz = clz

    def __call__(self, container):
        if '__init__' not in self.clz.__dict__:
            return self.clz()

        argspec = getargspec(self.clz.__init__)
        # ignore self
        dependencies = argspec.args[1:]

        return self.clz(*[container.get_instance(dependency) for dependency in dependencies])


class ListInstanceProvider(Provider):
    def __init__(self, *providers):
        self._providers = providers

    def add(self, *providers):
        self._providers.extend(providers)

    def __call__(self, container):
        return map(lambda provider: provider(container), self._providers)


class CacheInstanceProvider(Provider):
    def __init__(self, provider):
        self.provider = provider
        self.cache = None

    def __call__(self, container):
        if self.cache:
            return self.cache

        self.cache = self.provider(container)
        return self.cache


class Container(object):
    """Very simple dependency manager useful to manage constructor dependencies"""

    def __init__(self):
        self._providers = {}
        self._call_stack = []

    def __setattr__(self, name, provider):
        if name in set(['_providers', '_call_stack']):
            self.__dict__[name] = provider
            return

        if not hasattr(provider, '__call__'):
            raise Exception('A dependency provider must be callable and receive exactly one argument: the container')

        self._providers[name] = provider

    def __getattr__(self, name):
        return self.get_instance(name)

    def get_instance(self, name):
        if name in self.__dict__:
            return self.__dict__[name]

        if name not in self._providers:
            raise Exception('Dependency {name} is not defined: {call_stack}; bind one '
                            'using appContainer.{name} = ...'
                            .format(name=name, call_stack=format_call_stack(self._call_stack + [name + " (missing)"])))

        if name in self._call_stack:
            raise Exception('Cyclic dependency chain detected: {call_stack}'
                            .format(call_stack=format_call_stack(self._call_stack + [name + " (cycle)"])))

        return self._providers[name](self.clone(name))

    def get_provider(self, name):
        return self._providers[name]

    def clone(self, name):
        container = Container()
        container._call_stack = self._call_stack + [name]
        container._providers = self._providers

        return container


def format_call_stack(call_stack):
    return " -> ".join(call_stack)
