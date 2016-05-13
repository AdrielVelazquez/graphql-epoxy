from contextlib import contextmanager
from graphql.type import definition


def add_impl_to_interfaces(impl):
    for type in impl.get_interfaces():
        if not hasattr(type, "_impls"):
            type._impls = []
        type._impls.append(impl)


@contextmanager
def no_implementation_registration():
    old_definition = add_impl_to_interfaces
    definition.add_impl_to_interfaces = lambda type: None
    try:
        yield

    finally:
        definition.add_impl_to_interfaces = old_definition
