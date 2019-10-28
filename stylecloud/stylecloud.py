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
    mask = Image.new("RGBA", icon.size, (255, 255, 255, 255))
    mask.paste(icon, icon)
    mask_array = np.array(mask, dtype='float32')

    palette_split = palette.split(".")
    palette_name = palette_split[-1]

    # https://stackoverflow.com/a/6677505
    palette_func = getattr(__import__('palettable.{}'.format(
        ".".join(palette_split[:-1])), fromlist=[palette_name]), palette_name)
    gradient = np.array(makeMappingArray(size, palette_func.mpl_colormap))

    # matplotlib color maps are from range of (0, 1). Convert to RGB.
    gradient *= 255.

    # Add new axis and repeat gradient across it.
    gradient = np.tile(gradient, (size, 1, 1))

    # if vertical, transpose the gradient.
    if gradient_dir == 'vertical':
        gradient = np.transpose(gradient, (1, 0, 2))

    # Turn any nonwhite pixels on the icon into the gradient colors.
    mask_array[mask_array != (255., 255., 255., 255.)
               ] = gradient[mask_array != (255., 255., 255., 255.)]

    image_colors = ImageColorGenerator(mask_array)
    return image_colors
