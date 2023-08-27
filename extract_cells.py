import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pickle
import json

def show(img):
    cv2.imshow('13', img)
    cv2.waitKey(1)
    while True:
        k = cv2.waitKey(1)
        if k == 27:
            break
    cv2.destroyAllWindows()
def show_2x(img, zoom=2):
    #print(img.shape[0],img.shape[1])
    show(cv2.resize(img, [img.shape[1] * zoom,img.shape[0] * zoom], cv2.INTER_AREA))  
def load_images(path):
    table_image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    table_image_alpha = table_image[:,:,3]
    ret, table_image_alpha = cv2.threshold(table_image_alpha, 125, 255, cv2.THRESH_BINARY)
    table_image = cv2.cvtColor(table_image[:,:,3], cv2.COLOR_GRAY2BGR)
    return table_image, table_image_alpha
def extract_cells_cords(table_image_alpha):
    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(table_image_alpha, 4, cv2.CV_32S)
    components = np.zeros([table_image_alpha.shape[0], table_image_alpha.shape[1], 1], dtype="uint8")
    for i in range(1, labels_count):
        area = stats[i, cv2.CC_STAT_AREA] 
        if (area > 700):
            componentMask = (labels == i).astype("uint8") * 255
            components = cv2.bitwise_or(components, componentMask, componentMask)
    contours, hierarchy = cv2.findContours(components,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

    cells = []
    for cnt_id, cnt in enumerate(contours):
        x,y,w,h = cv2.boundingRect(cnt)
        if w > 20:
            cells.append([x,y,w,h])
    cells.pop(-1)# последняя ячейка это вся таблица целиком
    cells = sorted(cells, key=lambda x: x[1] // 2 // 2)
    cells_wc = list(map(lambda x: (x[1] // 2 // 2), cells))
    cells_by_row = []
    cur_line = 0
    cur_cells = []
    for row_n in range(len(cells_wc)):
        if cells_wc[row_n] == cur_line:
            cur_cells.append(cells[row_n])
        else:
            cells_by_row.append(sorted(cur_cells, key=lambda x: x[0]))
            cur_line = cells_wc[row_n]
            cur_cells = [cells[row_n]]
    cells_by_row.append(sorted(cur_cells, key=lambda x: x[0]))
    return cells_by_row
def split_into_tables(table_json):
    def get_pattern(row):
        return list(map(lambda x: x['width'], row))

    tables_json = []
    current_pattern = get_pattern(table_json[0])
    current_table = []
    for row in table_json:
        pattern = get_pattern(row)
        #print(pattern)
        if pattern == current_pattern:
            current_table.append(row)
        else:
            tables_json.append({'pattern': current_pattern, 'table': current_table})
            current_table = [row]
            current_pattern = pattern
    tables_json.append({'pattern': current_pattern, 'table': current_table})
    return tables_json


def extract_cells(card_name, save=False):
    table_image, table_image_alpha = load_images('old/' + card_name + '.png')
    cells_by_row = extract_cells_cords(table_image_alpha)
    #pickle.dump(cells_by_row, open('cells.dat', 'wb'))
    imgs = []
    table_json = []
    cells_left = 99999
    for row in range(len(cells_by_row)):
        cells = cells_by_row[row]
        row_json = []
        for cell_id, cell in enumerate(cells):
            row_json.append(dict())
            x,y,w,h = cell
            cells_left = min([cells_left, x])
            row_json[-1]['bbox'] = [x, x+w, y, y+h]
            cell_img = table_image[y:h+y,x:w+x]
            #remove white borders
            _, thresh = cv2.threshold(cell_img, 20, 255, cv2.THRESH_BINARY_INV)
            thresh_gray = cv2.cvtColor(thresh, cv2.COLOR_RGB2GRAY)
            contours, _ = cv2.findContours(thresh_gray,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
            cells = []
            cnt = contours[-1]
            x,y,w,h = cv2.boundingRect(cnt)
            cell_img = cell_img[y:h+y,x:w+x]
            #show(cell_img)
            imgs.append(cell_img)
            if save:
                cv2.imwrite(f'cells/{card_name}_{row}_{cell_id}.png', cell_img)
        table_json.append(row_json)

    cells_width = []
    for row_n, row in enumerate(cells_by_row):
        for cell_n, cell in enumerate(row):
            table_json[row_n][cell_n]['width'] = cell[2] // 2 // 2
        if len(row) > 0:
            if row[0][0] // 2 // 2 > cells_left:
                table_json[row_n].insert(0, {'bbox': [0,1,0,1], 'width': row[0][0] // 2 // 2})
        cells_width.append(list(map(lambda x: [x[0] // 2 // 2, x[2] // 2 // 2], row)))
    tables_json = split_into_tables(table_json)
    return cells_width, tables_json
if __name__  == '__main__':
    tables = dict()
    card_names = list(map(lambda x: x.split('.png')[0], os.listdir('old')))
    for card_name in card_names:
        #card_name = 'climb-rates-speed'
        cells_width, tables_json = extract_cells(card_name)
        tables[card_name] = tables_json
        #break
    json.dump(tables, open('tables.json', 'w'))
