from setuptools import setup

setup(
    name = "CardShuffle",
    version = "0.1",
    packages = ['cardshuffle', 'twisted.plugins'],
    install_requires = ['twisted'],
    description = "Card Shuffle server",
    author = "Robert Lehmann",
    author_email = "mail@robertlehmann.de",
)
