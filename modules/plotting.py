import matplotlib
# Use a non-interactive backend that doesn't require GUI
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os
import datetime
import json

# Try to import plotly, with a fallback if not available
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Plotly not available. Install with 'pip install plotly' for interactive HTML plots.")

def plot_results(results_df, starting_stake, num_hands, output_dir="output"):
    """Create and save plots of the simulation results"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create timestamp for filenames
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    
    # Create static matplotlib plot
    plt.figure(figsize=(12, 8))
    
    # Plot each session
    for session in results_df['session'].unique():
        session_data = results_df[results_df['session'] == session]
        plt.plot(session_data['hand'], session_data['bankroll'], 
                 label=f"Session {session}")
    
    # Add horizontal lines for starting stake and double starting stake
    plt.axhline(y=starting_stake, color='r', linestyle='--', 
                label="Starting Stake")
    plt.axhline(y=starting_stake * 2, color='g', linestyle='--', 
                label="Double Starting Stake")
    
    # Set plot limits and labels
    plt.xlim(0, num_hands)
    plt.ylim(0, starting_stake * 2.1)
    plt.xlabel("Hand Number")
    plt.ylabel("Bankroll ($)")
    plt.title("Blackjack Simulation: Bankroll vs. Hand Number")
    plt.grid(True)
    plt.legend()
    
    # Save the static plot
    static_output_file = os.path.join(output_dir, f"{timestamp}_bankroll_plot.png")
    plt.savefig(static_output_file, dpi=300)
    plt.close()  # Close the figure to free memory
    
    print(f"Static plot saved to {static_output_file}")
    
    # Create interactive HTML plot if plotly is available
    html_output_file = None
    if PLOTLY_AVAILABLE:
        fig = go.Figure()
        
        # Add data for each session
        session_data_dict = {}
        for session in sorted(results_df['session'].unique()):
            session_data = results_df[results_df['session'] == session]
            # Only show first session by default, others hidden in legend
            visible = True if session == 1 else "legendonly"
            
            # Store session data for javascript interactivity
            session_data_dict[f"Session {session}"] = {
                "x": session_data['hand'].tolist(),
                "y": session_data['bankroll'].tolist(),
                "final_bankroll": session_data['bankroll'].iloc[-1] if len(session_data) > 0 else 0
            }
            
            fig.add_trace(
                go.Scatter(
                    x=session_data['hand'],
                    y=session_data['bankroll'],
                    mode='lines',
                    name=f'Session {session}',
                    visible=visible,
                    hovertemplate=f'Hand: %{{x}}<br>Bankroll: $%{{y:.2f}}<extra>Session {session}</extra>'
                )
            )
        
        # Add horizontal line for starting stake
        fig.add_shape(
            type="line",
            x0=0,
            y0=starting_stake,
            x1=num_hands,
            y1=starting_stake,
            line=dict(
                color="red",
                width=2,
                dash="dash",
            )
        )
        
        # Add horizontal line for double starting stake
        fig.add_shape(
            type="line",
            x0=0,
            y0=starting_stake * 2,
            x1=num_hands,
            y1=starting_stake * 2,
            line=dict(
                color="green",
                width=2,
                dash="dash",
            )
        )
        
        # Add annotations for the horizontal lines
        fig.add_annotation(
            x=num_hands * 0.02,
            y=starting_stake,
            text="Starting Stake",
            showarrow=False,
            yshift=10,
            font=dict(color="red")
        )
        
        fig.add_annotation(
            x=num_hands * 0.02,
            y=starting_stake * 2,
            text="Double Starting Stake",
            showarrow=False,
            yshift=10,
            font=dict(color="green")
        )
        
        # Update layout
        fig.update_layout(
            title='Blackjack Simulation: Bankroll vs. Hand Number',
            xaxis_title='Hand Number',
            yaxis_title='Bankroll ($)',
            legend_title='Session',
            autosize=True,
            height=700,
            hovermode="closest",
            margin=dict(t=100, l=50, r=50, b=50),
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    buttons=[
                        dict(label="Reset View",
                             method="relayout",
                             args=[{"xaxis.range": [0, num_hands],
                                    "yaxis.range": [0, starting_stake * 2.1]}])
                    ],
                    pad={"r": 10, "t": 10},
                    showactive=False,
                    x=0.1,
                    xanchor="left",
                    y=1.1,
                    yanchor="top"
                )
            ]
        )
        
        # Set axis ranges
        fig.update_xaxes(range=[0, num_hands])
        fig.update_yaxes(range=[0, starting_stake * 2.1])
        
        # Add session statistics to the plot
        session_stats = results_df.groupby('session')['bankroll'].last().reset_index()
        session_stats['outcome'] = session_stats['bankroll'].apply(
            lambda x: "Doubled" if x >= 2 * starting_stake else
                      "Positive" if x > 0 else
                      "Zero" if x == 0 else "Negative"
        )
        
        # Add buttons to filter sessions by outcome
        fig.update_layout(
            updatemenus=[
                dict(
                    buttons=[
                        dict(label="Show All",
                             method="update",
                             args=[{"visible": [True] * len(fig.data)},
                                  {"title": "All Sessions"}]),
                        dict(label="Doubled Stake",
                             method="update",
                             args=[{"visible": [session_stats.loc[i-1, 'outcome'] == "Doubled" 
                                               for i in range(1, len(fig.data)+1)]},
                                  {"title": "Sessions with Doubled Stake"}]),
                        dict(label="Positive",
                             method="update",
                             args=[{"visible": [session_stats.loc[i-1, 'outcome'] == "Positive" 
                                               for i in range(1, len(fig.data)+1)]},
                                  {"title": "Sessions with Positive Outcome"}]),
                        dict(label="Negative",
                             method="update",
                             args=[{"visible": [session_stats.loc[i-1, 'outcome'] == "Negative" 
                                               for i in range(1, len(fig.data)+1)]},
                                  {"title": "Sessions with Negative Outcome"}]),
                        dict(label="Zero",
                             method="update",
                             args=[{"visible": [session_stats.loc[i-1, 'outcome'] == "Zero" 
                                               for i in range(1, len(fig.data)+1)]},
                                  {"title": "Sessions with Zero Bankroll"}]),
                    ],
                    direction="down",
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=1.02,
                    yanchor="top"
                ),
                dict(
                    type="buttons",
                    direction="right",
                    buttons=[
                        dict(label="Reset View",
                             method="relayout",
                             args=[{"xaxis.range": [0, num_hands],
                                    "yaxis.range": [0, starting_stake * 2.1]}])
                    ],
                    pad={"r": 10, "t": 10},
                    showactive=False,
                    x=0.37,
                    xanchor="left",
                    y=1.02,
                    yanchor="top"
                )
            ]
        )
        
        # Save as interactive HTML
        html_output_file = os.path.join(output_dir, f"{timestamp}_bankroll_interactive.html")
        fig.write_html(
            html_output_file,
            include_plotlyjs='cdn',
            config={'displayModeBar': True}
        )
        
        print(f"Interactive plot saved to {html_output_file}")
    
    return static_output_file, html_output_file
