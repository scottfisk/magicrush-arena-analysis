import csv
import numpy
import pandas

from itertools import combinations, repeat
from multiprocessing import cpu_count, Manager, Pool
from sklearn import preprocessing


def members_as_list(team):
    return [team['1'], team['2'], team['3'], team['4'], team['5']]


def eval_combo(heroes, normed_data, avg_power):
    # teams with this hero present
    exp = (' & ').join('({})'.format(h) for h in heroes)
    teams = normed_data.query(exp)['power']
    if len(teams) > 10:
        power = teams.mean()
        count = teams.count()
        avg_power.append({'heroes': ','.join(h for h in sorted(heroes)), 'avg_rel_power': int(power), 'count': count})


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
                'server': team['Server'],
                'rank': int(team['Rank']),
                'power': int(team['Power'])
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
            server_data['power'] = relative_power
            frames.append(server_data)

        normed_data = pandas.concat(frames)

        # spaces seem to anger pandas query command
        normed_data.columns = [c.replace(' ', '_') for c in normed_data.columns]
        all_heroes = [c.replace(' ', '_') for c in all_heroes]

        # multiprocessing manager
        manager = Manager()
        pool = Pool(processes=cpu_count())

        subset_sizes = [1, 2, 3, 4, 5]
        for subset_size in subset_sizes:
            avg_power = manager.list()
            # iterates over all combinations of a team for a given size using
            # all processors
            pool.starmap(
                eval_combo,
                zip(combinations(all_heroes, subset_size), repeat(normed_data), repeat(avg_power)),
                chunksize=1000)

            with open('team_size{}.csv'.format(subset_size), 'w') as csvfile:
                fieldnames = ['heroes', 'avg_rel_power', 'count']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                # write out sorted by power
                writer.writerows(sorted(avg_power, key=lambda k: k['avg_rel_power'], reverse=True))


if __name__ == '__main__':
    main()
