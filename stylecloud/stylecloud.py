from icon_font_to_png.icon_font import IconFont
from wordcloud import WordCloud, STOPWORDS
import csv
import os


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


def gen_fa_mask(icon_name='fas fa-grin'):
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
                    ttf_file=os.path.join('static', font_files[icon_prefix]])

    icon.export_icon(icon=icon_name_raw[len(icon.common_prefix):],
                     size=300)
