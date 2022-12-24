import sys
import matplotlib.pyplot as plt
import seaborn as sns
from zquest.extract import ZeldaClassicReader


def to_index(x: int, y: int, w: int) -> int:
    return x + y * w


# Number of tiles in a screen
screen_width = 16
screen_height = 11

reader = ZeldaClassicReader(sys.argv[1])
reader.read_qst()

heat_map = [[0 for x in range(screen_width * 2)] for y in range(screen_height * 2)]
for map in reader.maps:
    for screen in (s for s in map.screens if s.valid):
        for sx in range(screen_width):
            for sy in range(screen_height):
                combo_index = screen.data[to_index(sx, sy, screen_width)]
                if combo_index > len(reader.combos):
                    continue

                x = sx * 2
                y = sy * 2
                walk = reader.combos[combo_index].walk
                heat_map[y][x] += 1 if (walk & 1) > 0 else 0
                heat_map[y + 1][x] += 1 if (walk & 2) > 0 else 0
                heat_map[y][x + 1] += 1 if (walk & 4) > 0 else 0
                heat_map[y + 1][x + 1] += 1 if (walk & 8) > 0 else 0


sns.heatmap(heat_map, square=True, xticklabels=False, yticklabels=False)
plt.show()
