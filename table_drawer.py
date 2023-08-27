from PIL import Image, ImageDraw, ImageFont
import textwrap


class TableDrawing():
    def __init__(self, cell_widths_fr:list[int], font_path:str, font_size:int,
                 width=1024, color=(0,0,0,255), background=(0,0,0,0),
                 h_padding=0, v_padding=0, spacing=0, border_width=2, border_color=(0,0,0,255)) -> None:
        
        self.font = ImageFont.truetype(font_path, font_size, encoding='unic')
        self.font_size = font_size
        self.width = width
        self.color = color
        self.background = background
        self.h_padding = h_padding if h_padding else int(font_size * 0.5)
        self.v_padding = v_padding if v_padding else int(font_size * 0.5)
        self.spacing = spacing if spacing else int(font_size * 0.1)
        self.border_width = border_width
        all_cells_width_fr = sum(cell_widths_fr)
        all_cells_w = (width - border_width * (len(cell_widths_fr) + 1))

        self.cell_widths_fr = cell_widths_fr
        self.all_cells_w = all_cells_w
        self.all_cells_width_fr = all_cells_width_fr

        self.cell_widths = [int(all_cells_w * cell_fr / all_cells_width_fr) for cell_fr in cell_widths_fr]
        self.border_color = border_color
        self.symbol_width = 0.6 * font_size
        self.image = Image.new('RGBA', (width, self.border_width))
        self.cell_heights = []
        self.rows = 0

    def __iadd__(self, row):
        self.add_row(row)
        return self

    def add_row(self, row):
        images:list[Image.Image] = []
        height = 0
        for col_n, col in enumerate(row):
            images.append(self.add_cell(col, self.cell_widths[col_n]))
            if images[-1].height > height:
                height = images[-1].height
        height += self.border_width
        row_image = Image.new('RGBA', (self.width, height))
        x = 0
        for col_n, cell in enumerate(images):
            row_image.paste(cell, (int(x), (height - cell.height) // 2))
            x += self.cell_widths[col_n] + self.border_width

        t_img = Image.new('RGBA', (self.width, self.image.height + row_image.height))
        t_img.paste(self.image, (0, 0))
        t_img.paste(row_image, (0, self.image.height))
        self.image = t_img
        #t_img.show()
        self.rows += 1
        self.cell_heights.append(height)

    def add_cell(self, text, width):
        align = 'left'
        if text.startswith('$center$'):
            align = 'center'
            text = text[8:]

        lines = text.split('\n')
        result_lines = []
        for line in lines:
            try:
                result_lines += textwrap.wrap(line, width=(width - 2 * self.h_padding) // self.symbol_width)
            except Exception:
                result_lines += [line]#textwrap.wrap(line, width=1)
                align = 'center'
        text = '\n'.join(result_lines)#textwrap.wrap(text, width=(width - 2 * self.h_padding) // self.symbol_width))
        _, _, w, h = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), text, font=self.font, spacing=self.spacing)
        cell_height = self.h_padding * 2 + h
        cell_image = Image.new('RGBA', (width, cell_height))
        draw = ImageDraw.Draw(cell_image)

        
        if align == 'left':
            draw.text((self.h_padding, self.v_padding), text, self.color, self.font, spacing=self.spacing)
        elif align == 'center':
            v_padding = self.v_padding
            v_padding_step = (h + self.spacing) / (text.count('\n') + 1)
            for line in text.split('\n'):
                _, _, w, _ = draw.textbbox((0, 0), line, font=self.font)
                draw.text(((width - w) // 2, int(v_padding)), line, self.color, self.font)
                v_padding += v_padding_step
        
        return cell_image
    
    def draw_borders(self):
        draw = ImageDraw.Draw(self.image)
        h = 0
        for row_n in range(self.rows + 1):
            draw.line((0, h, self.width, h), fill=self.border_color, width=self.border_width)
            if row_n < self.rows:
                h += self.cell_heights[row_n]
        w = 0
        cols = len(self.cell_widths)
        for col_n in range(cols + 1):
            draw.line((w, 0, w, self.image.height), fill=self.border_color, width=self.border_width)
            if col_n < cols:
                w += self.cell_widths[col_n] + self.border_width
            
        #self.image.show()

if __name__ == "__main__": 
    r'C:\Windows\Fonts\cour.ttf'
    r'C:\Windows\Fonts\courbd.ttf'
    drawer = TableDrawing([1,2,1], r'C:\Windows\Fonts\consola.ttf', 28)
    drawer += ['$center$Hello world!Hello world!', 'Hello world!Hello world!Hello', 'world!Hello world!Hello']#world!Hello world!Hello world!Hello world!Hello world!8888888888888'
    drawer += ['$center$Hello world!Hello world!', '$center$Hello world!Hello world!Hello', 'world!Hello world!Hello']
    drawer += ['$center$Hello world!Hello world!', '$center$Hello world!Hello world!Hello', 'world!Hello world!Hello']
    drawer.draw_borders()
    drawer.image.show()