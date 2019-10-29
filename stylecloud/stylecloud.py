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


def gen_fa_mask(icon_name='fas fa-grin', size=1024, icon_dir='.temp'):
    """
    Generates a Font Awesome icon mask from the given FA prefix + name.
    """

    # FA prefixes which map to a font file.
    font_files = {'fas': 'fa-solid-900.ttf',
                  'far': 'fa-regular-400.ttf',
                  'fab': 'fa-brands-400.ttf'}

    icon_prefix = icon_name.split(' ')[0]
    icon_name_raw = icon_name.split(' ')[1]

    icon = IconFont(css_file=os.path.join('static', 'fontawesome.min.css'),
                    ttf_file=os.path.join('static', font_files[icon_prefix]))

    icon.export_icon(icon=icon_name_raw[len(icon.common_prefix):],
                     size=size,
                     filename="icon.png",
                     export_dir=icon_dir)


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
    white = (255., 255., 255., 255.)
    mask_array[mask_array != white] = gradient[mask_array != white]

    image_colors = ImageColorGenerator(mask_array)
    return image_colors, mask_array


def gen_stylecloud(text=None,
                   size=1024,
                   icon_name='fas fa-grin',
                   palette='matplotlib.Viridis_20',
                   background_color="white",
                   max_font_size=200,
                   max_words=2000,
                   icon_dir='.temp',
                   output_name='stylecloud.png',
                   gradient_dir=None,
                   file_path=None,
                   font_path=os.path.join('static', 'Staatliches-Regular.ttf'),
                   random_state=None):
    """Generates a stylecloud!"""

    assert any([text, file_path]
               ), "Either text or file_path must be specified."

    gen_fa_mask(icon_name, size, icon_dir)
    image_colors, mask_array = gen_gradient_mask(size, palette, icon_dir,
                                                 gradient_dir)

    wc = WordCloud(background_color=background_color,
                   font_path=font_path,
                   max_words=max_words, mask=np.uint8(mask_array),
                   max_font_size=max_font_size, random_state=random_state)

    # generate word cloud
    wc.generate_from_text(text)
    wc.recolor(color_func=image_colors, random_state=random_state)
    wc.to_file(output_name)
