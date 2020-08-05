import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def data_init():
    spreadsheet_file = pd.ExcelFile('data.xlsx')
    worksheets = spreadsheet_file.sheet_names
    island_coordinates = []
    island_numbers = []
    locationDF = pd.read_excel('data.xlsx', sheet_name="Locations", header=None, skiprows=1)
    for index, row in locationDF.iterrows():
        island_coordinates.append([row[1], row[2]])
        island_numbers.append(row[0])
    return [island_numbers, island_coordinates]


def storm_init():
    storms = []
    stormDF = pd.read_excel('data.xlsx', sheet_name="Storms", header=None, skiprows=2)
    for index, row in stormDF.iterrows():
        storms.append([row[0], row[1], row[2]])
    return storms


def main():
    island_numbers, island_coordinates = data_init()
    storms = storm_init()
    #optimum_route = [1, 23, 6, 4, 22, 13, 2, 3, 5, 28, 20, 11, 18, 16, 24, 30, 21, 15, 27, 12, 19, 8, 29, 9, 10, 25, 26, 17, 14, 7, 1]
    #optimum_route = [1, 23, 13, 28, 6, 4, 22, 2, 3, 5, 20, 11, 18, 16, 24, 30, 21, 15, 27, 12, 19, 8, 29, 9, 10, 25, 26, 17, 14, 7, 1]
    optimum_route = [1, 23, 13, 2, 22, 5, 3, 4, 6, 28, 18, 24, 16, 11, 20, 10, 9, 29, 8, 19, 12, 27, 15, 30, 21, 26, 25, 17, 14, 7, 1]
    data = np.array(island_coordinates)
    x, y = data.T
    plt.scatter(x, y)

    for i in range(len(island_coordinates)):
        x = island_coordinates[i][0]
        y = island_coordinates[i][1]
        plt.plot(x, y, 'bo')
        plt.text(x * (1 + 0.01), y * (1 + 0.01), i + 1, fontsize=12)

    for i in range(len(island_coordinates) - 1):
        # i = 0 .... n-1
        plt.plot([island_coordinates[optimum_route[i] - 1][0], island_coordinates[optimum_route[i+1] - 1][0]],
                 [island_coordinates[optimum_route[i] - 1][1], island_coordinates[optimum_route[i+1] - 1][1]], 'green', linestyle=':', marker='')

    for i in range(len(storms)):
        x = storms[i][0]
        y = storms[i][1]
        r = storms[i][2]
        circle1 = plt.Circle((x, y), r, color='r', alpha=0.3, fill=False, label="storm:" + str(i + 1))
        label = plt.annotate(i + 1, xy=(x, y), fontsize=12,
                            verticalalignment='center', horizontalalignment='center')
        plt.gcf().gca().add_artist(circle1)

    plt.gca().set_aspect('equal', adjustable='box')
    plt.draw()

    plt.show()
    plt.savefig('plot.png', dpi=100)


if __name__ == '__main__':
    main()