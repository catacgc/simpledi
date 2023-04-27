Simple, small dependency injection container for python

## Basics

```syntax:python

class Users(object):

    def __init__(self, connection):
        self.connection = connection
        
    def fetch(self, limit=10):
        return self.connection....
        
class Connection(object):
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

# configuration
from simpledi import Container

container = Container()
container.users = lambda c: Users(c.connection)
container.connection = lambda c: Connection(c.username, c.password)
container.username = lambda c: read_userame()
container.password = lambda c: read_password()

# usage
container.users.fetch()
```

## Providers

The core concept of the container is the Provider which is a glorified callable that receives
 the container as the first argument. As simple as it is, this simple concept allow to create
  some more advanced providers that are explained below:
  
### The AutoProvider

Receives a class name as it's only argument and, based on the name of the arguments of `__init__` constructor, it 
 creates the instance when called auto-providing the needed dependencies. For the example above, we can simple 
 replace the manual provider methods for Users and Connections with the "auto" provider method:
 
```syntax:python

from simpledi import auto

container.users = auto(Users)
container.connnection = auto(Connection)
```
 
### The CacheProvider

For the example above, creating the connection each time might not be ideal; The `cache` provider it's simple provider
that caches the result of the first call of the provider it wraps:
 
```syntax:python

container.connection = cache(auto(Connection))

# same connection instance each time
assert container.connection == container.connection 
```
 
### The InstanceProvider

Sometimes you just want to bind simple instances into container; as an example, if one of your dependencies
is a simple string, you can bind it with `container.my_string = lambda c: "a_string"`. You can use the `instance`
provider to do the exact same thing:

```
container.my_string = instance("a string")
container.my_number = instance(42)
```

### The ListInstanceProvider

You dependency might sometimes be a list of things; plugin architectures are a good example. Let's say we have an image
 conversion utility class that accepts a list of convertors as it dependencies and calls each one.
  
```syntax:python
class ImageProcessor(object):
    
    def __init__(self, image_processors):
        self.image_processors = image_processors
        
    def process(self, imageurl):
        for processor in self.image_processors:
            self.image_processors.process(imageurl)
```

Now to wire everything up and allow for a an extension point in our application we can do:
 
```syntax:python

container = Container()
container.image_processor = auto(ImageProcessor)
container.image_processors = ListInstanceProvider(
    auto(JpegProcessor),
    auto(PngProcessor)
)


# somewere down below, based on a configurtion flag or something:
container.get_provider('image_processors').add(auto(AsciiProcessor))


# and your image processor will be wired with the 3 image processors you configured
container.image_processor.process("http://....")
```
