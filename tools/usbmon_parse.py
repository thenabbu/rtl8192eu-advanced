#!/usr/bin/env python3
"""Parse a usbmon textual capture: control ops, phases, endpoint stats.

Usage: usbmon_parse.py CAPTURE.txt [--gap-ms 50] | --selftest
usbmon timestamps are integer MICROSECONDS with no decimal point; all output
converts them to float seconds (raw us digit-runs get mangled by output
redaction and corrupt eyeballed timelines).
"""
import re
import sys
import collections

SETUP = re.compile(
    r'\sS (?P<dir>C[io]):\d+:\d+:\d+ s (?P<bm>[0-9a-f]{2}) (?P<req>[0-9a-f]{2})'
    r' (?P<wval>[0-9a-f]{4}) (?P<widx>[0-9a-f]{4}) (?P<wlen>[0-9a-f]{4})'
    r' \d+(?: = (?P<data>[0-9a-f]+))?')
EP = re.compile(r'\sS (?P<kind>[CB][io]):\d+:\d+:(?P<ep>\d+)')


def parse(lines):
    """-> (ops, eps); op = (ts_us, dir, bm, bReq, wValue, wLen, data)."""
    eps, ops = collections.Counter(), []
    for line in lines:
        if ' S ' not in line:
            continue
        m = EP.search(line)
        if m:
            eps[f"{m.group('kind')} ep{m.group('ep')}"] += 1
        m = SETUP.search(line)
        if m:
            ops.append((int(line.split()[1]), m.group('dir'), m.group('bm'),
                        m.group('req'), m.group('wval'), int(m.group('wlen'), 16),
                        m.group('data')))
    return ops, eps


def selftest():
    sample = (
        'ffff1 1000000 S Ci:6:002:0 s c0 05 0824 0000 0004 4 <\n'
        'ffff1 1000500 C Ci:6:002:0 0 4 = 040239a1\n'
        'ffff2 1001000 S Co:6:002:0 s 40 05 0100 0000 00fe 254 = aabb\n'
        'ffff3 1060000 S Bo:6:002:5 0 1500 >\n').splitlines()
    ops, eps = parse(sample)
    assert len(ops) == 2, ops
    assert ops[0][1:6] == ('R', 'c0', '05', '0824', 4), ops[0]
    assert ops[1][5] == 254 and ops[1][6] == 'aabb', ops[1]
    assert eps == {'Bo ep5': 1}, eps
    assert ops[1][0] - ops[0][0] == 1000  # us integer timestamps
    print('selftest OK')


def main():
    if '--selftest' in sys.argv:
        selftest()
        return
    path = sys.argv[1]
    gap_us = 50000
    if '--gap-ms' in sys.argv:
        gap_us = int(sys.argv[sys.argv.index('--gap-ms') + 1]) * 1000
    lines = open(path, errors='replace').read().splitlines()
    ops, eps = parse(lines)
    if not ops:
        sys.exit('no control submits parsed — check capture format')
    t0 = ops[0][0]
    print(f'lines={len(lines)} control_ops={len(ops)} '
          f'span={(ops[-1][0] - t0) / 1e6:.2f}s')
    print('submits per endpoint:', dict(eps))

    phases, cur = [], [ops[0]]
    for o in ops[1:]:
        if o[0] - cur[-1][0] > gap_us:
            phases.append(cur)
            cur = [o]
        else:
            cur.append(o)
    phases.append(cur)
    print(f'phases (gap>{gap_us // 1000}ms): {len(phases)}')
    for i, p in enumerate(phases[:25]):
        wl = dict(collections.Counter(o[5] for o in p))
        pages = dict(collections.Counter(o[4][:2] for o in p).most_common(5))
        print(f'  p{i:03d}: t+{(p[0][0] - t0) / 1e6:8.3f}s '
              f'dur={(p[-1][0] - p[0][0]) / 1e6:7.3f}s n={len(p):5d} '
              f'wlen={wl} pages={pages}')
    if len(phases) > 25:
        print(f'  ... {len(phases) - 25} more phases')

    print('\nsetup (bm, bReq, dir, wLen): count')
    for k, v in collections.Counter(
            (o[2], o[3], o[1], o[5]) for o in ops).most_common(15):
        print(f'  {k}: {v}')

    blk = [o for o in ops if o[5] not in (1, 2, 4)]
    if blk:
        print(f'\nblock writes: n={len(blk)} '
              f'lens={dict(collections.Counter(o[5] for o in blk))} '
              f'wval {blk[0][4]}..{blk[-1][4]}')

    dominant = collections.Counter((o[2], o[3]) for o in ops).most_common(1)[0][0]
    other = [o for o in ops if (o[2], o[3]) != dominant][:15]
    if other:
        print(f'\nnon-dominant requests (dominant={dominant}):')
        for o in other:
            print(f'  t+{(o[0] - t0) / 1e6:.3f}s bm={o[2]} req={o[3]} '
                  f'dir={o[1]} wval={o[4]} wlen={o[5]}')


if __name__ == '__main__':
    main()
