from graphql.core.type.definition import GraphQLUnionType

from ..utils.no_implementation_registration import no_implementation_registration


class UnionMeta(type):
    def __new__(mcs, name, bases, attrs):
        if attrs.pop('abstract', False):
            return super(UnionMeta, mcs).__new__(mcs, name, bases, attrs)

        with no_implementation_registration():
            union_type = GraphQLUnionType(
                name,
                types=mcs._get_types(),
                description=attrs.get('__doc__'),
            )

        mcs._register(union_type)
        cls = super(UnionMeta, mcs).__new__(mcs, name, bases, attrs)
        cls.T = union_type
        cls._registry = mcs._get_registry()

        return cls

    @staticmethod
    def _register(union_type):
        raise NotImplementedError('_register must be implemented in the sub-metaclass')

    @staticmethod
    def _get_registry():
        raise NotImplementedError('_get_registry must be implemented in the sub-metaclass')

    @staticmethod
    def _get_types():
        return None
