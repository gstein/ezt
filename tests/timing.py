#!/usr/bin/env python
"""timing"""

import string
import time


def run():
    """run"""
    timing(['foo', 'bar', 'baz', 'blorg'], ['foo'])
    timing(['foo', 'bar', 'baz', 'blorg'], [])
    timing(['foo', 'bar', 'baz', 'blorg'], ['foo', 'bar', 'baz'])
    timing(['foo', 'bar', 'baz', 'blorg'], ['foo.bar', 'bar', 'baz'])
    timing(['foo', 'bar', 'baz', 'blorg'], ['foo.bar.baz', 'bar', 'baz'])
    timing(['foo', 'bar', 'baz', 'blorg'], ['foo.bar.baz', 'foo.bar', 'foo'])
    timing(['foo', 'bar', 'baz', 'blorg'], ['foo', 'foo.bar', 'foo.bar.baz'])
    timing(['foo'], [])
    timing(['foo', 'bar'], [])


def timing(parts, for_names):
    """timing"""
    b = time_it(baseline, parts, for_names)
    t1, res1 = time_it(alg1, parts, for_names)
    t2, res2 = time_it(alg2, parts, for_names)
    t3, res3 = time_it(alg3, parts, for_names)

    f2 = []
    for f in for_names:
        f2.append((len(f), f, string.count(f, '.') + 1))
    f2.sort()
    f2.reverse()

    t4, res4 = time_it(alg4, parts, f2)

    # res3 is borken. ignore it.
    if res1 != res2 or res1 != res4:
        print res1, res2, res3, res4
        return

    print '%s %0.4f %0.4f %0.4f %0.4f %0.4f' % (res1, b, t1 - b, t2 - b, t3 - b, t4 - b)


def time_it(func, parts, for_names):
    """time_it"""
    t = time.time()
    for i in xrange(10000):
        res = func(parts[:], for_names)
    return time.time() - t, res


def baseline(parts, for_names):
    """baseline"""
    return '', []


def alg1(parts, for_names):
    """alg1"""
    rest = []
    while parts:
        start = string.join(parts, '.')
        if start in for_names:
            return start, rest

        rest.insert(0, parts[-1])
        del parts[-1]

    return rest[0], rest[1:]


def alg2(parts, for_names):
    """alg2"""
    for i in range(len(parts), 0, -1):
        start = string.join(parts[:i], '.')
        if start in for_names:
            return start, parts[i:]
    return parts[0], parts[1:]


def alg3(parts, for_names):
    """alg3"""
    all = string.join(parts, '.')
    for f in for_names:
        l = len(f)
        if all[:l] == f:
            return f, string.split(all[l + 1:], '.')
    return parts[0], parts[1:]


def alg4(parts, for_names):
    """
    print for_names
    import sys
    sys.exit(0)
    """
    if for_names:
        all = string.join(parts, '.')
        for l, f, s in for_names:
            if all[:l] == f:
                return f, parts[s:]
    return parts[0], parts[1:]


if __name__ == '__main__':
    run()
