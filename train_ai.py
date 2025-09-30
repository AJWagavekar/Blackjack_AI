import numpy as np
from game_engine import Shoe, Hand, Card
import pickle

print("Starting Advanced AI Training...")

# HYPERPARAMETERS
LEARNING_RATE = 0.1  # Alpha (α)
DISCOUNT = 0.95      # Gamma (γ)
EPISODES = 5_000_000 # More episodes are needed for the complex state
EPSILON_START = 1.0  # Start with high exploration
EPSILON_END = 0.01   # End with low exploration
EPSILON_DECAY = 0.999995 # Decay rate

# ACTIONS
ACTION_STAND = 0
ACTION_HIT = 1
ACTION_DOUBLE = 2
ACTION_SPLIT = 3
actions = [ACTION_STAND, ACTION_HIT, ACTION_DOUBLE, ACTION_SPLIT]

# Q-TABLE SETUP
# State: (player_total, dealer_upcard, has_usable_ace, true_count_idx, can_split_flag)
# Dimensions: 32 for total, 12 for dealer card, 2 for ace, 21 for true count, 2 for split, 4 for actions
q_table = np.zeros((32, 12, 2, 21, 2, len(actions)))

def get_state(player_hand, dealer_upcard_val, shoe, is_initial_hand):
    """Gets the state tuple for the Q-table."""
    # Normalize true count to an index from 0-20
    true_count_idx = int(max(-10, min(10, shoe.counter.true_count)) + 10)
    usable_ace = 1 if player_hand.aces > 0 else 0
    can_split_flag = 1 if is_initial_hand and player_hand.can_split else 0
    return (player_hand.value, dealer_upcard_val, usable_ace, true_count_idx, can_split_flag)

def get_valid_actions(player_hand, is_initial_hand):
    """Returns a list of valid actions for the current hand."""
    valid = [ACTION_STAND, ACTION_HIT]
    if is_initial_hand:
        valid.append(ACTION_DOUBLE)
        if player_hand.can_split:
            valid.append(ACTION_SPLIT)
    return valid

def play_hand(player_hand, dealer_hand, shoe, epsilon):
    """Plays a single hand, updates the Q-table, and returns the outcome reward."""
    is_initial_hand = True
    
    # Define state and a default action BEFORE the loop to handle initial blackjacks.
    # This prevents the UnboundLocalError if the loop is skipped.
    state = get_state(player_hand, dealer_hand.cards[0].value, shoe, is_initial_hand)
    action = ACTION_STAND # A blackjack is effectively a "stand".

    # --- Player's Turn ---
    while True:
        if player_hand.value >= 21:
            break # Breaks on blackjack or bust

        # Get current state and valid actions for the decision
        state = get_state(player_hand, dealer_hand.cards[0].value, shoe, is_initial_hand)
        valid_actions = get_valid_actions(player_hand, is_initial_hand)

        # Epsilon-Greedy Strategy: Choose a random valid action or the best known valid action
        if np.random.random() < epsilon:
            action = np.random.choice(valid_actions)
        else:
            q_values = q_table[state]
            valid_q_values = {a: q_values[a] for a in valid_actions}
            action = max(valid_q_values, key=valid_q_values.get)

        # Perform the chosen action
        if action == ACTION_STAND:
            break
        
        elif action == ACTION_HIT:
            player_hand.add_card(shoe.deal())
            is_initial_hand = False
        
        elif action == ACTION_DOUBLE:
            player_hand.add_card(shoe.deal())
            break

        elif action == ACTION_SPLIT:
            # Simplified split logic for training: play out one of the new hands
            player_hand.cards.pop()
            # Recalculate value for the single remaining card
            card = player_hand.cards[0]
            player_hand.value = card.value
            player_hand.aces = 1 if card.rank == 'A' else 0
            
            player_hand.add_card(shoe.deal())
            is_initial_hand = True # A new hand is formed
            continue # Re-evaluate this new hand from the start of the loop
            
    # --- Dealer's Turn ---
    while dealer_hand.value < 17:
        dealer_hand.add_card(shoe.deal())
        
    # --- Determine Reward and Update Q-Table ---
    reward = 0
    if player_hand.value > 21: # Player busts
        reward = -1
    elif dealer_hand.value > 21 or player_hand.value > dealer_hand.value: # Player wins
        reward = 1
    elif player_hand.value < dealer_hand.value: # Player loses
        reward = -1
    
    # Double the reward if the action was Double Down
    if action == ACTION_DOUBLE:
        reward *= 2

    # Update Q-table with the new Q-value using the Bellman equation
    new_state = get_state(player_hand, dealer_hand.cards[0].value, shoe, False)
    max_future_q = np.max(q_table[new_state])
    current_q = q_table[state][action]
    
    new_q = current_q + LEARNING_RATE * (reward + DISCOUNT * max_future_q - current_q)
    q_table[state][action] = new_q

# --- MAIN TRAINING LOOP ---
epsilon = EPSILON_START
for episode in range(EPISODES):
    shoe = Shoe(num_decks=6)
    
    player_hand = Hand()
    dealer_hand = Hand()

    player_hand.add_card(shoe.deal())
    dealer_hand.add_card(shoe.deal())
    player_hand.add_card(shoe.deal())
    dealer_hand.add_card(shoe.deal()) # Dealer's hole card
    
    play_hand(player_hand, dealer_hand, shoe, epsilon)

    epsilon = max(EPSILON_END, epsilon * EPSILON_DECAY)

    if episode % 100000 == 0:
        print(f"Episode: {episode}, Epsilon: {epsilon:.4f}")

# Save the trained Q-table
with open("q_table.pkl", "wb") as f:
    pickle.dump(q_table, f)

print("Training finished and advanced Q-table saved as q_table.pkl")