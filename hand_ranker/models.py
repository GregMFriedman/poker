from django.db import models

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

    rank = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.rank}: {self.card5} {self.card4} {self.card3} {self.card2} {self.card1}"
