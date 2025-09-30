import tkinter as tk
from tkinter import messagebox, simpledialog
import pickle
from game_engine import Shoe, Card, Hand # Make sure you have the upgraded game_engine.py

class BlackjackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack AI Assistant v2.0")
        
        try:
            with open("q_table.pkl", "rb") as f:
                self.q_table = pickle.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "q_table.pkl not found. Please run train_ai_v2.py first.")
            self.root.destroy()
            return

        self.shoe = Shoe(num_decks=6)
        self.num_players = 7
        self.hero_player_id = 3 # Player 4 is our "Hero"

        self._setup_ui()
        self.new_round()

    def add_extra_card(self, player_index):
        """Asks for an extra card for a player and updates the count."""
        card_str = simpledialog.askstring("Add Card", f"Enter extra card for Player {player_index + 1}:")
        if card_str:
            card_str = card_str.upper()
            # This is a simplified update. We just need to update the count.
            # We don't need a full Card object.
            self.shoe.counter.update(card_str)
            decks_remaining = len(self.shoe.cards) / 52
            self.shoe.counter.calculate_true_count(decks_remaining)
            self.update_counts()
            print(f"Added card '{card_str}' for Player {player_index + 1}. Count updated.")

    def count_dealer_final_hand(self):
        """Processes the dealer's hole card and any hits to finalize the round's count."""
        final_cards_str = self.dealer_final_cards_entry.get().upper()
        if not final_cards_str:
            messagebox.showinfo("Info", "No final dealer cards entered to count.")
            return

        for card_char in final_cards_str:
            # Update the count for each card the dealer revealed at the end
            self.shoe.counter.update(card_char)
        
        # Recalculate the true count with the updated running count
        decks_remaining = len(self.shoe.cards) / 52
        self.shoe.counter.calculate_true_count(decks_remaining)
        self.update_counts()

        self.dealer_final_cards_entry.delete(0, tk.END) # Clear the box after counting
        messagebox.showinfo("Count Updated", f"Count updated with dealer's final cards: {final_cards_str}")


    def _setup_ui(self):
        # UI Frames
        top_frame = tk.Frame(self.root, pady=5)
        top_frame.pack()
        middle_frame = tk.Frame(self.root, pady=5, padx=10)
        middle_frame.pack()
        bottom_frame = tk.Frame(self.root, pady=10)
        bottom_frame.pack()

        # Top Frame: Info and Controls
        self.running_count_label = tk.Label(top_frame, text="Running Count: 0", font=("Arial", 12))
        self.running_count_label.grid(row=0, column=0, padx=10)
        self.true_count_label = tk.Label(top_frame, text="True Count: 0.00", font=("Arial", 12))
        self.true_count_label.grid(row=0, column=1, padx=10)
        tk.Button(top_frame, text="New Round / Reshuffle", command=self.new_round).grid(row=0, column=3, padx=10)
        tk.Button(top_frame, text="Clear Hand Inputs", command=self.clear_inputs).grid(row=2, column=3, padx=10)

        # Middle Frame: Dealer and Players
        self.dealer_card_entry = tk.Entry(middle_frame, width=10)
        tk.Label(middle_frame, text="Dealer's Upcard:").grid(row=0, column=0, sticky='e')
        self.dealer_card_entry.grid(row=0, column=1, pady=5, sticky='w')

        # NEW: Add fields for dealer's final cards
        tk.Label(middle_frame, text="Dealer's Other Cards (Hole/Hits):").grid(row=0, column=2, sticky='e', padx=5)
        self.dealer_final_cards_entry = tk.Entry(middle_frame, width=10)
        self.dealer_final_cards_entry.grid(row=0, column=3, sticky='w')

        tk.Button(middle_frame, text="Count Final Dealer Hand", command=self.count_dealer_final_hand).grid(row=0, column=4, padx=10)

        self.player_entries = []
        for i in range(self.num_players):
            label_text = f"Player {i+1}"
            if i == self.hero_player_id:
                label_text += " (HERO)"
            tk.Label(middle_frame, text=label_text).grid(row=i+1, column=0, sticky='e')
            
            p1_entry = tk.Entry(middle_frame, width=5)
            p1_entry.grid(row=i+1, column=1, padx=2)
            p2_entry = tk.Entry(middle_frame, width=5)
            p2_entry.grid(row=i+1, column=2, padx=2)
            
            # NEW: Add a "+" button for extra cards
            hit_button = tk.Button(middle_frame, text="+", command=lambda p=i: self.add_extra_card(p))
            hit_button.grid(row=i+1, column=3, padx=2)
            
            self.player_entries.append((p1_entry, p2_entry))

        # Bottom Frame: AI Recommendation
        tk.Button(bottom_frame, text="GET HERO RECOMMENDATION", font=("Arial", 14, "bold"), bg="lightblue", command=self.get_recommendation).pack()
        self.recommendation_label = tk.Label(bottom_frame, text="...", font=("Arial", 16, "bold"), fg="darkgreen")
        self.recommendation_label.pack(pady=10)

    def clear_inputs(self):
        """Clears the entry fields for the next hand without resetting the count."""
        self.recommendation_label.config(text="...")
        self.dealer_card_entry.delete(0, tk.END)
        for p1, p2 in self.player_entries:
            p1.delete(0, tk.END)
            p2.delete(0, tk.END)
        print("Inputs cleared for the next hand.")

    def new_round(self):
        self.shoe.build() # Resets deck and counts
        self.update_counts()
        self.recommendation_label.config(text="...")
        self.dealer_card_entry.delete(0, tk.END)
        for p1, p2 in self.player_entries:
            p1.delete(0, tk.END)
            p2.delete(0, tk.END)

    def update_counts(self):
        self.running_count_label.config(text=f"Running Count: {self.shoe.counter.running_count}")
        self.true_count_label.config(text=f"True Count: {self.shoe.counter.true_count:.2f}")
    
    def process_all_cards(self):
        """Simulate dealing all visible cards to update the count accurately."""
        self.shoe.build() # Start with a fresh shoe for calculation
        all_cards = []

        # Get dealer card
        d_card_str = self.dealer_card_entry.get().upper()
        if d_card_str: all_cards.append(d_card_str)

        # Get all player cards
        for p1, p2 in self.player_entries:
            p1_str, p2_str = p1.get().upper(), p2.get().upper()
            if p1_str: all_cards.append(p1_str)
            if p2_str: all_cards.append(p2_str)
        
        # 'Deal' these cards from our dummy shoe to update the count
        for card_str in all_cards:
            # We don't care about the actual card, just its rank for counting
            rank = card_str if card_str in ['A', 'K', 'Q', 'J', 'T'] or card_str.isdigit() else '0'
            self.shoe.counter.update(rank)
        
        decks_remaining = len(self.shoe.cards) / 52
        self.shoe.counter.calculate_true_count(decks_remaining)
        self.update_counts()

    def get_recommendation(self):
        try:
            self.process_all_cards()

            # Get Hero's hand
            hero_p1_str = self.player_entries[self.hero_player_id][0].get().upper()
            hero_p2_str = self.player_entries[self.hero_player_id][1].get().upper()
            dealer_str = self.dealer_card_entry.get().upper()

            if not all([hero_p1_str, hero_p2_str, dealer_str]):
                messagebox.showerror("Input Error", "Please enter both of Hero's cards and the Dealer's card.")
                return

            hero_hand = Hand()
            hero_hand.add_card(Card('H', hero_p1_str))
            hero_hand.add_card(Card('D', hero_p2_str))

            dealer_card_val = Card('S', dealer_str).value

            # Get state for the Q-table
            is_initial_hand = True # For this button, assume it's the first decision
            state = self.get_q_state(hero_hand, dealer_card_val, self.shoe, is_initial_hand)
            
            # Find best valid action from Q-table
            valid_actions_idx = self.get_valid_q_actions(hero_hand, is_initial_hand)
            q_values = self.q_table[state]
            valid_q_values = {a: q_values[a] for a in valid_actions_idx}
            best_action_idx = max(valid_q_values, key=valid_q_values.get)

            action_map = {0: "STAND", 1: "HIT", 2: "DOUBLE", 3: "SPLIT"}
            recommendation = action_map.get(best_action_idx, "Error")

            self.recommendation_label.config(text=f"Recommendation: {recommendation}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def get_q_state(self, hand, dealer_val, shoe, is_initial):
        """Helper to get state tuple in the correct format for the Q-table."""
        true_count_idx = int(max(-10, min(10, shoe.counter.true_count)) + 10)
        usable_ace = 1 if hand.aces > 0 else 0
        can_split_flag = 1 if is_initial and hand.can_split else 0
        return (hand.value, dealer_val, usable_ace, true_count_idx, can_split_flag)

    def get_valid_q_actions(self, hand, is_initial):
        """Helper to get valid action indices."""
        valid = [0, 1] # Stand, Hit
        if is_initial:
            valid.append(2) # Double
            if hand.can_split:
                valid.append(3) # Split
        return valid

if __name__ == "__main__":
    root = tk.Tk()
    app = BlackjackApp(root)
    root.mainloop()