from django.core.checks import register, Error

from apification.utils.discover import discover_tree
from apification.nodes import ApiNode
from apification.actions import Action
from apification.serializers import Serializer

def fetch_actions_under(node):
    ret = []
    for subnode in node.iter_class_children():
        if issubclass(subnode, Action):
            ret.append(subnode)
        else:
            ret.extend(fetch_actions_under(subnode))
    return ret



@register()
def all_checks(app_configs, **kwargs):
    errors = []
    for root in discover_tree():
        actions = fetch_actions_under(root)
        errors.extend(check_type(root))
        errors.extend(check_actions_are_leafs(actions))
        errors.extend(check_no_action_without_serializer(actions))
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


def check_actions_are_leafs(actions):  # FIXME: Do we realy need root here?
    errors = []

    for action in actions:
        if tuple(action.iter_class_children()):  # if at least one child
            children = map(str, action.iter_class_children())
            errors.append(
                Error(
                    'Action must have no child nodes, but it have these children: %s' % ', '.join(children),
                    # hint='A hint.',
                    obj=action,
                    id='apification.E002',
                )
            )
    return errors


def check_no_action_without_serializer(actions):
    errors = []
    without_serializers = []
    for action in actions:
        if not isinstance(action.serializer, type) or not issubclass(action.serializer, Serializer):
            without_serializers.append(str(action))
    
    if without_serializers:
        errors.append(
            Error(
                'These Actions have no suitable serializers: %s' % ', '.join(without_serializers),
                # hint='A hint.',
                obj=action.parent_class,
                id='apification.E003',
            )
        )
    return errors
    