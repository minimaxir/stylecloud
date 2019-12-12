# stylecloud

![](https://github.com/minimaxir/stylecloud-examples/raw/master/stylecloud_banner.png)

Generate stylistic wordclouds, including gradients and icon shapes!

stylecloud is a Python package that leverages the popular [word_cloud](https://github.com/amueller/word_cloud) package, adding useful features to create truly unique word clouds!

* Icon shapes (of any size!) for wordclouds (via [Font Awesome](https://fontawesome.com) 5.12.0 Free, or your own [Font Awesome Pro](https://github.com/minimaxir/stylecloud-examples/tree/master/fa-pro))
* Support for advanced color palettes (via [palettable](https://jiffyclub.github.io/palettable/))
* Manual color selection for text and backgrounds,
* Directional gradients w/ the aforementioned palettes.
* Supports reading text files and CSVs (either one-column w/ texts, or two columns w/ words+weights).
* Command Line Interface!

This package is a more formal implementation of my [stylistic word cloud project](https://minimaxir.com/2016/05/wordclouds/) from 2016.

## Installation

You can install [stylecloud](https://pypi.org/project/stylecloud/) via pip:

```sh
pip3 install stylecloud
```

## Usage

You can use stylecloud in a Python script or as a standalone CLI app. For example, let's say you have a [text](https://github.com/amueller/word_cloud/blob/master/examples/constitution.txt) of the U.S. Constitution `constitution.txt`.

Python script:

```python
import stylecloud

stylecloud.gen_stylecloud(file_path='constitution.txt')
```

![](https://github.com/minimaxir/stylecloud-examples/raw/master/hello-world/stylecloud1.png)

But you can do so much more! You can use the [free Font Awesome icons](https://fontawesome.com/icons?d=gallery&m=free) to change the shape, change the color palette to one from [palettable](https://jiffyclub.github.io/palettable/) for a custom style, change the background color, and, most importantly, add a gradient so the colors flow in a specified direction!

```python
import stylecloud

stylecloud.gen_stylecloud(file_path='constitution.txt',
                          icon_name='fas fa-dog',
                          palette='colorbrewer.diverging.Spectral_11',
                          background_color='black',
                          gradient='horizontal')
```

![](https://github.com/minimaxir/stylecloud-examples/raw/master/hello-world/stylecloud3.png)

You can also use the CLI for even faster stylecloud generation! For the simple flag stylecloud above:

```sh
stylecloud --file_path constitution.txt
```

For the more complex dog-gradient stylecloud:

```sh
stylecloud --file_path constitution.txt --icon_name 'fas fa-dog' --palette colorbrewer.diverging.Spectral_11 --background_color black --gradient horizontal
```

You can find more examples of styleclouds, including how to make styleclouds from Twitter and Reddit data, in the [stylecloud-examples](https://github.com/minimaxir/stylecloud-examples) repo.

### Custom Colors for stylecloud Text

You can manually specify the color(s) of the text with the `colors` parameter, overriding the palettes. This can be useful for specific branding, or high-contrast visualizations. However, manual color selection will not work with gradients.

```python
import stylecloud

stylecloud.gen_stylecloud(file_path='constitution.txt',
                          colors=['#ecf0f1', '#3498db', '#e74c3c'],
                          background_color='#1A1A1A')
```

```sh
stylecloud --file_path constitution.txt --colors "['#ecf0f1', '#3498db', '#e74c3c']" --background_color '#1A1A1A'
```

![](https://github.com/minimaxir/stylecloud-examples/raw/master/hello-world/stylecloud5.png)

### Stopwords

In order to filter out stopwords in non-English languages or use custom stopwords, you can pass a list of words to the `custom_stopwords` parameter:

```python
import stylecloud
my_long_list = ["thereof", "may", "state", "united states"]

stylecloud.gen_stylecloud(file_path='constitution.txt',
                          custom_stopwords=my_long_list)
```

```sh
stylecloud --file_path constitution.txt --custom_stopwords "[thereof, may, state, united states]"
```

Good resources for stopwords in other languages are the [stop-words Python package](https://github.com/Alir3z4/python-stop-words) and the [ISO stopword collections](https://github.com/stopwords-iso/stopwords-iso).

### Helpful Parameters

These parameters are valid for both the Python function and the CLI (you can use `stylecloud -h` to get this information as well).

* text: Input text. Best used if calling the function directly.
* file_path: File path of the input text/CSV. Best used on the CLI.
* gradient: Direction of gradient. (if not None, the stylecloud will use a directional gradient) [default: `None`]
* size: Size (length and width in pixels) of the stylecloud. [default: `512`]
* icon_name: Icon Name for the stylecloud shape. (e.g. 'fas fa-grin') [default: `fas fa-flag`]
* palette: Color palette (via palettable) [default: `cartocolors.qualitative.Bold_5`]
* colors: Color(s) to use as the text colors. Overrides both gradient and palette if specified [default: `None`]
* background_color: Background color (name or hex) [default: `white`]
* max_font_size: Maximum font size in the stylecloud. [default: `200`]
* max_words: Maximum number of words to include in the stylecloud. [default: `2000`]
* stopwords: Boolean to filter out common stopwords. [default: `True`]
* custom_stopwords: list of custom stopwords. e.g: For other languages than english [default: `STOPWORDS`, via `word_cloud`]
* output_name: Output file name of the stylecloud. [default: `stylecloud.png`]
* font_path: Path to .ttf file for font to use in stylecloud. [default: uses included Staatliches font]
* random_state: Controls random state of words and colors. [default: `None`]
* collocations: Whether to include collocations (bigrams) of two words. Same behavior as base `word_cloud` package. [default: `True`]
* invert_mask: Whether to invert the icon mask, so the words fill the space *except* the icon mask. [default: `False`]
* pro_icon_path: Path to Font Awesome Pro .ttf file if using FA Pro. [default: `None`]
* pro_css_path: Path to Font Awesome Pro .css file if using FA Pro. [default: `None`]

## Helpful Notes

* The primary goal of this package is to create data visualizations of text that provide a unique aesthetic. Word clouds have tradeoffs in terms of a statistically robust data visualization, but this is explicitly prioritizing coolness!
* This package is released as a separate package from `word_cloud` due to the increase in scope and Python dependencies.
* The ideal fonts for generating a good stylecloud are a) bold/high weight in order to increase readability, and b) condensed/low kerning to fit more text. Both of these traits are why [Staatliches](https://fonts.google.com/specimen/Staatliches) is the default font for stylecloud (overriding Droid Sans in the base `word_cloud`).
* You may want to consider doing post-processing after generating a stylecloud: for example, adding color masks, adding perception skew, feed it to a style transfer AI model, etc.
* The default `max_font_size` of `200` is calibrated for the default `size` of `512`. If you increase the `size`, you may want to consider increasing `max_font_size` as well.
* Due to the size of the included Font Awesome font files, they will not be updated on every new minor FA release.
* It's recommended to use FA icons which are large with heavy weight; thin icons might constrain the text too much.
* If using the default random-color-sampling method, it's recommended to use a qualitative palette. Inversely, if using a gradient, it's recommended to use a *non*qualitative palette (e.g. a sequential palette).
  
# Projects Using stylecloud

* [twcloud](https://github.com/minimaxir/twcloud) — Python package + CLI to generate wordclouds of Twitter tweets.

## Maintainer/Creator

Max Woolf ([@minimaxir](https://minimaxir.com))

*Max's open-source projects are supported by his [Patreon](https://www.patreon.com/minimaxir) and [GitHub Sponsors](https://github.com/sponsors/minimaxir). If you found this project helpful, any monetary contributions to the Patreon are appreciated and will be put to good creative use.*

## License

MIT

Font Awesome icon font files included per the terms in its [SIL OFL 1.1 License](https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL).

Staatliches font included per the terms in its [SIL OFL 1.1 License](https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL).
