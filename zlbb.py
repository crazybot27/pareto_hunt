import json
import math
import urllib.request

import db


def check_infinity(score, cat):
    if score[cat] == "Infinity" or score[cat] == None:
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
            mAreaInf, mHeightInf, mWidthInf,
            mTrackless, mOverlap, mLoop)
            VALUES (?,?,?,?,
            ?,?,?,?,
            ?,?,?,
            ?,?,?,
            ?,?,?
            )"""

    data = []
    for j in jj:
        if j['solution'] == None:
            j['solution'] = j['gif']
        score = j['score']

        check_infinity(score, 'rate')
        check_infinity(score, 'areaINF')
        check_infinity(score, 'heightINF')
        check_infinity(score, 'widthINF')

        if score['rate'] == math.inf:
            score['loop'] = 0
        else:
            score['loop'] = 1

        datum = [j['solution'], j['gif'], pn, j['smartFormattedCategories'],
                 score['cost'], score['cycles'], score['area'], score['instructions'],
                 score['height'], score['width'], score['rate'],
                 score['areaINF'], score['heightINF'], score['widthINF'],
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
    url = '''https://zlbb.faendir.com/om/puzzles'''
    raw = urllib.request.urlopen(url).read().decode('utf-8')
    jj = json.loads(raw)
    for j in jj:
        sql = "SELECT * FROM community WHERE puzzle_name=?"
        rows = db.con.execute(sql, [j['id']]).fetchall()
        print(j['id'], len(rows))

        # if len(rows) == 0:
        update_community(j['id'])
