from django.db import models
from django.db.models import Q
from django.db.models import QuerySet
from collections import Counter

# Create your models here.


class Card(models.Model):

    class Meta:
        unique_together = (("suit", "rank"),)

    class Suit(models.IntegerChoices):
        SPADE = 4
        HEART = 3
        DIAMOND = 2
        CLUB = 1

    suit = models.IntegerField(choices=Suit)

    class Rank(models.IntegerChoices):
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5
        SIX = 6
        SEVEN = 7
        EIGHT = 8
        NINE = 9
        TEN = 10
        JACK = 11
        QUEEN = 12
        KING = 13
        ACE = 14

    rank = models.IntegerField(choices=Rank)

    def __str__(self) -> str:
        return f"{self.Rank(self.rank).name} {self.Suit(self.suit).name[0]}"

    def __gt__(self, other: "Card") -> bool:
        return self.rank > other.rank

    def __lt__(self, other: "Card") -> bool:
        return self.rank < other.rank

    @property
    def all_hands(self) -> QuerySet["Hand"]:
        Hand.objects.filter(
            Q(card5=self)
            | Q(card4=self)
            | Q(card3=self)
            | Q(card2=self)
            | Q(card1=self)
        )


class Hand(models.Model):

    class Meta:
        unique_together = (
            (
                "card1",
                "card2",
                "card3",
                "card4",
                "card5",
            ),
        )

    card1 = models.ForeignKey(
        Card, on_delete=models.CASCADE, related_name="hand1s"
    )
    card2 = models.ForeignKey(
        Card, on_delete=models.CASCADE, related_name="hand2s"
    )
    card3 = models.ForeignKey(
        Card, on_delete=models.CASCADE, related_name="hand3s"
    )
    card4 = models.ForeignKey(
        Card, on_delete=models.CASCADE, related_name="hand4s"
    )
    card5 = models.ForeignKey(
        Card, on_delete=models.CASCADE, related_name="hand5s"
    )

    class HandType(models.IntegerChoices):

        STRAIGHT_FLUSH = 9
        QUADS = 8
        FULL_HOUSE = 7
        FLUSH = 6
        STRAIGHT = 5
        TRIPS = 4
        TWO_PAIR = 3
        PAIR = 2
        HIGH_CARD = 1

    hand_type = models.IntegerField(choices=HandType, db_index=True)

    rank = models.PositiveIntegerField(db_index=True)

    def __str__(self) -> str:
        return f"{self.HandType(self.hand_type).name} (rank: {self.rank}): {self.card5} {self.card4} {self.card3} {self.card2} {self.card1}"

    @property
    def cards(self) -> list[Card]:
        return [self.card5, self.card4, self.card3, self.card2, self.card1]

    @property
    def ranks(self) -> list[Card.Rank]:
        return [card.rank for card in self.cards]

    @property
    def suits(self) -> list[Card.Suit]:
        return [card.suit for card in self.cards]

    def _get_comparison_array(self) -> list[Card.Rank]:
        match self.hand_type:
            case self.HandType.STRAIGHT_FLUSH:
                if Card.Rank.ACE in self.ranks and Card.Rank.FIVE in self.ranks:
                    return [Card.Rank.FIVE]
                return [max(self.ranks)]
            case self.HandType.QUADS:
                counts = {v: k for (k, v) in Counter(self.ranks).items()}
                return [counts[4], counts[1]]
            case self.HandType.FULL_HOUSE:
                counts = {v: k for (k, v) in Counter(self.ranks).items()}
                return [counts[3], counts[2]]
            case self.HandType.FLUSH:
                return sorted(self.cards, reverse=True)
            case self.HandType.STRAIGHT:
                if Card.Rank.ACE in self.ranks and Card.Rank.FIVE in self.ranks:
                    return [Card.Rank.FIVE]
                return [max(self.ranks)]
            case self.HandType.TRIPS:
                counts = {v: k for (k, v) in Counter(self.ranks).items()}
                trip = counts[3]
                kickers = [rank for rank in self.ranks if rank != trip]
                return [trip] + sorted(kickers, reverse=True)
            case self.HandType.TWO_PAIR:
                counter = Counter(self.ranks)
                counts = {v: k for (k, v) in Counter(self.ranks).items()}
                pairs = sorted(
                    [key for (key, value) in counter.items() if value == 2],
                    reverse=True,
                )
                return pairs + [counts[1]]
            case self.HandType.PAIR:
                counter = Counter(self.ranks)
                kickers = []
                pair = []
                for k, v in counter.items():
                    if v == 2:
                        pair.append(k)
                    else:
                        kickers.append(k)
                return pair + sorted(kickers, reverse=True)
            case self.HandType.HIGH_CARD:
                return sorted(self.ranks, reverse=True)
