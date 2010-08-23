from twisted.application.service import ServiceMaker

CardShuffle = ServiceMaker(
    "CardShuffle Server",
    "cardshuffle.tap",
    "A Card Shuffle lobby service.",
    "cardshuffle")
