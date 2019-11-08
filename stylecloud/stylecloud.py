from icon_font_to_png.icon_font import IconFont
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import csv
import os
from PIL import Image
from matplotlib.colors import makeMappingArray
import numpy as np
import fire
from shutil import rmtree
from pkg_resources import resource_filename

STATIC_PATH = resource_filename(__name__, 'static')


def file_to_text(file_path):
    """
    Reads a text file, or if the file is a .csv,
    read as a dict of word/weights.
    """

    if not file_path.endswith('.csv'):
        with open(file_path, 'r') as f:
            text = f.read()
        return text
    else:  # parse as a CSV

        with open(file_path, 'r') as f:
            r = csv.reader(f)
            header = next(r)
            assert len(header) <= 2, "The input CSV has too many columns."

            # If a single-column CSV, read as a bulk text
            if len(header) == 1:
                texts = ''
                for row in r:
                    texts += row[0] + '\n'
            # If a two-column CSV, read as words/weights
            elif len(header) == 2:
                texts = {}
                for row in r:
                    texts[row[0]] = float(row[1])
        return texts


def gen_fa_mask(icon_name='fas fa-grin', size=512, icon_dir='.temp'):
    """
    Generates a Font Awesome icon mask from the given FA prefix + name.
    """

    # FA prefixes which map to a font file.
    font_files = {'fas': 'fa-solid-900.ttf',
                  'far': 'fa-regular-400.ttf',
                  'fab': 'fa-brands-400.ttf'}

    icon_prefix = icon_name.split(' ')[0]
    icon_name_raw = icon_name.split(' ')[1]

    icon = IconFont(css_file=os.path.join(STATIC_PATH, 'fontawesome.min.css'),
                    ttf_file=os.path.join(STATIC_PATH, font_files[icon_prefix]))

    icon.export_icon(icon=icon_name_raw[len(icon.common_prefix):],
                     size=size,
                     filename="icon.png",
                     export_dir=icon_dir)


def gen_palette(palette):
    """Generates the corresponding palette function from `palettable`."""
    palette_split = palette.split(".")
    palette_name = palette_split[-1]

    # https://stackoverflow.com/a/6677505
    palette_func = getattr(__import__('palettable.{}'.format(
        ".".join(palette_split[:-1])), fromlist=[palette_name]), palette_name)
    return palette_func


def gen_mask_array(icon_dir, dtype):
    """Generates a numpy array of an icon mask."""
    icon = Image.open(os.path.join(icon_dir, 'icon.png'))
    mask = Image.new("RGBA", icon.size, (255, 255, 255, 255))
    mask.paste(icon, icon)
    mask_array = np.array(mask, dtype=dtype)

    return mask_array


def gen_gradient_mask(size, palette, icon_dir='.temp',
                      gradient_dir='horizontal'):
    """Generates a gradient color mask from a specified palette."""
    mask_array = gen_mask_array(icon_dir, 'float32')

    palette_func = gen_palette(palette)
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
    return image_colors, np.uint8(mask_array)


def gen_stylecloud(text=None,
                   file_path=None,
                   size=512,
                   icon_name='fas fa-flag',
                   palette='cartocolors.qualitative.Bold_6',
                   background_color="white",
                   max_font_size=200,
                   max_words=2000,
                   stopwords=True,
                   custom_stopwords=STOPWORDS,
                   icon_dir='.temp',
                   output_name='stylecloud.png',
                   gradient=None,
                   font_path=os.path.join(STATIC_PATH,
                                          'Staatliches-Regular.ttf'),
                   random_state=None):
    """Generates a stylecloud!
    :param text: Input text. Best used if calling the function directly.
    :param file_path: File path of the input text/CSV. Best used on the CLI.
    :param size: Size (length and width in pixels) of the stylecloud.
    :param icon_name: Icon Name for the stylecloud shape. (e.g. 'fas fa-grin')
    :param palette: Color palette (via palettable)
    :param background_color: Background color (name or hex)
    :param max_font_size: Maximum font size in the stylecloud.
    :param max_words: Maximum number of words to include in the stylecloud.
    :param stopwords: Boolean to filter out common stopwords.
    :param custom_stopwords: list of custom stopwords.
    :param icon_dir: Temp directory to store the icon mask image.
    :param output_name: Output file name of the stylecloud.
    :param gradient: Direction of gradient. (if not None, will use gradient)
    :param font_path: Path to .ttf file for font to use in stylecloud.
    :param random_state: Controls random state of words and colors.
    """

    assert any([text, file_path]
               ), "Either text or file_path must be specified."

    if file_path:
        text = file_to_text(file_path)

    gen_fa_mask(icon_name, size, icon_dir)

    if gradient:
        colors, mask_array = gen_gradient_mask(size, palette, icon_dir,
                                               gradient)
    else:  # Color each word randomly from the palette
        mask_array = gen_mask_array(icon_dir, 'uint8')
        palette_func = gen_palette(palette)

        # See also:
        # https://amueller.github.io/word_cloud/auto_examples/a_new_hope.html
        def colors(word, font_size, position,
                   orientation, random_state,
                   **kwargs):
            rand_color = np.random.randint(0, palette_func.number - 1)
            return tuple(palette_func.colors[rand_color])

    # cleanup icon folder
    rmtree(icon_dir)

    wc = WordCloud(background_color=background_color,
                   font_path=font_path,
                   max_words=max_words, mask=mask_array,
                   stopwords=custom_stopwords if stopwords else None,
                   max_font_size=max_font_size, random_state=random_state)

    # generate word cloud
    if isinstance(text, str):
        wc.generate_from_text(text)
    else:  # i.e. a dict of word:value from a CSV
        wc.generate_from_frequencies(text)
    wc.recolor(color_func=colors, random_state=random_state)
    wc.to_file(output_name)


def stylecloud_cli(**kwargs):
    """Entrypoint for the stylecloud CLI."""
    fire.Fire(gen_stylecloud)
