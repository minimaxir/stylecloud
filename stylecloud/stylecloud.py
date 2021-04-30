from icon_font_to_png.icon_font import IconFont
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import csv
import os
from PIL import Image
from matplotlib.colors import to_rgb
import numpy as np
import fire
from shutil import rmtree
from pkg_resources import resource_filename
from typing import List, Union

STATIC_PATH = resource_filename(__name__, "static")


def file_to_text(file_path: str):
    """
    Reads a text file, or if the file is a .csv,
    read as a dict of word/weights.
    """

    if not file_path.endswith(".csv"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return text
    else:  # parse as a CSV

        with open(file_path, "r", encoding="utf-8") as f:
            r = csv.reader(f)
            header = next(r)
            assert len(header) <= 2, "The input CSV has too many columns."

            # If a single-column CSV, read as a bulk text
            if len(header) == 1:
                texts = ""
                for row in r:
                    texts += row[0] + "\n"
            # If a two-column CSV, read as words/weights
            elif len(header) == 2:
                texts = {}
                for row in r:
                    texts[row[0]] = float(row[1])
        return texts


def gen_fa_mask(
    icon_name: str = "fas fa-grin",
    size: int = 512,
    icon_dir: str = ".temp",
    pro_icon_path: str = None,
    pro_css_path: str = None,
):
    """
    Generates a Font Awesome icon mask from the given FA prefix + name.
    """

    # FA prefixes which map to a font file.
    font_files = {
        "fas": "fa-solid-900.ttf",
        "far": "fa-regular-400.ttf",
        "fab": "fa-brands-400.ttf",
    }

    icon_prefix = icon_name.split(" ")[0]
    icon_name_raw = icon_name.split(" ")[1]

    css_path = pro_css_path or os.path.join(STATIC_PATH, "fontawesome.min.css")
    ttf_path = pro_icon_path or os.path.join(STATIC_PATH, font_files[icon_prefix])

    icon = IconFont(css_file=css_path, ttf_file=ttf_path)

    # If a length and width are provided, make icon the smaller of the two
    if isinstance(size, tuple):
        size = min(size)

    icon.export_icon(
        icon=icon_name_raw[len(icon.common_prefix) :],
        size=size,
        filename="icon.png",
        export_dir=icon_dir,
    )


def gen_palette(palette: str):
    """Generates the corresponding palette function from `palettable`."""
    palette_split = palette.split(".")
    palette_name = palette_split[-1]

    # https://stackoverflow.com/a/6677505
    palette_func = getattr(
        __import__(
            "palettable.{}".format(".".join(palette_split[:-1])),
            fromlist=[palette_name],
        ),
        palette_name,
    )
    return palette_func


def gen_mask_array(icon_dir: str, invert_mask: bool, size: int):
    """Generates a numpy array of an icon mask."""
    icon = Image.open(os.path.join(icon_dir, "icon.png"))

    if isinstance(size, int):
        size = (size, size)

    # https://stackoverflow.com/a/2563883
    icon_w, icon_h = icon.size
    icon_mask = Image.new("RGBA", icon.size, (255, 255, 255, 255))
    icon_mask.paste(icon, icon)
    mask = Image.new("RGBA", size, (255, 255, 255, 255))
    mask_w, mask_h = mask.size
    offset = ((mask_w - icon_w) // 2, (mask_h - icon_h) // 2)
    mask.paste(icon_mask, offset)
    mask_array = np.array(mask, dtype="uint8")

    if invert_mask:
        mask_array = np.invert(mask_array)

    return mask_array


def gen_gradient_mask(
    size: int,
    palette: str,
    icon_dir: str = ".temp",
    gradient_dir: str = "horizontal",
    invert_mask: bool = False,
):
    """Generates a gradient color mask from a specified palette."""
    mask_array = gen_mask_array(icon_dir, invert_mask, size)
    mask_array = np.float32(mask_array)

    palette_func = gen_palette(palette)
    gradient = palette_func.mpl_colormap(np.linspace(0.0, 1.0, size))

    # matplotlib color maps are from range of (0, 1). Convert to RGB.
    gradient *= 255.0

    # Add new axis and repeat gradient across it.
    gradient = np.tile(gradient, (size, 1, 1))

    # if vertical, transpose the gradient.
    if gradient_dir == "vertical":
        gradient = np.transpose(gradient, (1, 0, 2))

    # Turn any nonwhite pixels on the icon into the gradient colors.
    white = (255.0, 255.0, 255.0, 255.0)
    mask_array[mask_array != white] = gradient[mask_array != white]

    image_colors = ImageColorGenerator(mask_array)
    return image_colors, np.uint8(mask_array)


def color_to_rgb(color):
    """Converts a color to a RGB tuple from (0-255)."""
    if isinstance(color, tuple):
        # if a RGB tuple already
        return color
    else:
        # to_rgb() returns colors from (0-1)
        color = tuple(int(x * 255) for x in to_rgb(color))
        return color


def gen_stylecloud(
    text: str = None,
    file_path: str = None,
    size: int = 512,
    icon_name: str = "fas fa-flag",
    palette: str = "cartocolors.qualitative.Bold_5",
    colors: Union[str, List[str]] = None,
    background_color: str = "white",
    max_font_size: int = 200,
    max_words: int = 2000,
    stopwords: bool = True,
    custom_stopwords: Union[List[str], set] = STOPWORDS,
    add_stopwords: bool = False,
    icon_dir: str = ".temp",
    output_name: str = "stylecloud.png",
    gradient: str = None,
    font_path: str = os.path.join(STATIC_PATH, "Staatliches-Regular.ttf"),
    random_state: int = None,
    collocations: bool = True,
    invert_mask: bool = False,
    pro_icon_path: str = None,
    pro_css_path: str = None,
):
    """Generates a stylecloud!
    :param text: Input text. Best used if calling the function directly.
    :param file_path: File path of the input text/CSV. Best used on the CLI.
    :param size: Size (length and width in pixels) of the stylecloud.
    :param icon_name: Icon Name for the stylecloud shape. (e.g. 'fas fa-grin')
    :param palette: Color palette (via palettable)
    :param colors: Custom color(s) for text (name or hex). Overrides palette.
    :param background_color: Background color (name or hex).
    :param max_font_size: Maximum font size in the stylecloud.
    :param max_words: Maximum number of words to include in the stylecloud.
    :param stopwords: Boolean to filter out common stopwords.
    :param custom_stopwords: list of custom stopwords.
    :param add_stopwords: Whether to use custom_stopwords to add to default
    :param icon_dir: Temp directory to store the icon mask image.
    :param output_name: Output file name of the stylecloud.
    :param gradient: Direction of gradient. (if not None, will use gradient)
    :param font_path: Path to .ttf file for font to use in stylecloud.
    :param random_state: Controls random state of words and colors.
    :param collocations: Whether to include collocations (bigrams) of two words.
    :param invert_mask: Whether to invert the icon mask.
    :param pro_icon_path: Path to Font Awesome Pro .ttf file if using FA Pro.
    :param pro_css_path: Path to Font Awesome Pro .css file if using FA Pro.
    """

    assert any([text, file_path]), "Either text or file_path must be specified."

    if file_path:
        text = file_to_text(file_path)

    gen_fa_mask(icon_name, size, icon_dir, pro_icon_path, pro_css_path)

    if gradient and colors is None:
        pal_colors, mask_array = gen_gradient_mask(
            size, palette, icon_dir, gradient, invert_mask
        )
    else:  # Color each word randomly from the palette
        mask_array = gen_mask_array(icon_dir, invert_mask, size)
        if colors:
            # if specifying a single color string
            if isinstance(colors, str):
                colors = [colors]

            # iterate through each color to ensure correct RGB format.
            # see matplotlib docs on how colors are decoded:
            # https://matplotlib.org/3.1.1/api/colors_api.html
            colors = [color_to_rgb(color) for color in colors]

        else:
            palette_func = gen_palette(palette)
            colors = palette_func.colors

        def pal_colors(word, font_size, position, orientation, random_state, **kwargs):
            rand_color = np.random.randint(0, len(colors))
            return tuple(colors[rand_color])

    if add_stopwords:
        custom_stopwords.extend(STOPWORDS)

    # cleanup icon folder
    rmtree(icon_dir)

    wc = WordCloud(
        background_color=background_color,
        font_path=font_path,
        max_words=max_words,
        mask=mask_array,
        stopwords=custom_stopwords if stopwords else None,
        max_font_size=max_font_size,
        random_state=random_state,
        collocations=collocations,
    )

    # generate word cloud
    if isinstance(text, str):
        wc.generate_from_text(text)
    else:  # i.e. a dict of word:value from a CSV
        if stopwords:  # manually remove stopwords since otherwise ignored
            text = {k: v for k, v in text.items() if k not in custom_stopwords}
        wc.generate_from_frequencies(text)
    wc.recolor(color_func=pal_colors, random_state=random_state)
    wc.to_file(output_name)


def stylecloud_cli(**kwargs):
    """Entrypoint for the stylecloud CLI."""
    fire.Fire(gen_stylecloud)
