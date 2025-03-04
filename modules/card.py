from enum import Enum
import random

class Suit(Enum):
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        
    def get_numerical_value(self):
        if self.value in ["J", "Q", "K", "T"]:
            return 10
        elif self.value == "A":
            return 11  # Ace's default value (will be adjusted as needed)
        else:
            return int(self.value)
            
    def __str__(self):
        return f"{self.value}{self.suit.name[0]}"
    
    def __repr__(self):
        return self.__str__()

class Shoe:
    def __init__(self, num_decks=6):
        self.num_decks = num_decks
        self.cards = []
        self.initialize()
        
    def initialize(self):
        """Initialize the shoe with the specified number of decks and shuffle"""
        self.cards = []
        values = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        
        for _ in range(self.num_decks):
            for suit in Suit:
                for value in values:
                    self.cards.append(Card(value, suit))
        
        self.shuffle()
        
    def shuffle(self):
        """Shuffle the cards in the shoe"""
        random.shuffle(self.cards)
        
    def draw_card(self):
        """Draw a card from the top of the shoe"""
        if not self.cards:
            raise ValueError("No cards left in the shoe")
        return self.cards.pop(0)
        
    def should_reshuffle(self):
        """Check if the shoe should be reshuffled (less than 10% cards remain)"""
        return len(self.cards) < (self.num_decks * 52 * 0.1)
    
    def cards_remaining(self):
        """Return the number of cards remaining in the shoe"""
        return len(self.cards)
    
    def insert_cards(self, cards):
        """Insert specific cards at the beginning of the shoe (for testing)"""
        for card in reversed(cards):
            self.cards.insert(0, card)
