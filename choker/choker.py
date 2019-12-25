from collections import Counter
from itertools import combinations_with_replacement

from numpy import prod
from scipy.special import binom

# Initials
deck = {'Q': 4, 'R': 8, 'B': 8, 'N': 8, 'P': 16}
p_val = {'Q': 9.0, 'R': 5.0, 'B': 3.5, 'N': 3.0, 'P': 1.0}
FLOP_CARDS_CNT = 2
TURN_CARDS_CNT = 4
RIVER_CARDS_CNT = 5
piece_set_values = {
    # with promotions and demotions
    'Q': [0, p_val['Q'], p_val['Q'] + p_val['P'], p_val['Q'] + 2 * p_val['P'], p_val['Q'] + 3 * p_val['P']],
    'R': [0, p_val['R'], 2 * p_val['R'], 2 * p_val['R'] + p_val['P'], 2 * p_val['R'] + 2 * p_val['P'],
          2 * p_val['R'] + 3 * p_val['P']],
    'B': [0, p_val['B'], 2 * p_val['B'], 2 * p_val['B'] + p_val['P'], 2 * p_val['B'] + 2 * p_val['P'],
          2 * p_val['B'] + 3 * p_val['P']],
    'N': [0, p_val['N'], 2 * p_val['N'], 2 * p_val['N'] + p_val['P'], 2 * p_val['N'] + 2 * p_val['P'],
          2 * p_val['N'] + 3 * p_val['P']],
    'P': [0, p_val['P'], 2 * p_val['P'], 2 * p_val['P'] + p_val['R'], 2 * p_val['P'] + p_val['R'] + p_val['Q'],
          2 * p_val['P'] + p_val['R'] + 2 * p_val['Q']]
}

PALLACE_HAND = {'Q': 1, 'R': 1, 'B': 1, 'N': 1, 'P': 1}
PALLACE_MULTIPLIER = {'Q': 2, 'R': 1, 'B': 1, 'N': 1}

# produced initials
# DECK_LIST = [card for card in deck.keys() for n in range(deck[card])]
CARDS_IN_DECK_CNT = sum(deck.values())


# code
def isPallace(c):
    return c == PALLACE_HAND


def isEmpress(c):
    if len(c.keys()) != 2:
        return False
    if sorted(list(c.values())) != [2, 3]:
        return False
    return True


def evaluate_hand_value(hand):
    c = Counter(hand)
    if isPallace(c):
        return sum([p_val[card] * PALLACE_MULTIPLIER[card] for card in PALLACE_MULTIPLIER.keys()])
    if isEmpress(c):
        return sum([piece_set_values[card][2] for card in c.keys()]) + p_val['Q']
    return sum([piece_set_values[card][c.get(card)] for card in c.keys()])


custom_order = {e: i for i, e in enumerate(['P', 'N', 'B', 'R', 'Q'])}
CUSTOM_COMPARATOR = lambda a: custom_order.get(a)
VALUE_COMPARATOR = lambda a: p_val[a] + ord(a) / 100
VALUE_B_AFTER_N_COMPARATOR = lambda a: p_val['N'] + 0.01 * p_val['N'] if a == 'B' else p_val[a]
ALPHA_COMPARATOR = lambda a: ord(a)
NAME_ORDER_COMPARATOR = CUSTOM_COMPARATOR


def create_key_from_string(hand):
    return ''.join(sorted([s for s in hand], key=NAME_ORDER_COMPARATOR))


def evaluate_potential_value(hand, hand_values):
    remaining_cards = Counter(deck) - Counter(hand)
    remaining_count = float(sum(remaining_cards.values()))
    values = []
    for card in remaining_cards.keys():
        hand_new = create_key_from_string(hand + card)
        percentage_of_drawing_this_card = remaining_cards[card] / remaining_count
        hand_value = hand_values[hand_new]["potential"]
        values.append(percentage_of_drawing_this_card * hand_value)
    return round(sum(values), 3)


def probability_of_combination(hand, without=''):
    tmp_deck = Counter(deck) - Counter(without)
    counter = Counter(hand)
    numerator = prod([binom(tmp_deck[c], counter[c]) for c in counter.keys()])
    denominator = binom(CARDS_IN_DECK_CNT, len(hand))
    return round(numerator / denominator * 100, 5)


def all_combinations_in_alpha_order(r):
    return [''.join(hand) for hand in
            list(combinations_with_replacement(create_key_from_string(''.join(deck.keys())), r))]

def hand_description(hand):
    return {"actual": hand[1], "potential": hand[0], "probability": hand[2]}

def calculate_actual_and_potential_hand_value(possible_hands, hand_values_next_level=None):
    return {hand[3]: hand_description(hand) for hand in
            sorted([(evaluate_potential_value(hand, hand_values_next_level) if hand_values_next_level else evaluate_hand_value(hand),
                     evaluate_hand_value(hand),
                     probability_of_combination(hand),
                     hand)
                    for hand in possible_hands]
                   )
            }


def get_distribution_of_values(values):
    cnt = Counter(values.values())
    return {t[0]: t[1] for t in sorted([(e, cnt.get(e)) for e in cnt.keys()])}


# River
possible_river_hands = all_combinations_in_alpha_order(RIVER_CARDS_CNT)
possible_river_hands.remove('QQQQQ')
hand_values_river = calculate_actual_and_potential_hand_value(possible_river_hands)

# turn
possible_turn_hands = all_combinations_in_alpha_order(TURN_CARDS_CNT)
hand_values_turn = calculate_actual_and_potential_hand_value(possible_turn_hands, hand_values_river)

# pre turn
possible_pre_turn_hands = all_combinations_in_alpha_order(FLOP_CARDS_CNT + 1)
hand_values_pre_turn = calculate_actual_and_potential_hand_value(possible_pre_turn_hands, hand_values_turn)

# flop
possible_flop_hands = all_combinations_in_alpha_order(FLOP_CARDS_CNT)
hand_values_flop = calculate_actual_and_potential_hand_value(possible_flop_hands, hand_values_pre_turn)

# print(len(hand_values_flop), hand_values_flop)
# print(len(hand_values_pre_turn), hand_values_pre_turn)
# print(len(hand_values_turn), hand_values_turn)
# print(len(hand_values_river), hand_values_river)

d = hand_values_flop;
[print(k, d.get(k)) for k in d.keys()];  # [print(i) for i in d.items()]
d = hand_values_turn;
[print(k, d.get(k)) for k in d.keys()];  # [print(i) for i in d.items()]
d = hand_values_river;
[print(k, d.get(k)) for k in d.keys()];  # [print(i) for i in d.items()]

print(probability_of_combination('BN', without='BN'))