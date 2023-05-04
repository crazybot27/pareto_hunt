# https://github.com/ianh/omsim  #thank you panic!

import math
from ctypes import cdll, c_void_p, c_char_p

# load panic's tool
lv = cdll.LoadLibrary('./libverify.dll')
lv.verifier_create.restype = c_void_p
lv.verifier_error.restype = c_char_p

# I had problems in the past with it running slow on large area puzzles but it seems much better now.
# if you want to skip big area puzzles, modify this
# todo: move to settings
MAX_AREA = 100000

# todo, being extra lazy here. need to identify production puzzles better
productions = set([
    "P076",    "P080",    "P075",    "P074",    "P083",    "P078",    "P079",    "P081",    "P082",
    "P077",    "P084",    "P091b",    "P090",    "P092",    "P093",    "P094",    "P105",    "P109",
    "w1698786588", "week5",
    "w2501728107",
    "w2450512232", "OM2021_W4",
    "w2788067624", "OM2022_AetherReactor",
    "w2946684660", "OM2023_W5_ProbeModule",
])


def get_metric(v, name: bytes):
    r = lv.verifier_evaluate_metric(c_void_p(v), c_char_p(name))
    if r < 0:
        return math.inf
    return r


def get_metrics(sol):
    puzzle_file = ('puzzle/'+sol.puzzle_name+'.puzzle').encode('utf-8')
    solution_file = sol.full_path.encode('utf-8')
    v = lv.verifier_create(c_char_p(puzzle_file), c_char_p(solution_file))

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

    if sol.puzzle_name in productions:
        metrics['mcHeight'] = None
        metrics['mcWidth'] = None
        metrics['mcHeightInf'] = None
        metrics['mcWidthInf'] = None

    err = lv.verifier_error(c_void_p(v))
    if err:
        # should just be a no throughput error
        print('error after victory', err)

    return metrics
