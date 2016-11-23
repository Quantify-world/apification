from django.core.checks import register, Tags, Error

from apification.utils.discover import discover_tree
from apification.nodes import ApiNode
from apification.actions import Action


@register()
def all_checks(app_configs, **kwargs):
    errors = []
    for root in discover_tree():
        errors.extend(check_type(root))
        errors.extend(check_actions_are_leafs(root))
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


def check_actions_are_leafs(root):
    errors = []
    actions = []
    
    def fetch_actions_under (node):
        for name, subnode in node.iter_children():
            if issubclass(subnode, Action):
                actions.append(subnode)
            else:
                fetch_actions_under(subnode)
    
    fetch_actions_under(root)
    for action in actions:
        if tuple(action.iter_children()):  # if at least one child
            children = map(str, zip(*action.iter_children())[1])
            errors.append(
                Error(
                    'Action must have not child nodes, but %s have these children: %s.' % (action, ', '.join(children)),
                    # hint='A hint.',
                    obj=root,
                    id='apification.E002',
                )
            )
    return errors