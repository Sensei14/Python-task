def calculate_max_parents_depth(tree_node):
    if not tree_node:
        return 0

    if not tree_node.get('parents'):
        return tree_node.get('depth', 0)

    max_parents_depth = 0
    for parent in tree_node['parents']:
        parent_depth = calculate_max_parents_depth(parent)
        max_parents_depth = max(max_parents_depth, parent_depth)

    return max_parents_depth + 1


def calculate_max_children_depth(tree_node):
    if not tree_node:
        return 0

    if not tree_node.get('children'):
        return tree_node.get('depth', 0)

    max_child_depth = 0
    for child in tree_node['children']:
        child_depth = calculate_max_children_depth(child)
        max_child_depth = max(max_child_depth, child_depth)

    return max_child_depth + 1
