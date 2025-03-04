class Hand:
    def __init__(self, cards=None):
        self.cards = cards or []
        self.bet = 0
        self.doubled = False
        self.split = False
        self.surrendered = False
        self.is_split_hand = False
        self.is_split_aces = False
        
    def add_card(self, card):
        """Add a card to the hand"""
        self.cards.append(card)
        
    def is_blackjack(self):
        """Check if the hand is a blackjack (exactly 2 cards with value of 21)"""
        return len(self.cards) == 2 and self.get_value() == 21
        
    def get_value(self):
        """Calculate the value of the hand, handling aces optimally"""
        total = 0
        aces = 0
        
        for card in self.cards:
            value = card.get_numerical_value()
            if value == 11:
                aces += 1
                value = 1
            total += value
        
        # Add back 10 for each ace if it wouldn't bust
        while aces > 0 and total + 10 <= 21:
            total += 10
            aces -= 1
            
        return total
    
    def is_soft(self):
        """Check if the hand is soft (contains an Ace counted as 11)"""
        value_without_aces = sum(
            card.get_numerical_value() if card.value != "A" else 1 
            for card in self.cards
        )
        
        aces = sum(1 for card in self.cards if card.value == "A")
        
        return aces > 0 and value_without_aces + 10 <= 21
        
    def is_pair(self):
        """Check if the hand is a pair (two cards with the same value)"""
        if len(self.cards) != 2:
            return False
        
        # For face cards and 10s
        if self.cards[0].value in ["T", "J", "Q", "K"] and self.cards[1].value in ["T", "J", "Q", "K"]:
            return True
        
        return self.cards[0].value == self.cards[1].value
        
    def can_split(self):
        """Check if the hand can be split"""
        return self.is_pair() and not self.doubled and not self.surrendered
        
    def can_double(self):
        """Check if the hand can be doubled"""
        return len(self.cards) == 2 and not self.doubled and not self.surrendered
        
    def can_surrender(self):
        """Check if the hand can surrender"""
        return len(self.cards) == 2 and not self.doubled and not self.split and not self.surrendered
    
    def is_busted(self):
        """Check if the hand is busted (value > 21)"""
        return self.get_value() > 21
    
    def __str__(self):
        cards_str = " ".join(str(card) for card in self.cards)
        return f"[{cards_str}] = {self.get_value()}"
