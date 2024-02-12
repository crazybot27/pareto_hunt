import json
import math
import urllib.request

import db


def check_infinity(score, cat):
    if score[cat] == "Infinity" or score[cat] is None:
        score[cat] = math.inf


def update_community(pn):
    print('getting community scores', pn)

    url = f"https://zlbb.faendir.com/om/puzzle/{pn}/records?includeFrontier=true"
    # print(url)

    raw = urllib.request.urlopen(url).read().decode('utf-8')
    # uh, check that it's not broken?

    # delete old entries
    sql = "DELETE FROM community WHERE puzzle_name=?"
    db.con.execute(sql, [pn])

    jj = json.loads(raw)
    print(len(jj), 'community files')
    sql = """INSERT OR REPLACE INTO community
            (solution_file, gif_file, puzzle_name, category,
            mCost, mCycles, mArea, mInstructions,
            mHeight, mWidth, mRate,
            mAreaInfLevel, mAreaInfValue, mHeightInf, mWidthInf,
            mTrackless, mOverlap, mLoop)
            VALUES (?,?,?,?,
            ?,?,?,?,
            ?,?,?,
            ?,?,?,?,
            ?,?,?
            )"""

    data = []
    for j in jj:
        if j['solution'] is None:
            j['solution'] = j['gif']
        score = j['score']

        check_infinity(score, 'rate')
        check_infinity(score, 'areaINFLevel')
        check_infinity(score, 'areaINFValue')
        check_infinity(score, 'heightINF')
        check_infinity(score, 'widthINF')

        if score['rate'] == math.inf:
            score['loop'] = 0
        else:
            score['loop'] = 1

        datum = [j['solution'], j['gif'], pn, j['smartFormattedCategories'],
                 score['cost'], score['cycles'], score['area'], score['instructions'],
                 score['height'], score['width'], score['rate'],
                 score['areaINFLevel'], score['areaINFValue'], score['heightINF'], score['widthINF'],
                 score['trackless'], score['overlap'], score['loop']]
        data.append(datum)
    db.con.executemany(sql, data)

    # mark that we have new data
    sql = """INSERT OR REPLACE INTO community_cache
    (puzzle_name, last_check)
    VALUES (?,CURRENT_TIMESTAMP)"""
    db.con.execute(sql, [pn])
    db.con.commit()


def update_all():
    for j in puzzles.values():
        sql = "SELECT * FROM community WHERE puzzle_name=?"
        rows = db.con.execute(sql, [j['id']]).fetchall()
        print(j['id'], len(rows))

        # if len(rows) == 0:
        update_community(j['id'])


def get_puzzles():
    print('Getting puzzle list')
    url = 'https://zlbb.faendir.com/om/puzzles'
    raw = urllib.request.urlopen(url).read().decode('utf-8')
    jj = json.loads(raw)

    return {j['id']: j for j in jj}


def get_categories():
    print('Getting tracked categories')
    url = 'https://zlbb.faendir.com/om/categories'
    raw = urllib.request.urlopen(url).read().decode('utf-8')
    jj = json.loads(raw)

    return jj


def get_puzzle_name(puz):
    if puz in puzzles:
        return puzzles[puz]['displayName']
    return puz


# todo: cache these locally?
puzzles = get_puzzles()
categories = get_categories()
