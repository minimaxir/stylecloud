from icon_font_to_png.icon_font import IconFont
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import csv
import os
import importlib
from PIL import Image
from matplotlib.colors import makeMappingArray
import numpy as np


def file_to_text(file_path):
    """
    Reads a text file, or if the file is a .csv, read as a list of word/counts.
    """

    if not file_path.endswith('.csv'):
        with open(file_path, 'r') as f:
            text = f.read()
        return text
    else:  # parse as a CSV
        texts = []
        with open(file_path, 'r') as f:
            r = csv.reader(f)
            for row in r:
                texts.append((row[0], row[1]))
        return texts


def gen_fa_mask(icon_name='fas fa-grin', size=512):
    """
    Generates a Font Awesome icon mask from the given FA prefix + name.
    """

    # FA prefixes which map to a text file.
    font_files = {'fas': 'fa-solid-900.ttf',
                  'far': 'fa-regular-400.ttf',
                  'fab': 'fa-brands-400.ttf'}

    icon_prefix = icon_name.split(' ')[0]
    icon_name_raw = icon_name.split(' ')[1]

    icon = IconFont(css_file=os.path.join('static, fontawesome.min.css'),
                    ttf_file=os.path.join('static', font_files[icon_prefix]))

    icon.export_icon(icon=icon_name_raw[len(icon.common_prefix):],
                     size=size,
                     filename="icon.png",
                     export_dir=".temp")


def gen_gradient_mask(size, palette, icon_dir='.temp',
                      gradient_dir='horizontal'):
    """
    Generates a gradient color mask from a specified palette.
    """
    icon = Image.open(os.path.join(icon_dir, 'icon.png'))
    mask = Image.new("RGB", icon.size, (255, 255, 255))
    mask.paste(icon, icon)

    palette_split = palette.split(".")
    palette_name = palette_split[-1]

    # https://stackoverflow.com/a/6677505
    palette_func = getattr(__import__('palettable.{}'.format(
        ".".join(palette_split[:-1])), fromlist=[palette_name]), palette_name)
    palette = makeMappingArray(size, palette_func.mpl_colormap)

    for y in range(size):
        for x in range(size):
            # Only change nonwhite pixels of icon
            if mask.getpixel((x, y)) != (255, 255, 255):

                color = palette[y] if gradient_dir is "vertical" else palette[x]

                # matplotlib color maps are from range of (0,1). Convert to RGB.
                r = int(color[0] * 255)
                g = int(color[1] * 255)
                b = int(color[2] * 255)

                mask.putpixel((x, y), (r, g, b))

    # create coloring from gradient mask
    image_colors = ImageColorGenerator(np.array(mask))
    return image_colors
