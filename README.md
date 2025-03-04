# Blackjack Simulator

This program simulates multiple sessions of blackjack play according to specific rules and a predefined strategy. It tracks the player's bankroll over time and provides data and visualizations for analysis.

## Features

- Simulates any number of blackjack sessions with configurable parameters
- Implements specific blackjack rules as described in the requirements
- Uses a basic strategy table to determine player actions
- Tracks bankroll progression throughout each session
- Generates both static and interactive visualizations
- Supports debug mode with predefined card scenarios for testing
- Sessions end when bankroll is <= 0 or >= 2x starting stake
- Output files are timestamped for easy organization

## Requirements

- Python 3.7+
- pandas
- matplotlib
- numpy
- plotly (optional, for interactive HTML plots)

## Installation

1. Clone the repository or download the source code
2. Install the required packages:

```bash
pip install pandas matplotlib numpy
```

3. For interactive HTML plots, install plotly:

```bash
pip install plotly
```

4. Ensure the provided strategy file is in the `data` directory

## Project Structure

```
blackjack_sim/
├── README.md
├── blackjack_sim.py         # Main entry point
├── modules/
│   ├── card.py              # Card and Deck classes
│   ├── hand.py              # Hand management
│   ├── strategy.py          # Strategy parser
│   ├── game.py              # Core game logic
│   ├── simulator.py         # Simulation engine
│   └── plotting.py          # Results visualization
├── data/
│   └── basic-strategy.csv   # Default strategy file
└── output/                  # Results and plots directory
```

## Usage

Run the simulator with default settings:

```bash
python blackjack_sim.py
```

### Command Line Options

- `--num_sessions`: Number of sessions to simulate (default: 1)
- `--num_hands`: Number of hands per session (default: 100)
- `--starting_stake`: Initial bankroll amount (default: 1000)
- `--standard_bet`: Standard bet amount (default: 10)
- `--verbose`: Enable detailed hand-by-hand logging
- `--debug`: Enable debug mode with hand verification
- `--strategy_file`: Path to strategy CSV file (default: data/basic-strategy.csv)
- `--scenario`: Test scenario to run in debug mode (default: split_8s)

### Examples

Run 10 sessions of 500 hands each with a $2000 starting bankroll:

```bash
python blackjack_sim.py --num_sessions 10 --num_hands 500 --starting_stake 2000
```

Run in debug mode to test splitting 8s:

```bash
python blackjack_sim.py --debug --scenario split_8s
```

Run with verbose logging:

```bash
python blackjack_sim.py --verbose
```

## Output

The simulator produces three main outputs with timestamped filenames (format: YYYYMMDD_HHMM_filename):

1. **CSV Data File**: Contains the bankroll value after each hand for each session
2. **Static Plot**: A PNG line graph showing bankroll progression over time for each session
3. **Interactive HTML Plot**: An interactive visualization that allows exploring the results in detail

These files are saved in the `output` directory.

### Interpreting Results

#### Static Plot
The static plot shows the bankroll value (y-axis) after each hand (x-axis) for each session. The starting stake and double stake values are indicated by horizontal lines.

#### Interactive HTML Plot
The interactive HTML plot provides additional functionality:
- Toggle visibility of individual sessions by clicking on the legend
- Hover over lines to see exact values
- Filter sessions by outcome (doubled stake, positive, negative, zero)
- Reset view to default zoom level
- Pan and zoom for detailed exploration

#### Summary Statistics
The terminal output includes comprehensive statistics:
- Average/median/max/min final bankroll
- Percentage of sessions ending with a profit
- Detailed outcome distribution:
  - Sessions ending with doubled starting stake
  - Sessions ending positive but not doubled
  - Sessions ending negative but not zero
  - Sessions ending with zero bankroll

## Session Termination Conditions

A session will end when any of these conditions are met:
1. The specified number of hands has been played
2. The bankroll drops to zero or below (bust)
3. The bankroll reaches or exceeds twice the starting stake (success)

## Game Rules

The simulator implements specific blackjack rules as described in the requirements:

- Uses 6 decks of cards (312 cards)
- Dealer hits on soft 17
- Blackjack pays 3:2
- Double down allowed on first two cards
- Splitting allowed, including re-splitting
- Double after split allowed
- Surrender allowed on initial two cards
- No insurance
- Reshuffling when fewer than 10% of cards remain

## Strategy

Player decisions are strictly based on the provided basic strategy table. The strategy is loaded from a CSV file where:
- Rows represent player hand values
- Columns represent dealer up card values
- Cell values indicate the action to take (H, S, D, P, X, B, U)

## Debug Mode

Debug mode allows testing specific scenarios to verify the game logic. Available test scenarios:

- `split_8s`: Tests pair splitting
- `soft_17`: Tests dealer soft 17 behavior
- `double_after_split`: Tests doubling after split
- `soft19v6`: Tests soft total strategy
- `split_aces`: Tests ace splitting rules

## Performance

The simulator is designed to handle large-scale simulations efficiently. It can run 100 sessions of 500 hands each in under 5 minutes on a standard personal computer with 12GB RAM.
