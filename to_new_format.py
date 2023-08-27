import json


cards = json.load(open('tables_with_text_edited.json', encoding='utf-8'))
cards_new = dict()
for card in cards:
    new_tables = []
    for table in cards[card]:
        #print(table)
        new_tables.append({'pattern': list(map(lambda x: x['width'], table[0])), 'table': table})
    cards_new[card] = new_tables
json.dump(cards_new, open('tables_with_text_edited_v2.json', 'w', encoding='utf-8'), ensure_ascii=False)