from modules.hand import Hand

class BlackjackGame:
    def __init__(self, strategy, shoe, bankroll, standard_bet, verbose=False):
        self.strategy = strategy
        self.shoe = shoe
        self.bankroll = bankroll
        self.standard_bet = standard_bet
        self.verbose = verbose
        
    def place_bet(self, hand, bet_amount):
        """Place a bet on a hand and update bankroll"""
        if bet_amount > self.bankroll:
            bet_amount = self.bankroll  # Bet everything left if not enough
            
        hand.bet = bet_amount
        self.bankroll -= bet_amount
        
        if self.verbose:
            print(f"Placed bet: ${bet_amount:.2f}, Bankroll: ${self.bankroll:.2f}")
            
    def deal_initial_cards(self):
        """Deal the initial cards for a new round"""
        player_hand = Hand()
        dealer_hand = Hand()
        
        # Place the standard bet
        self.place_bet(player_hand, self.standard_bet)
        
        # Deal cards in the traditional order: player, dealer, player, dealer
        player_hand.add_card(self.shoe.draw_card())
        dealer_hand.add_card(self.shoe.draw_card())  # Dealer up card
        player_hand.add_card(self.shoe.draw_card())
        dealer_hand.add_card(self.shoe.draw_card())  # Dealer hole card
        
        if self.verbose:
            print(f"Player's initial hand: {player_hand}")
            print(f"Dealer's up card: {dealer_hand.cards[0]}")
            
        return player_hand, dealer_hand
    
    def execute_player_action(self, action, player_hand, dealer_upcard, player_hands):
        """Execute the player's action based on the strategy"""
        if self.verbose:
            print(f"Player action: {action} on hand {player_hand}")
            
        if action == "H":  # Hit
            player_hand.add_card(self.shoe.draw_card())
            if self.verbose:
                print(f"Hit: New hand: {player_hand}")
            
        elif action == "D":  # Double (or Stand if can't)
            if player_hand.can_double() and self.bankroll >= player_hand.bet:
                # Double the bet
                additional_bet = player_hand.bet
                self.bankroll -= additional_bet
                player_hand.bet += additional_bet
                player_hand.doubled = True
                
                # Take exactly one more card
                player_hand.add_card(self.shoe.draw_card())
                if self.verbose:
                    print(f"Double: New hand: {player_hand}, Bet: ${player_hand.bet:.2f}")
            else:
                # Stand if can't double
                if self.verbose:
                    print("Cannot double, standing instead")
                # No action needed for stand
            
        elif action == "P":  # Split
            if player_hand.can_split() and self.bankroll >= player_hand.bet:
                player_hand.split = True
                
                # Create a new hand with the second card
                new_hand = Hand([player_hand.cards.pop()])
                new_hand.is_split_hand = True
                
                # Mark if splitting aces
                if player_hand.cards[0].value == "A":
                    player_hand.is_split_aces = True
                    new_hand.is_split_aces = True
                
                # Place equal bet on new hand
                self.place_bet(new_hand, player_hand.bet)
                
                # Deal one more card to each hand
                player_hand.add_card(self.shoe.draw_card())
                new_hand.add_card(self.shoe.draw_card())
                
                # Add the new hand to the list of player hands
                player_hands.append(new_hand)
                
                if self.verbose:
                    print(f"Split: First hand: {player_hand}")
                    print(f"Split: Second hand: {new_hand}")
            else:
                # Hit if can't split
                if self.verbose:
                    print("Cannot split, hitting instead")
                player_hand.add_card(self.shoe.draw_card())
                if self.verbose:
                    print(f"Hit: New hand: {player_hand}")
            
        elif action == "X":  # Surrender (or Hit if can't)
            if player_hand.can_surrender():
                player_hand.surrendered = True
                # Return half the bet
                refund = player_hand.bet / 2
                self.bankroll += refund
                if self.verbose:
                    print(f"Surrender: Refund: ${refund:.2f}")
            else:
                # Hit if can't surrender
                if self.verbose:
                    print("Cannot surrender, hitting instead")
                player_hand.add_card(self.shoe.draw_card())
                if self.verbose:
                    print(f"Hit: New hand: {player_hand}")
            
        elif action == "B":  # Double (or Hit if can't)
            if player_hand.can_double() and self.bankroll >= player_hand.bet:
                # Double the bet
                additional_bet = player_hand.bet
                self.bankroll -= additional_bet
                player_hand.bet += additional_bet
                player_hand.doubled = True
                
                # Take exactly one more card
                player_hand.add_card(self.shoe.draw_card())
                if self.verbose:
                    print(f"Double: New hand: {player_hand}, Bet: ${player_hand.bet:.2f}")
            else:
                # Hit if can't double
                if self.verbose:
                    print("Cannot double, hitting instead")
                player_hand.add_card(self.shoe.draw_card())
                if self.verbose:
                    print(f"Hit: New hand: {player_hand}")
            
        elif action == "U":  # Surrender (or Stand if can't)
            if player_hand.can_surrender():
                player_hand.surrendered = True
                # Return half the bet
                refund = player_hand.bet / 2
                self.bankroll += refund
                if self.verbose:
                    print(f"Surrender: Refund: ${refund:.2f}")
            else:
                # Stand if can't surrender
                if self.verbose:
                    print("Cannot surrender, standing instead")
                # No action needed for stand
        
        # For Stand (S), no action is needed
        
        return player_hand
    
    def play_player_hand(self, player_hand, dealer_upcard):
        """Play a single player hand according to the strategy"""
        player_hands = [player_hand]
        current_hand_index = 0
        
        while current_hand_index < len(player_hands):
            current_hand = player_hands[current_hand_index]
            
            # For split aces, deal only one card per hand and move on
            if current_hand.is_split_aces:
                if self.verbose:
                    print(f"Split aces - only one card allowed: {current_hand}")
                current_hand_index += 1
                continue
            
            # Keep making decisions until the hand is complete
            while not (current_hand.is_busted() or current_hand.doubled or current_hand.surrendered):
                # Get the action from the strategy
                action = self.strategy.get_action(current_hand, dealer_upcard)
                
                # Execute the action
                current_hand = self.execute_player_action(action, current_hand, dealer_upcard, player_hands)
                
                # Stop if busted, doubled, or done standing
                if current_hand.is_busted() or current_hand.doubled or action in ["S", "D", "U"] or (action == "X" and not current_hand.surrendered):
                    break
            
            current_hand_index += 1
            
        return player_hands
    
    def play_dealer_hand(self, dealer_hand):
        """Play the dealer's hand according to the rules"""
        if self.verbose:
            print(f"Dealer's initial hand: {dealer_hand}")
            
        # Keep hitting until the dealer has at least a hard 17 or busts
        while True:
            dealer_value = dealer_hand.get_value()
            dealer_is_soft = dealer_hand.is_soft()
            
            # Dealer must hit on soft 17
            if dealer_value >= 18 or (dealer_value == 17 and not dealer_is_soft):
                break
                
            dealer_hand.add_card(self.shoe.draw_card())
            if self.verbose:
                print(f"Dealer hits: {dealer_hand}")
                
        return dealer_hand
    
    def evaluate_hand(self, player_hand, dealer_hand):
        """Evaluate the outcome of a hand and adjust the bankroll"""
        if player_hand.surrendered:
            # Already handled the bankroll adjustment during surrender
            outcome = "SURRENDER"
            payout = -player_hand.bet / 2
        elif player_hand.is_busted():
            outcome = "BUST"
            payout = -player_hand.bet
        elif dealer_hand.is_busted():
            outcome = "WIN (dealer bust)"
            payout = player_hand.bet
            self.bankroll += player_hand.bet * 2  # Original bet + winnings
        elif player_hand.is_blackjack() and not dealer_hand.is_blackjack():
            outcome = "BLACKJACK"
            payout = player_hand.bet * 1.5
            self.bankroll += player_hand.bet + (player_hand.bet * 1.5)  # Original bet + BJ payout
        elif dealer_hand.is_blackjack() and not player_hand.is_blackjack():
            outcome = "LOSE (dealer blackjack)"
            payout = -player_hand.bet
        elif player_hand.get_value() > dealer_hand.get_value():
            outcome = "WIN"
            payout = player_hand.bet
            self.bankroll += player_hand.bet * 2  # Original bet + winnings
        elif player_hand.get_value() < dealer_hand.get_value():
            outcome = "LOSE"
            payout = -player_hand.bet
        else:
            outcome = "PUSH"
            payout = 0
            self.bankroll += player_hand.bet  # Return the original bet
            
        if self.verbose:
            print(f"Outcome: {outcome}, Payout: ${payout:.2f}, New bankroll: ${self.bankroll:.2f}")
            
        return outcome, payout
    
    def play_round(self):
        """Play a complete round of blackjack"""
        initial_bankroll = self.bankroll
        
        # Check if we need to reshuffle
        if self.shoe.should_reshuffle():
            if self.verbose:
                print("Reshuffling the shoe")
            self.shoe.initialize()
            
        # Deal initial cards
        player_hand, dealer_hand = self.deal_initial_cards()
        
        # Check for dealer blackjack
        dealer_has_blackjack = dealer_hand.is_blackjack()
        if dealer_has_blackjack and self.verbose:
            print(f"Dealer has blackjack: {dealer_hand}")
            
        # Play the player's hand(s)
        player_hands = self.play_player_hand(player_hand, dealer_hand.cards[0])
        
        # Play the dealer's hand if needed
        active_player_hands = [h for h in player_hands if not h.is_busted() and not h.surrendered]
        if active_player_hands and not dealer_has_blackjack:
            dealer_hand = self.play_dealer_hand(dealer_hand)
        elif self.verbose:
            print("Dealer doesn't need to play")
            
        # Evaluate each player hand
        results = []
        for hand in player_hands:
            outcome, payout = self.evaluate_hand(hand, dealer_hand)
            results.append({
                "player_hand": str(hand),
                "dealer_hand": str(dealer_hand),
                "bet": hand.bet,
                "outcome": outcome,
                "payout": payout
            })
            
        # Calculate the net change in bankroll
        bankroll_change = self.bankroll - initial_bankroll
        
        if self.verbose:
            print(f"Round complete. Bankroll change: ${bankroll_change:.2f}, New bankroll: ${self.bankroll:.2f}")
            
        return {
            "initial_bankroll": initial_bankroll,
            "final_bankroll": self.bankroll,
            "change": bankroll_change,
            "results": results
        }
