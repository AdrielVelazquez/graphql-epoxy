from graphql.core.type.definition import GraphQLObjectType, GraphQLNonNull, GraphQLList
from graphql.core.type.scalars import GraphQLString
from epoxy.registry import TypeRegistry


def test_register_single_type():
    R = TypeRegistry()

    class Dog(R.ObjectType):
        name = R.Field(R.String)

    assert isinstance(Dog.T, GraphQLObjectType)
    assert R.type('Dog') is Dog.T

    fields = Dog.T.get_fields()
    assert list(fields.keys()) == ['name']
    assert fields['name'].type == GraphQLString
    assert fields['name'].name == 'name'


def test_register_type_can_declare_builtin_scalar_types_directly():
    R = TypeRegistry()

    class Dog(R.ObjectType):
        name = R.String


    fields = Dog.T.get_fields()
    assert list(fields.keys()) == ['name']
    assert fields['name'].type == GraphQLString
    assert fields['name'].name == 'name'


def test_register_type_can_declare_builtin_scalar_type_as_non_null():
    R = TypeRegistry()

    class Dog(R.ObjectType):
        name = R.String.NonNull

    fields = Dog.T.get_fields()
    assert list(fields.keys()) == ['name']
    assert str(fields['name'].type) == 'String!'


def test_register_type_can_declare_other_registered_types_directly():
    R = TypeRegistry()

    class Dog(R.ObjectType):
        friend = R.Dog

    fields = Dog.T.get_fields()
    assert list(fields.keys()) == ['friend']
    assert fields['friend'].type == Dog.T
    assert fields['friend'].name == 'friend'


def test_register_type_can_declare_other_registered_types_directly_as_non_null():
    R = TypeRegistry()

    class Dog(R.ObjectType):
        friend = R.Dog.NonNull

    fields = Dog.T.get_fields()
    assert list(fields.keys()) == ['friend']
    type = fields['friend'].type
    assert isinstance(type, GraphQLNonNull)
    assert type.of_type == Dog.T
    assert fields['friend'].name == 'friend'
    assert str(type) == 'Dog!'


def test_register_type_can_declare_other_registered_types_directly_as_list():
    R = TypeRegistry()

    class Dog(R.ObjectType):
        friend = R.Dog.List

    fields = Dog.T.get_fields()
    assert list(fields.keys()) == ['friend']
    type = fields['friend'].type
    assert isinstance(type, GraphQLList)
    assert type.of_type == Dog.T
    assert fields['friend'].name == 'friend'
    assert str(type) == '[Dog]'


def test_register_type_can_declare_other_registered_types_directly_as_list_of_non_null():
    R = TypeRegistry()

    class Dog(R.ObjectType):
        friend = R.Dog.NonNull.List

    fields = Dog.T.get_fields()
    assert list(fields.keys()) == ['friend']
    assert fields['friend'].name == 'friend'
    type = fields['friend'].type
    assert str(type) == '[Dog!]'

    assert isinstance(type, GraphQLList)
    type = type.of_type
    assert isinstance(type, GraphQLNonNull)
    assert type.of_type == Dog.T


def test_register_type_can_declare_other_registered_types_directly_as_non_null_list_of_non_null():
    R = TypeRegistry()

    class Dog(R.ObjectType):
        friend = R.Dog.NonNull.List.NonNull

    fields = Dog.T.get_fields()
    assert list(fields.keys()) == ['friend']
    assert fields['friend'].name == 'friend'
    type = fields['friend'].type
    assert str(type) == '[Dog!]!'

    assert isinstance(type, GraphQLNonNull)
    type = type.of_type
    assert isinstance(type, GraphQLList)
    type = type.of_type
    assert isinstance(type, GraphQLNonNull)
    assert type.of_type == Dog.T