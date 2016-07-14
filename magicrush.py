import csv
import numpy
import pandas

from itertools import combinations, repeat
from multiprocessing import Manager, Pool
from sklearn import preprocessing

PAID_HEROES = frozenset(
    ['ariel', 'charon', 'lilith', 'monk_sun', 'rams', 'robin',
     'saizo', 'smoke', 'theresa', 'edwin'])


def members_as_list(team):
    return [team['1'], team['2'], team['3'], team['4'], team['5']]


def eval_combo(heroes, normed_data, avg_power, f2p=False):
    # teams with this hero present
    exp = (' & ').join('({})'.format(h) for h in heroes)
    if f2p:
        exp = '{} & {}'.format(exp, (' & ').join('~{}'.format(h) for h in PAID_HEROES))
    teams = normed_data.query(exp)['relative_power']
    if len(teams) > 0:
        power = teams.mean()
        count = teams.count()
        if len(teams) > 1:
            stddev = teams.std()
        else:
            stddev = 0
        avg_power.append({'heroes': ','.join(h for h in sorted(heroes)), 'avg_rel_power': int(power), 'stddev': int(stddev), 'count': count})


def main():
    # load my file
    with open('magicrush-input.csv', 'r') as fp:
        data_iter = csv.DictReader(fp, delimiter=',')
        data = [r for r in data_iter]

        all_heroes = set()
        # get list of heroes
        for team in data:
            all_heroes.update(members_as_list(team))

        formatted_data = []
        for team in data:
            formatted_team = {
                'server': team['server'],
                'rank': int(team['rank']),
                'power': int(team['power']),
                'relative_power': int(team['relative_power'])
            }
            [formatted_team.update({hero: hero in members_as_list(team)}) for hero in all_heroes]
            formatted_data.append(formatted_team)

        # for each server
        data = pandas.DataFrame(formatted_data)
        frames = []
        for server in data['server'].unique():
            # get server data
            server_data = data[data.server == server]
            x = server_data['rank']
            # scale
            y = preprocessing.scale(server_data['power'], with_std=False)
            # fit
            p = numpy.polyfit(x, y, deg=2)
            yfit = numpy.polyval(p, x)
            # get distance
            relative_power = yfit - y
            # save
            # not currently using this relative power
            server_data['relative_power_calculated'] = relative_power
            frames.append(server_data)
        normed_data = pandas.concat(frames)

        # spaces seem to anger pandas query command
        normed_data.columns = [c.replace(' ', '_') for c in normed_data.columns]
        all_heroes = {c.replace(' ', '_') for c in all_heroes}
        f2p_heroes = all_heroes.difference(PAID_HEROES)

        # multiprocessing manager
        manager = Manager()
        pool = Pool(processes=6)

        subset_sizes = [1, 2, 3, 4, 5]
        for subset_size in subset_sizes:
            avg_power = manager.list()
            # iterates over all combinations of a team for a given size using
            # all processors
            pool.starmap(
                eval_combo,
                zip(combinations(all_heroes, subset_size), repeat(normed_data), repeat(avg_power), repeat(False)),
                chunksize=1000)

            with open('team_size{}.csv'.format(subset_size), 'w') as csvfile:
                fieldnames = ['heroes', 'avg_rel_power', 'stddev', 'count']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                # write out sorted by power
                writer.writerows(sorted(avg_power, key=lambda k: k['avg_rel_power'], reverse=True))

            # F2P
            avg_power = manager.list()
            # remove paid heros
            pool.starmap(
                eval_combo,
                zip(combinations(f2p_heroes, subset_size), repeat(normed_data), repeat(avg_power), repeat(True)),
                chunksize=1000)

            with open('f2p_team_size{}.csv'.format(subset_size), 'w') as csvfile:
                fieldnames = ['heroes', 'avg_rel_power', 'stddev', 'count']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                # write out sorted by power
                writer.writerows(sorted(avg_power, key=lambda k: k['avg_rel_power'], reverse=True))


if __name__ == '__main__':
    main()
