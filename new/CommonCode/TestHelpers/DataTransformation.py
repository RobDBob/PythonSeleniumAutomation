import functools
import operator

def findKeys(node, kv):
    """
    Fings all iterations of specific key and returns it as generator
    """
    if isinstance(node, list):
        for i in node:
            for x in findKeys(i, kv):
               yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findKeys(j, kv):
                yield x


def flattenSublists(listObject):
    """
    Flatten sublists into a single list
    """
    return functools.reduce(operator.iconcat, listObject, [])