from table_drawer import TableDrawing
import cv2
import numpy as np
from PIL import Image
import json
import tqdm

def show(img):
    try:
        cv2.imshow('13', img)
        cv2.waitKey(1)
        while True:
            k = cv2.waitKey(1)
            if k == 27:
                break
        cv2.destroyAllWindows()
    except cv2.error:
        pass

def show_pil(img):
    show(np.array(img)[:,:,3].copy())


font = r'C:\Windows\Fonts\courbd.ttf'
font = r'C:\Users\epchi\FlightGear\154_dev\tu154b_src\Шрифты авиационные\Надписи кабины\AVIA.ttf'
font = r'C:\Users\epchi\FlightGear\154_dev\tu154b_src\Шрифты авиационные\Надписи кабины\lisa_font.ttf'
cards = json.load(open('tables_with_text_edited_v2.json', encoding='utf-8'))
for card_name in tqdm.tqdm(cards):
    #card_name = 'Vstall'
    #print(card_name)
    tables = cards[card_name]
    sum_height = 2
    imgs = []
    for table in tables:
        if len(table['table'][0]) == 0:
            continue
        drawer = TableDrawing(table['pattern'], font, 50)
        for row in table['table']:
            drawer += map(lambda x: x['text'], row)
        drawer.draw_borders()
        sum_height += drawer.image.height
        imgs.append([drawer.image.height, drawer.image])
        #show_pil(drawer.image)
    res = Image.new('RGBA', (1024, sum_height), (0, 0, 0, 0))
    cur_h = drawer.border_width
    for h, img in imgs:
        res.paste(img, (0, cur_h, 1024, cur_h + h))
        cur_h += h# + drawer.border_width
    #show_pil(res)
    padding = 1.06
    new_size = int(max(res.size) * padding)
    square = Image.new('RGBA', [new_size, new_size], (0, 0, 0, 0))
    d_w = (new_size - res.width) / 2
    d_h = (new_size - res.height) / 2
    print((d_w, d_h, new_size - d_w, new_size - d_h), res.size)
    square.paste(res, (int(d_w), int(d_h), int(new_size - d_w), int(new_size - d_h)))
    try:
        square.save(f'new_ru_square/{card_name}.png')
    except Exception as e:
        print(e)