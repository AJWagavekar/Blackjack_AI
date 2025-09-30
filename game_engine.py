# In game_engine.py
# In game_engine.py
import random

class HiLoCounter:
    """Tracks the card count using the Hi-Lo system."""
    def __init__(self):
        self.running_count = 0
        self.true_count = 0

    def update(self, card_rank):
        if card_rank in ['2', '3', '4', '5', '6']:
            self.running_count += 1
        elif card_rank in ['10', 'J', 'Q', 'K', 'A', 'T']:
            self.running_count -= 1
    
    def calculate_true_count(self, decks_remaining):
        if decks_remaining > 0:
            self.true_count = self.running_count / decks_remaining
        else:
            self.true_count = 0

class Shoe:
    """Represents a multi-deck shoe used in casinos."""
    def __init__(self, num_decks=6):
        self.cards = []
        self.num_decks = num_decks
        self.counter = HiLoCounter()
        self.reshuffle_penetration = 0.75 # Reshuffle after 75% of cards are used
        self.build()

    def build(self):
        self.cards = []
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        for _ in range(self.num_decks):
            for suit in suits:
                for rank in ranks:
                    self.cards.append(Card(suit, rank))
        self.shuffle()
        self.counter = HiLoCounter() # Reset counter on reshuffle

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        # Check if we need to reshuffle before dealing
        if len(self.cards) < self.num_decks * 52 * (1 - self.reshuffle_penetration):
            print("--- RESHUFFLING THE SHOE ---")
            self.build()

        card = self.cards.pop()
        self.counter.update(card.rank)
        decks_remaining = len(self.cards) / 52
        self.counter.calculate_true_count(decks_remaining)
        return card

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        # Define card values
        if rank == 'A':
            self.value = 11
        elif rank in ['K', 'Q', 'J']:
            self.value = 10
        else:
            self.value = int(rank)

    def __repr__(self):
        # This method helps in printing the card object for debugging
        return f"{self.rank} of {self.suit}"
    

# In game_engine.py


class Deck:
    def __init__(self):
        self.cards = []
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        
        # Create a full 52-card deck
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))
        
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        # Remove and return the top card from the deck
        if len(self.cards) > 0:
            return self.cards.pop()
        return None # Return None if the deck is empty    
    
# In game_engine.py

class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0  # To keep track of aces

    @property
    def can_split(self):
        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank

    def add_card(self, card):
        self.cards.append(card)
        self.value += card.value
        if card.rank == 'A':
            self.aces += 1
        self.adjust_for_ace()

    def adjust_for_ace(self):
        # If value > 21 and we have an ace, change its value from 11 to 1
        while self.value > 21 and self.aces > 0:
            self.value -= 10
            self.aces -= 1


# --- Test the engine ---
if __name__ == "__main__":
    deck = Deck()
    
    player_hand = Hand()
    player_hand.add_card(deck.deal())
    player_hand.add_card(deck.deal())
    
    print("Player's Hand:")
    for card in player_hand.cards:
        print(card)
    print(f"Player's Hand Value: {player_hand.value}")

    # Example of an Ace being handled correctly
    print("\n--- Ace Test ---")
    ace_hand = Hand()
    ace_hand.add_card(Card('Hearts', 'A'))
    ace_hand.add_card(Card('Clubs', '7'))
    print(f"Hand: Ace, 7 -> Value: {ace_hand.value}") # Should be 18

    ace_hand.add_card(Card('Spades', '5'))
    print(f"Hand: Ace, 7, 5 -> Value: {ace_hand.value}") # Should be 13 (Ace becomes 1)