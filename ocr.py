import cv2
import pytesseract
import json



#import pickle

#cells_by_row = pickle.load(open('cells.dat', 'rb'))

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\epchi\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
#card_name = 'descend-rates'

def show(img):
    cv2.imshow('13', img)
    cv2.waitKey(1)
    while True:
        k = cv2.waitKey(1)
        if k == 27:
            break
    cv2.destroyAllWindows()


def one_cell_text(cell, table_image):
    bbox = cell['bbox']
    cell_img = table_image[bbox[2]:bbox[3], bbox[0]:bbox[1]]
    _, thresh = cv2.threshold(cell_img, 20, 255, cv2.THRESH_BINARY_INV)
    thresh_gray = cv2.cvtColor(thresh, cv2.COLOR_RGB2GRAY)
    contours, _ = cv2.findContours(thresh_gray,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
    cells = []
    cnt = contours[-1]
    x,y,w,h = cv2.boundingRect(cnt)
    cell_img = cell_img[y:h+y,x:w+x]

    zoom = 4
    if cell_img.shape[1] < 100:
        zoom += 2
    img_rgb = 255 - cv2.cvtColor(cell_img, cv2.COLOR_BGR2GRAY)

    img_rgb = cv2.resize(img_rgb, [img_rgb.shape[1] * zoom,img_rgb.shape[0] * zoom], cv2.INTER_AREA)

    config = ''
    if img_rgb.shape[0] < 30 * zoom:
        config = '--psm 7'
    text = pytesseract.image_to_string(cell_img, lang='rus+eng', timeout=10000, config=config)
    #show(cell_img)
    if text == '':
        text = pytesseract.image_to_string(cell_img, lang='rus+eng', timeout=10000)
    if text == '':
        text=f'ET' + config
        #print(zoom)
        #show(img_rgb)
    return text.replace('\n', ' ')
        
    return text.replace('  ', ' ')

def parse_all(tables):
    for card_name in tables:
        table_image = cv2.imread(f'old/{card_name}.png', cv2.IMREAD_UNCHANGED)
        table_image = cv2.cvtColor(table_image[:,:,3], cv2.COLOR_GRAY2BGR)
        for table in tables[card_name]:
            for row in table['table']:
                for cell in row:
                    cell['text'] = one_cell_text(cell, table_image)
    return tables

if __name__ == '__main__':
    tables = json.load(open('tables.json'))
    tables = parse_all(tables)
    json.dump(tables, open('tables_with_text.json', 'w', encoding='utf-8'), ensure_ascii=False)