from apification.utils.tpath.apitree import ApiTreeTPathResolver
from apification.utils.tpath.base import TPathError

parse = ApiTreeTPathResolver.parse


__all__ = ['parse', 'TPathError']
