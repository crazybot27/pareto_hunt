# this is a test script that finds all unsubmited local solutions on specific puzzle paretos
# primary usage would be for dailies
# couple of example at the bottom for usage.  needs a more friendly "user interface".


import os

import db
import zlbb


field_name = {
    'g': ('mcCost', 'mCost'),
    'c': ('mcCycles', 'mCycles'),
    'a': ('mcArea', 'mArea'),
    'i': ('mcInstructions', 'mInstructions'),
    'h': ('mcHeight', 'mHeight'),
    'w': ('mcWidth', 'mWidth'),
    'r': ('mcRate', 'mRate'),
    'ainf': ('mcAreaInf', 'mAreaInf'),
    'hinf': ('mcHeightInf', 'mHeightInf'),
    'winf': ('mcWidthInf', 'mWidthInf'),
}


def where(is_local: bool, table: str, requireTrack: bool, allowOverlap: bool):
    local = ''
    if is_local:
        local = 'c'

    wheres = []
    if local:
        wheres.append(f'{table}valid=1')
    if requireTrack:
        wheres.append(f'{table}m{local}Trackless=1')
    if not allowOverlap:
        wheres.append(f'{table}m{local}Overlap=0')

    return wheres


def frontier(puzzle: str, primary: list, front: list, requireTrack: bool = False, allowOverlap: bool = False):
    ff = [field_name[f] for f in primary + front]  # column names of the metrics
    # print(ff)

    # right puzzle
    # standard restrictions
    wa = (
        ['puzzle_name = ?'] +
        where(True, 'a.', requireTrack, allowOverlap)
    )

    # same puzzle
    # standard restrictions
    # no community puzzle equal or better on all metrics
    wb = (
        ['b.puzzle_name = a.puzzle_name'] +
        where(False, 'b.', requireTrack, allowOverlap) +
        [f'b.{f[1]} <= a.{f[0]}' for f in ff]
    )

    # same puzzle
    # standard restrictions
    # no local puzzle equal or better on all metrics, and at least one metric strictly better
    wc = (
        ['c.puzzle_name = a.puzzle_name'] +
        where(True, 'c.', requireTrack, allowOverlap) +
        [f'c.{f[0]} <= a.{f[0]}' for f in ff] +
        [f"({' OR '.join(f'c.{f[0]} < a.{f[0]}' for f in ff)})"]
    )

    args = [puzzle]

    if primary:
        # find the best solution on the community leaderboard for the given metrics
        pkey = [field_name[p] for p in primary]
        pkey_l = [p[0] for p in pkey]
        pkey_c = [p[1] for p in pkey]

        w = ['puzzle_name = ?'] + where(False, '', requireTrack, allowOverlap)
        sql = f"""SELECT {','.join(pkey_c)} FROM community
        WHERE {' AND '.join(w)}
        ORDER BY {','.join(pkey_c)}
        """
        pval = db.con.execute(sql, [puzzle]).fetchone()
        # print(sql)
        # print(pval)

        wa.append(f"({','.join(pkey_l)}) <= ({','.join(['?' for p in pkey_l])}) ")
        wb.append(f"({','.join(pkey_c)}) <= ({','.join(['?' for p in pkey_c])}) ")
        wc.append(f"({','.join(pkey_l)}) <= ({','.join(['?' for p in pkey_l])}) ")

        args += pval*3

    sql = f"""SELECT solution_file,  {','.join(f[0] for f in ff)} FROM local a
    WHERE {' AND '.join(wa)}
    AND NOT EXISTS (
        SELECT * FROM community b
        WHERE {' AND '.join(wb)}         
    )
    AND NOT EXISTS (
        SELECT * FROM local c
        WHERE {' AND '.join(wc)}
    )
    ORDER BY {','.join(f[0] for f in ff)}
    """
    # print(sql)
    # print(args)
    res = db.con.execute(sql, args).fetchall()

    print()
    print(f"{zlbb.get_puzzle_name(puzzle)} : {''.join(primary)}({''.join(front)}), {len(res)} paretos")
    for r in res:
        print(os.path.basename(r[0]), r[1:])


# if you want a@infinity, use 'ainf' not 'a'.  same for h/w.
# I should change this to just use single letters and a @V/@inf parameter
frontier('w2946684660', [], ['g', 'c'])  # probe (gc)
frontier('w2946684529', [], ['g', 'c'])  # biosteel (gc)
frontier('w2946684529', ['w'], ['a', 'g', 'c'])  # biosteel w(agc)
frontier('w2946687073', ['w', 'h'], ['g', 'r'])  # bicrystal wh(gr)
frontier('w2946687073', ['w', 'h'], ['g', 'r', 'a'])  # bicrystal wh(gra)
