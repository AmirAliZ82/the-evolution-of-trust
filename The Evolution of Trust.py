import tkinter as tk
from tkinter import simpledialog, scrolledtext, filedialog, messagebox, Toplevel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Player class and its subclasses
class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.history = []

    def choose_action(self, opponent_history):
        raise NotImplementedError

    def update_score(self, round_score):
        self.score += round_score

    def record_action(self, action):
        self.history.append(action)

class Copycat(Player):
    def choose_action(self, opponent_history):
        if not opponent_history:
            return 'cop'
        return opponent_history[-1]

class AllCheat(Player):
    def choose_action(self, opponent_history):
        return 'cht'

class AllCooperate(Player):
    def choose_action(self, opponent_history):
        return 'cop'

class Grudger(Player):
    def choose_action(self, opponent_history):
        if 'cht' in opponent_history:
            return 'cht'
        return 'cop'

class Detective(Player):
    def __init__(self, name):
        super().__init__(name)
        self.mode = 'initial'

    def choose_action(self, opponent_history):
        initial_moves = ['cop', 'cht', 'cop', 'cop']
        if len(self.history) < len(initial_moves):
            return initial_moves[len(self.history)]
        elif self.mode == 'initial':
            if 'cht' in opponent_history[-4:]:
                self.mode = 'copycat'
            else:
                self.mode = 'cheat'
        if self.mode == 'copycat':
            return opponent_history[-1]
        return 'cht'

def get_custom_payoff(payoff_cc1_var, payoff_cc2_var, payoff_cd1_var, payoff_cd2_var, payoff_dc1_var, payoff_dc2_var, payoff_dd1_var, payoff_dd2_var):
    try:
        payoff_cc1 = int(payoff_cc1_var.get())
        payoff_cc2 = int(payoff_cc2_var.get())
        payoff_cd1 = int(payoff_cd1_var.get())
        payoff_cd2 = int(payoff_cd2_var.get())
        payoff_dc1 = int(payoff_dc1_var.get())
        payoff_dc2 = int(payoff_dc2_var.get())
        payoff_dd1 = int(payoff_dd1_var.get())
        payoff_dd2 = int(payoff_dd2_var.get())
        if any(value < -10 or value > 10 for value in [payoff_cc1, payoff_cc2, payoff_cd1, payoff_cd2, payoff_dc1, payoff_dc2, payoff_dd1, payoff_dd2]):
            raise ValueError("Payoff values must be between -10 and 10.")
        return {
            ('cop', 'cop'): (payoff_cc1, payoff_cc2),
            ('cop', 'cht'): (payoff_cd1, payoff_cd2),
            ('cht', 'cop'): (payoff_dc1, payoff_dc2),
            ('cht', 'cht'): (payoff_dd1, payoff_dd2),
        }
    except ValueError as e:
        messagebox.showerror("Invalid Input", str(e))
        return None

def play_round(player1, player2, payoff_matrix):
    action1 = player1.choose_action(player2.history)
    action2 = player2.choose_action(player1.history)
    round_score = payoff_matrix[(action1, action2)]
    player1.update_score(round_score[0])
    player2.update_score(round_score[1])
    player1.record_action(action1)
    player2.record_action(action2)
    return round_score

def simulate_games_with_totals(players, num_rounds, payoff_matrix):
    total_scores = {player.name: 0 for player in players}
    results = ""
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            player1 = players[i]
            player2 = players[j]
            results += f"\nGame: {player1.name} vs {player2.name}\n"
            results += "Round\tAction1\tAction2\tScore1\tScore2\n"
            player1.score = 0
            player2.score = 0
            player1.history = []
            player2.history = []
            for round_number in range(1, num_rounds + 1):
                round_score = play_round(player1, player2, payoff_matrix)
                results += f"{round_number}\t{player1.history[-1]}\t{player2.history[-1]}\t{round_score[0]}\t{round_score[1]}\n"
            total_scores[player1.name] += player1.score
            total_scores[player2.name] += player2.score
    results += "\nTotal Scores after all games:\n"
    ranked_players = sorted(total_scores.keys(), key=lambda x: total_scores[x], reverse=True)
    ranks = {player: f"{i}th" for i, player in enumerate(ranked_players, start=1)}
    for player, score in total_scores.items():
        results += f"{player} {score} {ranks[player]}\n"
    winner = ranked_players[0]
    results += f"\nWinner: {winner} with a score of {total_scores[winner]}"
    return results, total_scores, ranks

def plot_scores(scores, ranks, frame):
    for widget in frame.winfo_children():
        widget.destroy()

    names = list(scores.keys())
    values = list(scores.values())
    fig, ax = plt.subplots()
    ax.bar(names, values)
    ax.set_ylabel('Scores')
    ax.set_title('Total Scores of Players')
    for i, v in enumerate(values):
        ax.text(i, v + 1, f"{ranks[names[i]]}", ha='center', va='bottom')

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def download_results(results):
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(results)

def open_settings_window():
    settings_window = Toplevel(window)
    settings_window.title("Settings")

    # Input for number of rounds
    num_rounds_var = tk.StringVar()
    tk.Label(settings_window, text="Enter Number of Rounds:").pack()
    tk.Entry(settings_window, textvariable=num_rounds_var).pack()

    # Custom payoff inputs
    payoff_frame = tk.Frame(settings_window)
    payoff_frame.pack(side=tk.TOP, padx=10, pady=10)
    tk.Label(payoff_frame, text="Custom Payoffs (Player1, Player2):").pack()
    tk.Label(payoff_frame, text="CC:").pack(side=tk.LEFT)
    payoff_cc1_var = tk.StringVar(value="2")
    tk.Entry(payoff_frame, textvariable=payoff_cc1_var).pack(side=tk.LEFT)
    payoff_cc2_var = tk.StringVar(value="2")
    tk.Entry(payoff_frame, textvariable=payoff_cc2_var).pack(side=tk.LEFT)
    tk.Label(payoff_frame, text="CD:").pack(side=tk.LEFT)
    payoff_cd1_var = tk.StringVar(value="-1")
    tk.Entry(payoff_frame, textvariable=payoff_cd1_var).pack(side=tk.LEFT)
    payoff_cd2_var = tk.StringVar(value="3")
    tk.Entry(payoff_frame, textvariable=payoff_cd2_var).pack(side=tk.LEFT)
    tk.Label(payoff_frame, text="DC:").pack(side=tk.LEFT)
    payoff_dc1_var = tk.StringVar(value="3")
    tk.Entry(payoff_frame, textvariable=payoff_dc1_var).pack(side=tk.LEFT)
    payoff_dc2_var = tk.StringVar(value="-1")
    tk.Entry(payoff_frame, textvariable=payoff_dc2_var).pack(side=tk.LEFT)
    tk.Label(payoff_frame, text="DD:").pack(side=tk.LEFT)
    payoff_dd1_var = tk.StringVar(value="0")
    tk.Entry(payoff_frame, textvariable=payoff_dd1_var).pack(side=tk.LEFT)
    payoff_dd2_var = tk.StringVar(value="0")
    tk.Entry(payoff_frame, textvariable=payoff_dd2_var).pack(side=tk.LEFT)

    def start_simulation():
        num_rounds = int(num_rounds_var.get())
        custom_payoff = get_custom_payoff(
            payoff_cc1_var, payoff_cc2_var, payoff_cd1_var, payoff_cd2_var,
            payoff_dc1_var, payoff_dc2_var, payoff_dd1_var, payoff_dd2_var
        )
        if custom_payoff:
            game_results, total_scores, ranks = simulate_games_with_totals(players, num_rounds, custom_payoff)
            open_results_window(game_results, total_scores, ranks)

    start_button = tk.Button(settings_window, text="Start Simulation", command=start_simulation)
    start_button.pack()

def open_results_window(game_results, total_scores, ranks):
    results_window = Toplevel(window)
    results_window.title("Results and Graph")

    # Games frame
    games_frame = tk.Frame(results_window)
    games_frame.pack(side=tk.TOP, padx=10, pady=10)
    text_area = scrolledtext.ScrolledText(games_frame, wrap=tk.WORD, width=80, height=20)
    text_area.pack()
    text_area.insert(tk.INSERT, game_results)

    # Winner frame
    winner_frame = tk.Frame(results_window)
    winner_frame.pack(side=tk.TOP, padx=10, pady=10)
    winner_label = tk.Label(winner_frame, text="Winner:")
    winner_label.pack()
    winner_var = tk.StringVar()
    winner_name_label = tk.Label(winner_frame, textvariable=winner_var, font=("Helvetica", 16))
    winner_name_label.pack()
    winner = max(total_scores, key=total_scores.get)
    winner_var.set(winner)

    # Download button
    download_button = tk.Button(results_window, text="Download Results", command=lambda: download_results(game_results))
    download_button.pack()

    # Plotting area
    plot_frame = tk.Frame(results_window)
    plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    plot_scores(total_scores, ranks, plot_frame)

# Create the main application window
window = tk.Tk()
window.title("Iterated Prisoner's Dilemma")

# Create a list of player instances
players = [
    Copycat("Copycat"),
    AllCheat("All Cheat"),
    AllCooperate("All Cooperate"),
    Grudger("Grudger"),
    Detective("Detective"),
]

# Main menu
menu = tk.Menu(window)
window.config(menu=menu)

# File menu
file_menu = tk.Menu(menu)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Exit", command=window.quit)

# Settings menu
settings_menu = tk.Menu(menu)
menu.add_cascade(label="Settings", menu=settings_menu)
settings_menu.add_command(label="Custom Payoffs", command=open_settings_window)

# Start simulation button
start_button = tk.Button(window, text="Start Simulation", command=lambda: open_settings_window())
start_button.pack(pady=10)

# Run the main loop
window.mainloop()