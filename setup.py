from setuptools import setup, find_packages

long_description = '''
Generate stylistic wordclouds, including gradients and icon shapes!

stylecloud is a Python package leverages the popular [word_cloud](https://github.com/amueller/word_cloud) package, adding useful features to create truly unique word clouds!

* Icon shapes for wordclouds (via [Font Awesome](https://fontawesome.com) 5.11.2)
* Support for advanced color palettes (via [palettable](https://jiffyclub.github.io/palettable/))
* Directional gradients w/ the aforementioned palettes.
* Supports reading a file of text, or reading a pre-generated CSV with words and counts.
* Command Line Interface!

This package is a more formal implementation of my [stylistic word cloud project](https://minimaxir.com/2016/05/wordclouds/) from 2016.
'''


setup(
    name='stylecloud',
    packages=['stylecloud'],  # this must be the same as the name above
    version='0.2',
    description="Python package + CLI to generate stylistic wordclouds, " \
    "including gradients and icon shapes!",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Max Woolf',
    author_email='max@minimaxir.com',
    url='https://github.com/minimaxir/stylecloud',
    keywords=['wordcloud', 'data visualization', 'text cool stuff'],
    classifiers=[],
    license='MIT',
    entry_points={
        'console_scripts': ['stylecloud=stylecloud.stylecloud:stylecloud_cli'],
    },
    python_requires='>=3.5',
    include_package_data=True,
    install_requires=['wordcloud', 'icon-font-to-png', 'palettable', 'fire', 'matplotlib']
)
