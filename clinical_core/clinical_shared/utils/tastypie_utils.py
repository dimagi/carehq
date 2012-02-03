from tastypie.paginator import Paginator
from tastypie.resources import ModelResource
from dimagi.utils.couch.pagination import DatatablesParams


class DatatablesPaginator(Paginator):
    """
    Override of the default Paginator for TastyPie - using couchdbkit, we can limit/paginate using the
    view API, but the slicing assumes we have a queryset, so to be more efficient, we do that in the get_list
    """
    def page(self):
        """
        Generates all pertinent data about the requested page.

        Handles getting the correct ``limit`` & ``offset``, then slices off
        the correct set of results and returns all pertinent metadata.
        """
        limit = self.get_limit()
        offset = self.get_offset()
        count = self.get_count()
        objects = self.get_slice(limit, offset)
        meta = {
            'offset': offset,
            'limit': limit,
            'total_count': count,
            }

        if limit:
            meta['previous'] = self.get_previous(limit, offset)
            meta['next'] = self.get_next(limit, offset, count)

        print meta
        print len(objects)
        return {
            'aaData': objects,
            'iTotalRecords': count,
            'iTotalDisplayRecords': count,
            }




class DatatablesModelResource(ModelResource):
    def get_list(self, request, **kwargs):
        """
        Returns a serialized list of resources.

        Calls ``obj_get_list`` to provide the data, then handles that result
        set and serializes it.

        Should return a HttpResponse (200 OK).
        """
        query = request.REQUEST
        params = DatatablesParams.from_request_dict(query)

        # TODO: Uncached for now. Invalidation that works for everyone may be
        #       impossible.
        objects = self.obj_get_list(request=request, **self.remove_api_resource_names(kwargs))
        sorted_objects = self.apply_sorting(objects, options=request.GET)

        paginator = DatatablesPaginator(request.GET, sorted_objects, resource_uri=self.get_resource_list_uri(), limit=params.count, offset=params.start)
        to_be_serialized = paginator.page()

        # Dehydrate the bundles in preparation for serialization.
        bundles = [self.build_bundle(obj=obj, request=request) for obj in to_be_serialized['aaData']]
        to_be_serialized['aaData'] = [self.full_dehydrate(bundle) for bundle in bundles]
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        if request.GET.get('sEcho', None) is not None:
            to_be_serialized['sEcho'] = int(request.GET['sEcho'])


        return self.create_response(request, to_be_serialized)
