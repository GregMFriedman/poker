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

    MAX_RANK = 2_598_960

    def __init__(self):
        self.current_rank = self.MAX_RANK
        self.records = []
        self.lookup = {
            (card.rank, card.suit): card for card in Card.objects.all()
        }

    def generate_all_hands_in_order(self):
        self._generate_straight_flushes()
        self._generate_quads()
        self._generate_full_houses()
        self._generate_flushes()
        self._generate_straights()
        self._generate_trips()
        self._generate_two_pairs()
        self._generate_pairs()
        self._generate_high_cards()

    def bulk_write_hands_to_db(self) -> list[Hand]:
        return Hand.objects.bulk_create(self.records)

    def _generate_straight_flushes(self):
        # includes royal flushes
        print(f"Straight Flushes start rank: {self.current_rank}")
        for rank in sorted(Card.Rank, reverse=True):
            count = 0
            if rank.value == 4:
                break
            if rank.value == 5:
                for suit in Card.Suit:
                    hand_kwargs = {
                        f"card{4 - i}": self.lookup[
                            (Card.Rank(rank.value - i), suit)
                        ]
                        for i in range(4)
                    }
                    hand_kwargs["card5"] = self.lookup[(Card.Rank.ACE, suit)]
                    hand_kwargs["rank"] = self.current_rank
                    hand_kwargs["hand_type"] = Hand.HandType.STRAIGHT_FLUSH
                    self.records.append(Hand(**hand_kwargs))
                    count += 1
            else:
                for suit in Card.Suit:
                    hand_kwargs = {
                        f"card{5 - i}": self.lookup[
                            (Card.Rank(rank.value - i), suit)
                        ]
                        for i in range(5)
                    }
                    hand_kwargs["rank"] = self.current_rank
                    hand_kwargs["hand_type"] = Hand.HandType.STRAIGHT_FLUSH
                    self.records.append(Hand(**hand_kwargs))
                    count += 1

            self.current_rank -= count

        print(f"Straight Flushes end rank: {self.current_rank}")

    def _generate_quads(self):
        print(f"Quads start rank: {self.current_rank}")
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
                    hand_kwargs[kicker_key] = self.lookup[(kicker, kicker_suit)]
                    hand_kwargs["rank"] = self.current_rank
                    quad_kwargs = {
                        f"card{start - i}": self.lookup[
                            (quad, Card.Suit(4 - i))
                        ]
                        for i in range(4)
                    }
                    hand_kwargs.update(quad_kwargs)
                    hand_kwargs["hand_type"] = Hand.HandType.QUADS
                    self.records.append(Hand(**hand_kwargs))

                self.current_rank -= 4

        print(f"Quads end rank: {self.current_rank}")

    def _generate_full_houses(self):
        print(f"Full house start rank: {self.current_rank}")
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
                        hand_kwargs[f"card{trip_start - i}"] = self.lookup[
                            (trip, trip_suit)
                        ]
                    for pair_suits in itertools.combinations(Card.Suit, 2):
                        for j, pair_suit in enumerate(pair_suits):
                            hand_kwargs[f"card{pair_start - j}"] = self.lookup[
                                (pair, pair_suit)
                            ]
                        count += 1
                        hand_kwargs["hand_type"] = Hand.HandType.FULL_HOUSE
                        hand_kwargs["rank"] = self.current_rank
                        self.records.append(Hand(**hand_kwargs))
                self.current_rank -= count
        print(f"Full house end rank: {self.current_rank}")

    def _generate_flushes(self):
        print(f"Flush start rank: {self.current_rank}")
        hand_kwargs = {"hand_type": Hand.HandType.FLUSH}
        for card5 in reversed(Card.Rank):
            for card4 in [r for r in reversed(Card.Rank) if r < card5]:
                for card3 in [r for r in reversed(Card.Rank) if r < card4]:
                    for card2 in [r for r in reversed(Card.Rank) if r < card3]:
                        for card1 in [
                            r for r in reversed(Card.Rank) if r < card2
                        ]:
                            if card5.value - card1.value == 4:
                                continue
                            elif set([card1, card2, card3, card4, card5]) == {
                                Card.Rank.ACE,
                                Card.Rank.TWO,
                                Card.Rank.THREE,
                                Card.Rank.FOUR,
                                Card.Rank.FIVE,
                            }:
                                continue
                            count = 0
                            for suit in Card.Suit:
                                hand_kwargs["card5"] = self.lookup[
                                    (card5, suit)
                                ]
                                hand_kwargs["card4"] = self.lookup[
                                    (card4, suit)
                                ]
                                hand_kwargs["card3"] = self.lookup[
                                    (card3, suit)
                                ]
                                hand_kwargs["card2"] = self.lookup[
                                    (card2, suit)
                                ]
                                hand_kwargs["card1"] = self.lookup[
                                    (card1, suit)
                                ]
                                hand_kwargs["rank"] = self.current_rank
                                self.records.append(Hand(**hand_kwargs))
                                count += 1

                            self.current_rank -= count

        print(f"Flush end rank: {self.current_rank}")

    def _generate_straights(self):
        print(f"Straights start rank: {self.current_rank}")
        for rank in sorted(Card.Rank, reverse=True):
            count = 0
            if rank.value == 4:
                break
            if rank.value == 5:
                for combo in itertools.product(Card.Suit, repeat=5):
                    if len(set(combo)) == 1:
                        continue
                    hand_kwargs = {
                        f"card{4 - i}": self.lookup[
                            (Card.Rank(rank.value - i), combo[4 - i])
                        ]
                        for i in range(4)
                    }
                    hand_kwargs["card5"] = self.lookup[
                        (Card.Rank.ACE, combo[0])
                    ]
                    hand_kwargs["rank"] = self.current_rank
                    hand_kwargs["hand_type"] = Hand.HandType.STRAIGHT
                    self.records.append(Hand(**hand_kwargs))
                    count += 1
            else:
                for combo in itertools.product(Card.Suit, repeat=5):
                    if len(set(combo)) == 1:
                        continue
                    hand_kwargs = {
                        f"card{5 - i}": self.lookup[
                            (Card.Rank(rank.value - i), combo[4 - i])
                        ]
                        for i in range(5)
                    }
                    hand_kwargs["rank"] = self.current_rank
                    hand_kwargs["hand_type"] = Hand.HandType.STRAIGHT
                    self.records.append(Hand(**hand_kwargs))
                    count += 1

            self.current_rank -= count
        print(f"Straights end rank: {self.current_rank}")

    def _generate_trips(self):
        print(f"Trips start rank: {self.current_rank}")
        for trip in reversed(Card.Rank):
            for kicker1 in reversed(Card.Rank):
                for kicker2 in reversed(Card.Rank):
                    if len(set([trip, kicker1, kicker2])) < 3:
                        continue
                    elif kicker1 < kicker2:
                        continue
                    if trip > kicker1:
                        trip_start = 5
                        kicker1_key = 2
                        kicker2_key = 1
                    elif trip > kicker2:
                        trip_start = 4
                        kicker1_key = 5
                        kicker2_key = 1
                    else:
                        trip_start = 3
                        kicker1_key = 5
                        kicker2_key = 4

                    count = 0
                    for trip_suit_combos in itertools.combinations(
                        Card.Suit, 3
                    ):
                        hand_kwargs = {"hand_type": Hand.HandType.TRIPS}
                        for i, trip_suit in enumerate(trip_suit_combos):
                            hand_kwargs[f"card{trip_start - i}"] = self.lookup[
                                (trip, trip_suit)
                            ]

                        for kicker1_suit in Card.Suit:
                            hand_kwargs[f"card{kicker1_key}"] = self.lookup[
                                (kicker1, kicker1_suit)
                            ]
                            for kicker2_suit in Card.Suit:
                                hand_kwargs[f"card{kicker2_key}"] = self.lookup[
                                    (kicker2, kicker2_suit)
                                ]
                                hand_kwargs["rank"] = self.current_rank
                                self.records.append(Hand(**hand_kwargs))
                                count += 1

                    self.current_rank -= count

        print(f"Trips end rank: {self.current_rank}")

    def _generate_two_pairs(self):
        print(f"Two Pair start rank: {self.current_rank}")
        for pair1 in reversed(Card.Rank):
            for pair2 in reversed(Card.Rank):
                for kicker in reversed(Card.Rank):
                    if len(set([pair1, pair2, kicker])) < 3:
                        continue
                    elif pair2 > pair1:
                        continue

                    if pair2 > kicker:
                        pair1_start = 5
                        pair2_start = 3
                        kicker_key = 1
                    elif pair1 > kicker:
                        pair1_start = 5
                        pair2_start = 2
                        kicker_key = 3
                    else:
                        pair1_start = 4
                        pair2_start = 2
                        kicker_key = 5

                    count = 0
                    for pair1_suits in itertools.combinations(Card.Suit, 2):
                        for pair2_suits in itertools.combinations(Card.Suit, 2):
                            hand_kwargs = {"hand_type": Hand.HandType.TWO_PAIR}
                            for i, pair_suit1 in enumerate(pair1_suits):
                                hand_kwargs[f"card{pair1_start - i}"] = (
                                    self.lookup[(pair1, pair_suit1)]
                                )
                            for j, pair_suit2 in enumerate(pair2_suits):
                                hand_kwargs[f"card{pair2_start - j}"] = (
                                    self.lookup[(pair2, pair_suit2)]
                                )
                            for kicker_suit in Card.Suit:
                                hand_kwargs[f"card{kicker_key}"] = self.lookup[
                                    (kicker, kicker_suit)
                                ]
                                hand_kwargs["rank"] = self.current_rank
                                self.records.append(Hand(**hand_kwargs))
                                count += 1
                    self.current_rank -= count

        print(f"Two pair end rank: {self.current_rank}")

    def _generate_pairs(self):
        print(f"Pair start rank: {self.current_rank}")
        for pair in reversed(Card.Rank):
            for kicker1 in [r for r in reversed(Card.Rank) if r != pair]:
                for kicker2 in [r for r in reversed(Card.Rank) if r < kicker1]:
                    for kicker3 in [
                        r for r in reversed(Card.Rank) if r < kicker2
                    ]:
                        if len(set([pair, kicker1, kicker2, kicker3])) < 4:
                            continue
                        if pair > kicker1:
                            pair_start = 5
                            kicker1_key = 3
                            kicker2_key = 2
                            kicker3_key = 1
                        elif pair > kicker2:
                            pair_start = 4
                            kicker1_key = 5
                            kicker2_key = 2
                            kicker3_key = 1
                        elif pair > kicker1:
                            pair_start = 3
                            kicker1_key = 5
                            kicker2_key = 4
                            kicker3_key = 1
                        else:
                            pair_start = 2
                            kicker1_key = 5
                            kicker2_key = 4
                            kicker3_key = 3
                        count = 0
                        for pair_suits in itertools.combinations(Card.Suit, 2):
                            hand_kwargs = {"hand_type": Hand.HandType.PAIR}
                            for i, pair_suit in enumerate(pair_suits):
                                hand_kwargs[f"card{pair_start - i}"] = (
                                    self.lookup[(pair, pair_suit)]
                                )
                            for kicker_suits in itertools.product(
                                Card.Suit, repeat=3
                            ):
                                kicker_suit1, kicker_suit2, kicker_suit3 = (
                                    kicker_suits
                                )
                                hand_kwargs[f"card{kicker1_key}"] = self.lookup[
                                    (kicker1, kicker_suit1)
                                ]
                                hand_kwargs[f"card{kicker2_key}"] = self.lookup[
                                    (kicker2, kicker_suit2)
                                ]
                                hand_kwargs[f"card{kicker3_key}"] = self.lookup[
                                    (kicker3, kicker_suit3)
                                ]
                                hand_kwargs["rank"] = self.current_rank
                                count += 1
                                self.records.append(Hand(**hand_kwargs))
                        self.current_rank -= count
        print(f"Pair end rank: {self.current_rank}")

    def _generate_high_cards(self):
        print(f"High card start rank: {self.current_rank}")
        hand_kwargs = {"hand_type": Hand.HandType.HIGH_CARD}
        for card5 in reversed(Card.Rank):
            for card4 in [r for r in reversed(Card.Rank) if r < card5]:
                for card3 in [r for r in reversed(Card.Rank) if r < card4]:
                    for card2 in [r for r in reversed(Card.Rank) if r < card3]:
                        for card1 in [
                            r for r in reversed(Card.Rank) if r < card2
                        ]:
                            if card5.value - card1.value == 4:
                                continue
                            elif set([card1, card2, card3, card4, card5]) == {
                                Card.Rank.ACE,
                                Card.Rank.TWO,
                                Card.Rank.THREE,
                                Card.Rank.FOUR,
                                Card.Rank.FIVE,
                            }:
                                continue
                            count = 0
                            for suit_combo in itertools.product(
                                Card.Suit, repeat=5
                            ):
                                if len(set(suit_combo)) == 1:
                                    continue

                                hand_kwargs["card5"] = self.lookup[
                                    (card5, suit_combo[0])
                                ]
                                hand_kwargs["card4"] = self.lookup[
                                    (card4, suit_combo[1])
                                ]
                                hand_kwargs["card3"] = self.lookup[
                                    (card3, suit_combo[2])
                                ]
                                hand_kwargs["card2"] = self.lookup[
                                    (card2, suit_combo[3])
                                ]
                                hand_kwargs["card1"] = self.lookup[
                                    (card1, suit_combo[4])
                                ]
                                hand_kwargs["rank"] = self.current_rank
                                self.records.append(Hand(**hand_kwargs))
                                count += 1

                            self.current_rank -= count

        print(f"High card end rank: {self.current_rank}")
