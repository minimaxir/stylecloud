from icon_font_to_png.icon_font import IconFont


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

    icon = IconFont(css_file='static/fontawesome.min.css',
                    ttf_file='static/{}'.format(font_files[icon_prefix]))

    icon.export_icon(icon=icon_name_raw[len(icon.common_prefix):],
                     size=300)
