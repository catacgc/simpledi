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

def builder(clz, *dependencies):
    return InstanceProvider(clz, dependencies)

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

        return self.clz(*[container.get_instance(dependency, self.clz.__name__) for dependency in dependencies])


class InstanceProvider(Provider):
    """
    A do-it yourself dependency builder where you have to specify the class,
    and the list for the named dependencies that have to be passed to the constructor
    """

    def __init__(self, clz, dependencies=[]):
        self.dependencies = dependencies
        self.clz = clz

    def __call__(self, container):
        return self.clz(*[container.get_instance(dependency, self.clz.__name__) for dependency in self.dependencies])


class ListInstanceProvider(Provider):
    def __init__(self):
        self.providers = []

    def add(self, provider):
        self.providers.append(provider)

    def __call__(self, container):
        return map(lambda provider: provider(container), self.providers)


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

    providers = {}

    def __setattr__(self, key, value):
        self.bind(key, value)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]

        return self.get_instance(name)

    def bind(self, name, provider):
        if not hasattr(provider, '__call__'):
            raise Exception("A dependency provider must be callable and receive exactly one argument: the container")

        self.providers[name] = provider

    def get_provider(self, name):
        return self.providers[name]

    def get_instance(self, name, caller=None):
        if name not in self.providers:
            raise Exception("Dependency {caller}.{name} is not defined; bind one "
                            "using appContainer.{name} = ...".format(name=name, caller=caller))

        return self.providers[name](self)