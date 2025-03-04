import csv
import pandas as pd
import os

class Strategy:
    def __init__(self, strategy_file):
        """Initialize strategy from the CSV file"""
        try:
            self.strategy_table = self.load_strategy(strategy_file)
            print(f"Successfully loaded strategy from {strategy_file}")
            # Print the first few rows to verify
            print(f"Strategy table shape: {self.strategy_table.shape}")
        except Exception as e:
            print(f"Error loading strategy file: {e}")
            print(f"Looking for file at: {os.path.abspath(strategy_file)}")
            raise
        
    def load_strategy(self, strategy_file):
        """Load the strategy table from a CSV file"""
        if not os.path.exists(strategy_file):
            raise FileNotFoundError(f"Strategy file not found at: {os.path.abspath(strategy_file)}")
            
        try:
            df = pd.read_csv(strategy_file, index_col=0)
            print(f"Successfully loaded strategy from {strategy_file}")
            return df
        except Exception as e:
            raise Exception(f"Error parsing strategy file {strategy_file}: {e}")
    
    def get_action(self, player_hand, dealer_upcard):
        """
        Determine the correct action based on the strategy table
        
        Args:
            player_hand: The player's hand
            dealer_upcard: The dealer's face-up card
            
        Returns:
            str: The action to take (H, S, D, P, X, B, U)
        """
        # Convert face cards to 'T' for the dealer's upcard
        dealer_value = dealer_upcard.value
        if dealer_value in ["J", "Q", "K"]:
            dealer_value = "T"
            
        # Handle pairs
        if player_hand.is_pair():
            card_value = player_hand.cards[0].value
            # For face cards and 10s
            if card_value in ["J", "Q", "K"]:
                card_value = "T"
                
            row_key = f"{card_value}{card_value}"
                
            try:
                return self.strategy_table.loc[row_key, dealer_value]
            except KeyError:
                print(f"KeyError: Pair lookup failed for row_key={row_key}, dealer_value={dealer_value}")
                print(f"Available row keys: {self.strategy_table.index.tolist()}")
                print(f"Available column keys: {self.strategy_table.columns.tolist()}")
                return "S"  # Default to stand if lookup fails
        
        # Handle soft totals (Ace counted as 11)
        elif player_hand.is_soft():
            hand_value = player_hand.get_value()
            
            # For soft 20 (A,9) and soft 21 (A,10), use hard total strategy
            if hand_value >= 20:
                row_key = str(hand_value)
            # For hands like A,2 through A,9
            elif 13 <= hand_value <= 19:
                non_ace_value = hand_value - 11
                row_key = f"A{non_ace_value}"
                
            try:
                return self.strategy_table.loc[row_key, dealer_value]
            except KeyError:
                print(f"KeyError: Soft total lookup failed for row_key={row_key}, dealer_value={dealer_value}")
                print(f"Available row keys: {self.strategy_table.index.tolist()}")
                if hand_value >= 17:
                    return "S"  # Stand on soft 17+
                else:
                    return "H"  # Hit on soft 16-
        
        # Handle hard totals
        else:
            hand_value = player_hand.get_value()
            row_key = str(hand_value)
            
            # Use appropriate row based on hand value
            if hand_value <= 8:
                row_key = "8"
            elif hand_value >= 21:
                row_key = "21"
                
            try:
                return self.strategy_table.loc[row_key, dealer_value]
            except KeyError:
                print(f"KeyError: Hard total lookup failed for row_key={row_key}, dealer_value={dealer_value}")
                if hand_value >= 17:
                    return "S"  # Stand on 17+
                else:
                    return "H"  # Hit on 16-
