from graphql.type.definition import GraphQLObjectType
import six
from ...bases.mutation import MutationBase
from .connections import connection_args
from .metaclasses.mutation import RelayMutationMeta
from .utils import base64, unbase64


class RelayMixin(object):
    def __init__(self, registry, data_source):
        self.R = registry
        self.data_source = data_source
        self._node_field = None
        self._connections = {}
        self.Mutation = self._create_mutation_type_class()

    @property
    def NodeField(self):
        return self.R.Field(
            self.R.Node,
            description='Fetches an object given its ID',
            args={
                'id': self.R.ID.NonNull(description='The ID of an object')
            },
            resolver=lambda obj, args, info: self.fetch_node(args.get('id'), info)
        )

    def get_connection_and_edge_types(self, type_name):
        return self._connections[type_name]

    def register_types(self):
        R = self.R

        class Node(R.Interface):
            id = R.ID.NonNull(description='The id of the object.')

            resolve_id = self._resolve_node_id

        class PageInfo(R.ObjectType):
            has_next_page = R.Boolean.NonNull(description='When paginating forwards, are there more items?')
            has_previous_page = R.Boolean.NonNull(description='When paginating backwards, are there more items?')
            start_cursor = R.String(description='When paginating backwards, the cursor to continue.')
            end_cursor = R.String(description='When paginating forwards, the cursor to continue.')

        self.Node = Node
        self.PageInfo = PageInfo

    def fetch_node(self, id, info):
        object_type_name, object_id = unbase64(id).split(':', 1)
        object_type = self.R[object_type_name]()
        assert isinstance(object_type, GraphQLObjectType)
        return self.data_source.fetch_node(object_type, object_id, info)

    def _resolve_node_id(self, obj, args, info):
        return self.node_id_for(obj, info)

    def node_id_for(self, obj, info=None):
        object_type = self.Node.T.resolve_type(obj, info)
        return base64('%s:%s' % (object_type, obj.id))

    def connection_definitions(self, name, object_type):
        R = self.R

        if name in self._connections:
            return self._connections[name]

        class Edge(R.ObjectType):
            _name = '{}Edge'.format(name)
            node = R[object_type](description='The item at the end of the edge')
            cursor = R.String.NonNull(description='A cursor for use in pagination')

        class Connection(R.ObjectType):
            _name = '{}Connection'.format(name)

            page_info = R.PageInfo.NonNull
            edges = R[Edge].List

        self._connections[name] = Connection, Edge
        return Connection, Edge

    def Connection(self, name, object_type, args=None, resolver=None, **kwargs):
        args = args or {}
        args.update(connection_args)
        if not resolver:
            resolver = self.data_source.make_connection_resolver(self, object_type)

        field = self.R.Field(self.connection_definitions(name, object_type)[0], args=args, resolver=resolver, **kwargs)
        return field

    def _create_mutation_type_class(self):
        registry = self.R

        class RelayRegistryMutationMeta(RelayMutationMeta):
            @staticmethod
            def _register(mutation_name, mutation):
                registry._register_mutation(mutation_name, mutation)

            @staticmethod
            def _get_registry():
                return registry

        @six.add_metaclass(RelayRegistryMutationMeta)
        class Mutation(MutationBase):
            abstract = True

        return Mutation
