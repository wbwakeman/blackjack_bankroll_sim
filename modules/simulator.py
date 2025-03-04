import json
import os
import pandas as pd
from modules.card import Card, Suit, Shoe
from modules.strategy import Strategy
from modules.game import BlackjackGame

class BlackjackSimulator:
    def __init__(self, args):
        """Initialize the simulator with the provided arguments"""
        self.num_sessions = args.num_sessions
        self.num_hands = args.num_hands
        self.starting_stake = args.starting_stake
        self.standard_bet = args.standard_bet
        self.verbose = args.verbose
        self.debug = args.debug
        self.strategy_file = args.strategy_file
        self.strategy = Strategy(self.strategy_file)
        
        # Load test scenarios if in debug mode
        if self.debug:
            self.test_scenarios = self.load_test_scenarios()
        
    def load_test_scenarios(self):
        """Load test scenarios from the JSON file"""
        # Parse the scenarios from the provided JSON structure
        scenarios = {}
        
        # This is just a placeholder - we'll need to properly parse the JSON
        with open('test-scenarios.json', 'r') as f:
            scenarios_text = f.read()
            # Extract the dictionary part
            scenarios_dict = scenarios_text.split('=')[1].strip()
            # This is unsafe but just for illustration
            scenarios = eval(scenarios_dict)
            
        return scenarios
    
    def run_simulation(self):
        """Run the specified number of simulation sessions"""
        results = []
        
        for session in range(1, self.num_sessions + 1):
            if self.verbose:
                print(f"\n=== Starting Session {session} ===\n")
                
            # Initialize for this session
            shoe = Shoe(6)
            game = BlackjackGame(
                self.strategy, 
                shoe, 
                self.starting_stake, 
                self.standard_bet, 
                self.verbose
            )
            
            session_results = []
            
            # Record initial bankroll
            session_results.append({
                "hand": 0,
                "bankroll": game.bankroll,
                "session": session
            })
            
            # Play the specified number of hands
            for hand_num in range(1, self.num_hands + 1):
                if self.verbose:
                    print(f"\n--- Hand {hand_num} ---\n")
                    
                # Play a round
                round_result = game.play_round()
                
                # Record the result
                session_results.append({
                    "hand": hand_num,
                    "bankroll": game.bankroll,
                    "session": session
                })
                
                # Check if bankroll is depleted or doubled
                if game.bankroll <= 0:
                    if self.verbose:
                        print("Bankroll depleted. Ending session.")
                    break
                elif game.bankroll >= 2 * self.starting_stake:
                    if self.verbose:
                        print("Bankroll doubled! Ending session.")
                    break
            
            results.extend(session_results)
            
            if self.verbose:
                print(f"\n=== Session {session} Complete ===")
                print(f"Final bankroll: ${game.bankroll:.2f}")
                
        # Convert results to DataFrame
        results_df = pd.DataFrame(results)
        
        return results_df
    
    def run_debug_session(self, scenario_name):
        """Run a specific test scenario for debugging"""
        if scenario_name not in self.test_scenarios:
            print(f"Error: Scenario '{scenario_name}' not found")
            return
            
        print(f"Running debug scenario: {scenario_name}")
        
        # Initialize game components
        shoe = Shoe(1)  # Use a single deck for testing
        
        # Clear the shoe and insert the test cards
        shoe.cards = []
        shoe.insert_cards(self.test_scenarios[scenario_name])
        
        # Set up the game
        game = BlackjackGame(
            self.strategy,
            shoe,
            self.starting_stake,
            self.standard_bet,
            verbose=True  # Always verbose in debug mode
        )
        
        # Play a single round and show detailed results
        print("\n=== Starting Debug Round ===\n")
        round_result = game.play_round()
        print("\n=== Debug Round Complete ===\n")
        
        # Display the results
        print(json.dumps(round_result, indent=4))
        
    def save_results(self, results_df, output_dir="output"):
        """Save simulation results to files"""
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        
        # Save raw data to CSV
        output_file = os.path.join(output_dir, f"{timestamp}_simulation_results.csv")
        results_df.to_csv(output_file, index=False)
        
        print(f"Results saved to {output_file}")
        
        return output_file
