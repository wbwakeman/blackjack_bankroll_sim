# Set matplotlib backend to non-interactive - must be done before any other matplotlib imports
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend which doesn't require a GUI

import argparse
import os
import json
import pandas as pd
from modules.card import Card, Suit, Shoe
from modules.strategy import Strategy
from modules.game import BlackjackGame
from modules.simulator import BlackjackSimulator
from modules.plotting import plot_results

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Blackjack Simulator')
    parser.add_argument('--num_sessions', type=int, default=1,
                        help='Number of sessions to simulate (default: 1)')
    parser.add_argument('--num_hands', type=int, default=100,
                        help='Number of hands per session (default: 100)')
    parser.add_argument('--starting_stake', type=float, default=1000,
                        help='Initial bankroll amount (default: 1000)')
    parser.add_argument('--standard_bet', type=float, default=10,
                        help='Standard bet amount (default: 10)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable detailed hand-by-hand logging')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode with hand verification')
    parser.add_argument('--strategy_file', type=str, default='data/basic-strategy.csv',
                        help='Path to strategy CSV file (default: data/basic-strategy.csv)')
    parser.add_argument('--scenario', type=str, default='split_8s',
                        help='Test scenario to run in debug mode (default: split_8s)')
    return parser.parse_args()

def create_output_directory():
    """Create output directory if it doesn't exist"""
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def main():
    """Main function to run the blackjack simulator"""
    # Parse command line arguments
    args = parse_args()
    
    # Create output directory
    output_dir = create_output_directory()
    
    # Initialize simulator
    simulator = BlackjackSimulator(args)
    
    if args.debug:
        # Run in debug mode with the specified test scenario
        simulator.run_debug_session(args.scenario)
    else:
        # Run the simulation
        print(f"Starting simulation with {args.num_sessions} sessions of {args.num_hands} hands each")
        print(f"Starting stake: ${args.starting_stake:.2f}, Standard bet: ${args.standard_bet:.2f}")
        
        results_df = simulator.run_simulation()
        
        # Save results to file
        results_file = simulator.save_results(results_df, output_dir)
        print(f"Simulation results saved to {results_file}")
        
        # Plot results
        static_plot_file, html_plot_file = plot_results(results_df, args.starting_stake, args.num_hands, output_dir)
        
        # Display summary statistics
        print("\nSummary Statistics:")
        final_bankrolls = results_df.groupby('session')['bankroll'].last()
        
        print(f"Average final bankroll: ${final_bankrolls.mean():.2f}")
        print(f"Median final bankroll: ${final_bankrolls.median():.2f}")
        print(f"Maximum final bankroll: ${final_bankrolls.max():.2f}")
        print(f"Minimum final bankroll: ${final_bankrolls.min():.2f}")
        
        # Calculate win/loss percentage
        win_percentage = (final_bankrolls > args.starting_stake).mean() * 100
        print(f"Sessions ending with profit: {win_percentage:.1f}%")
        
        # Calculate the additional outcome statistics
        total_sessions = len(final_bankrolls)
        doubled_count = sum(final_bankrolls >= 2 * args.starting_stake)
        positive_count = sum((final_bankrolls < 2 * args.starting_stake) & (final_bankrolls > 0))
        negative_count = sum(final_bankrolls < 0)
        zero_count = sum(final_bankrolls == 0)
        
        print("\nSession Outcome Distribution:")
        print(f"Doubled starting stake: {doubled_count} ({doubled_count/total_sessions*100:.1f}%)")
        print(f"Positive but not doubled: {positive_count} ({positive_count/total_sessions*100:.1f}%)")
        print(f"Negative but not zero: {negative_count} ({negative_count/total_sessions*100:.1f}%)")
        print(f"Zero bankroll: {zero_count} ({zero_count/total_sessions*100:.1f}%)")

if __name__ == "__main__":
    main()
