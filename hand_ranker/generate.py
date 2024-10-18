import itertools

from .models import Card
from .models import Hand


class CardGenerator:

    def __init__(self):
        self.cards = []

    def create_deck(self) -> list[Card]:
        for rank in Card.Rank:
            for suit in Card.Suit:
                self.cards.append(Card(rank=rank, suit=suit))

        return Card.objects.bulk_create(self.cards)


class RankedHandsGenerator:

    def __init__(self):
        self.current_rank = 2_598_960
        self.records = []

    def _generate_straight_flushes(self):
        # includes royal flushes
        for rank in sorted(Card.Rank, reverse=True):
            count = 0
            if rank.value == 4:
                break
            if rank.value == 5:
                for suit in Card.Suit:
                    hand_kwargs = {
                        f"card{i+2}": Card(
                            rank=Card.Rank(rank.value - i), suit=suit
                        )
                        for i in range(4)
                    }
                    hand_kwargs["card1"] = Card(rank=Card.Rank.ACE, suit=suit)
                    hand_kwargs["rank"] = self.current_rank
                    self.records.append(Hand(**hand_kwargs))
                    count += 1
            else:
                for suit in Card.Suit:
                    hand_kwargs = {
                        f"card{i+1}": Card(
                            rank=Card.Rank(rank.value - i), suit=suit
                        )
                        for i in range(5)
                    }
                    hand_kwargs["rank"] = self.current_rank
                    self.records.append(Hand(**hand_kwargs))
                    count += 1

            self.current_rank -= count

    def _generate_quads(self):
        for quad in sorted(Card.Rank, reverse=True):
            for kicker in sorted(Card.Rank, reverse=True):
                if quad == kicker:
                    continue
                if quad > kicker:
                    kicker_key = "card1"
                    start = 5
                else:
                    kicker_key = "card5"
                    start = 4

                for kicker_suit in Card.Suit:
                    hand_kwargs = {}
                    hand_kwargs[kicker_key] = Card(
                        rank=kicker, suit=kicker_suit
                    )
                    hand_kwargs["rank"] = self.current_rank
                    quad_kwargs = {
                        f"card{start - i}": Card(
                            rank=quad, suit=Card.Suit(4 - i)
                        )
                        for i in range(4)
                    }
                    hand_kwargs.update(quad_kwargs)
                    self.records.append(Hand(**hand_kwargs))

                self.current_rank -= 4

    def _generate_full_houses(self):
        for trip in reversed(Card.Rank):
            for pair in reversed(Card.Rank):
                if trip == pair:
                    continue
                if trip > pair:
                    trip_start = 5
                    pair_start = 2
                else:
                    trip_start = 3
                    pair_start = 5

                count = 0
                for trip_suits in itertools.combinations(Card.Suit, 3):
                    hand_kwargs = {}
                    for i, trip_suit in enumerate(trip_suits):
                        hand_kwargs[f"card{trip_start - i}"] = Card(
                            rank=trip, suit=trip_suit
                        )
                    for pair_suits in itertools.combinations(Card.Suit, 2):
                        for j, pair_suit in enumerate(pair_suits):
                            hand_kwargs[f"card{pair_start - j}"] = Card(
                                rank=pair, suit=pair_suit
                            )
                        count += 1
                        self.records.append(Hand(**hand_kwargs))
                self.current_rank -= count
