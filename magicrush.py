import csv
import pandas
import numpy
from sklearn import preprocessing


def members_as_list(team):
    return [team['1'], team['2'], team['3'], team['4'], team['5']]


def main():
    # load my file
    with open('magicrush-input.csv', 'r') as fp:
        data_iter = csv.DictReader(fp, delimiter=',')
        data = [r for r in data_iter]

        all_heros = set()
        # get list of heros
        for team in data:
            all_heros.update(members_as_list(team))

        formatted_data = []
        for team in data:
            formatted_team = {
                'server': team['Server'],
                'rank': int(team['Rank']),
                'power': int(team['Power'])
            }
            [formatted_team.update({hero: hero in members_as_list(team)}) for hero in all_heros]
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

        avg_power = []
        for hero in all_heros:
            # teams with this hero present
            teams = normed_data[normed_data[hero]]['power']
            power = teams.mean()
            count = teams.count()
            avg_power.append({'hero': hero, 'avg_power': power, 'count': count})

        for item in sorted(avg_power, key=lambda k: k['avg_power'], reverse=True):
            print("{},{},{}".format(item['hero'], int(item['avg_power']), item['count']))


if __name__ == '__main__':
    main()
