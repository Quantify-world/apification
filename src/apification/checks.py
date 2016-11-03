from django.core.checks import register, Tags, Error

from apification.utils.discover import discover_tree
from apification.nodes import ApiNode


@register()
def all_checks(app_configs, **kwargs):
    errors = []
    for root in discover_tree():
        errors.extend(check_type(root) or ())
    return errors


def check_type(root):
    errors = []
    if not issubclass(root, ApiNode):
        errors.append(
            Error(
                'Node %s is not ApiNode subclass' % root,
                # hint='A hint.',
                obj=root,
                id='apification.E001',
            )
        )
    return errors