import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.table as mtable
import pandas as pd
import numpy as np
from test import read_csv

def read_csv_(filepath):
    #table = pd.read_csv('t1.csv', encoding='utf-8', header=None)
    with open(filepath, encoding='utf-8-sig') as f:
        pages = f.read().split('$newpage$\n')[1:]
        for page in pages:
            heading = page.split('\n')[0]
            tables = page.split('$newtable$')[1:]
            print(tables[0])
            #              table = pd.read_csv('t1.csv', encoding='utf-8', header=None)

data = read_csv('t1.csv')[2]

#a = 1 / 0

#df = pd.read_csv('t1.csv', encoding='utf-8', header=None)

fig, ax = plt.subplots(1,1, figsize=(4, 4), dpi=256)
fig.patch.set_visible(False)
ax.axis('off')
table = ax.table(cellText=data, loc='center', cellLoc='left')
table.auto_set_font_size(False)
table.set_fontsize(13)


heights = []
for row_n, row in enumerate(data):
    for col in row:
        if len(col) > 20:
            heights.append(row_n)


for key, cell in table.get_celld().items():
    cell.PAD = 0.04
    row, col = key
    #if row in [1, 4] and col > -1:
    if row in heights:
        cell.set_height(cell.get_height() * 2)
    else:
        cell.set_height(cell.get_height())
    cell.set_alpha(0.5)
    cell.set_text_props(font='Courier New', weight='bold', wrap=True, ha='left')
    #y = cell.xy[1]
    #cell.set_edgecolor('r') # нарисуем границы отдельно а потом сложим получив прозрачный фон
    #ax.axhline(y, color='r', linewidth=4)

plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
#plt.show()
#table.scale(1, 2)
plt.savefig('res.png')#, bbox_inches='tight')