# https://github.com/ianh/omsim  #thank you panic!

import math
import os
import platform
import sys
from ctypes import cdll, c_void_p, c_char_p, c_int

import zlbb

# load panic's tool

if platform.system() == 'Windows':
    lv = cdll.LoadLibrary('./libverify.dll')
elif platform.system() == 'Darwin':
    lv = cdll.LoadLibrary('./libverifymac.so')
elif platform.system() == 'Linux':
    if os.path.isfile('./libverify.so'):
        lv = cdll.LoadLibrary('./libverify.so')
    else:
        print("Hey, thanks for trying to use my script, but you'll have to build panic's omsim yourself.  It should be an easy makefile to follow.  Just drop libverify.so in this folder after")
        print(r"https://github.com/ianh/omsim")
        sys.exit()
else:
    print("Huh, you're on a weird os I don't know or I broke something.  Hopefully you know how to fix this better than I do.")
    print("Find this comment in the code and fix it please.")
    sys.exit()
lv.verifier_create.restype = c_void_p
lv.verifier_error.restype = c_char_p

# I had problems in the past with it running slow on large area puzzles but it seems much better now.
# if you want to skip big area puzzles, modify this
# todo: move to settings
MAX_AREA = 100000
MAX_CYCLES = 100000
# current "worst" scores on the leaderboard for comparison are
# area:    73k   Mist of Dousing   GR
# cycles:  22k   Alchemical Slag   A


def get_metric(v, name: bytes):
    r = lv.verifier_evaluate_metric(c_void_p(v), c_char_p(name))
    if r < 0:
        return math.inf
    return r


def is_legal(v, sol):
    """overlap
    + max(0, parts of type baron - 1)
    + max(0, "parts of type glyph-disposal" - 1)
    + duplicate reagents
    + duplicate products
    + max(0, "maximum track gap^2" - 1)"""

    wheel = get_metric(v, b'parts of type baron')
    disposal = get_metric(v, b'parts of type glyph-disposal')
    reagents = not get_metric(v, b'duplicate reagents')
    products = not get_metric(v, b'duplicate products')
    track = get_metric(v, b'maximum track gap^2')
    overlap = get_metric(v, b'overlap')  # banned in production only for now

    err = lv.verifier_error(c_void_p(v))
    if err:
        # something went wrong, solution probably doesn't work
        return False
    return (wheel <= 1 and
            disposal <= 1 and
            reagents and
            products and
            track <= 1 and
            (overlap == 0 or zlbb.puzzles[sol.puzzle_name]['type'] != 'PRODUCTION')
            )


def get_metrics(sol):
    puzzle_file = ('puzzle/'+sol.puzzle_name+'.puzzle').encode('latin1')
    solution_file = sol.full_path.encode('latin1')
    v = lv.verifier_create(c_char_p(puzzle_file), c_char_p(solution_file))
    lv.verifier_set_cycle_limit(c_void_p(v), c_int(MAX_CYCLES))

    if not is_legal(v, sol):
        lv.verifier_destroy(c_void_p(v))
        return False

    metrics = {
        'mpCost': get_metric(v, b'parsed cost'),
        'mpCycles': get_metric(v, b'parsed cycles'),
        'mpArea': get_metric(v, b'parsed area'),
        'mpInstructions': get_metric(v, b'parsed instructions'),

        'mcCost': get_metric(v, b'cost'),
        'mcCycles': get_metric(v, b'cycles'),
        'mcArea': get_metric(v, b'area (approximate)'),
        'mcInstructions': get_metric(v, b'instructions'),

        'mcHeight': get_metric(v, b'height'),
        'mcWidth': get_metric(v, b'width*2')/2,

        'mcTrackless': get_metric(v, b'number of track segments') == 0,
        'mcOverlap': get_metric(v, b'overlap') > 0,
    }

    err = lv.verifier_error(c_void_p(v))
    if err:
        # something went wrong, solution probably doesn't work
        print('error before victory', err)
        lv.verifier_destroy(c_void_p(v))
        return False

    to = get_metric(v, b'throughput outputs')
    tc = get_metric(v, b'throughput cycles')

    if to <= 0 or tc <= 0 or err or to == math.inf:
        # technically, the leaderboard makes a distinction between 0 and inf, but I'm lazy
        metrics |= {
            'mcRate': math.inf,
            'mcAreaInf': math.inf,
            'mcHeightInf': math.inf,
            'mcWidthInf': math.inf,
            'mcLoop': 0,
        }
    else:
        # print('rate?', tc, to)
        metrics |= {
            'mcRate': math.ceil(tc/to*100)/100,
            'mcAreaInf': get_metric(v, b'steady state area'),
            'mcHeightInf': get_metric(v, b'steady state height'),
            'mcWidthInf': get_metric(v, b'steady state width*2')/2,
            'mcLoop': 1,
        }

    if zlbb.puzzles[sol.puzzle_name]['type'] == 'PRODUCTION':
        metrics['mcHeight'] = None
        metrics['mcWidth'] = None
        metrics['mcHeightInf'] = None
        metrics['mcWidthInf'] = None

    err = lv.verifier_error(c_void_p(v))
    if err:
        # should just be a no throughput error
        print('error after victory', err)

    lv.verifier_destroy(c_void_p(v))
    return metrics
