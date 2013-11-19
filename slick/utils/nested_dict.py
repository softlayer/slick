# Code from http://stackoverflow.com/questions/11700798/python-accessing-values-nested-within-dictionaries


def lookup(dic, key, *keys):
    if keys:
        return lookup(dic.get(key, {}), *keys)
    return dic.get(key)


# Code from http://stackoverflow.com/questions/1143671/python-sorting-list-of-dictionaries-by-multiple-keys
def multikeysort(items, columns):
    from operator import itemgetter
    comparers = [
        ((itemgetter(col[1:].strip()), -1) if col.startswith('-')
         else (itemgetter(col.strip()), 1)) for col in columns]

    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0
    return sorted(items, cmp=comparer)
