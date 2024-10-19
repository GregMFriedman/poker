import random
from hand_ranker.models import Card


class Deck:

    cards: list[Card]

    def __init__(self):
        self.new_game()

    def new_game(self):
        self.cards = list(Card.objects.all())
        random.shuffle(self.cards)

    def deal(self, n: int = 1) -> Card:
        for _ in n:
            self.cards.pop()
