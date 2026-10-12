
import math
import random 

# 1. score each option with a utility
# utility = ride_value - price_sens * price - time_sens * time

def logit_policy(obs, persona, seed):
    
    ride_value = persona.ride_value
    price_sens = persona.price_sens
    time_sens = persona.time_sens

    utilities = {}
    for option in obs["options"]:

        if option["action"] == "reject":
            utility = 0 
        else: 
            price = option["price_usd"]
            time = option["wait_min"]
            utility = ride_value - price_sens * price - time_sens * time
       
        utilities[option["action"]] = utility

# 2. turn the score into distribution with softmax 
    exps = {action: math.exp(u) for action, u in utilities.items()}

    total = sum(exps.values())

    probs = {action: exp_score / total for action, exp_score in exps.items()}

# 3. sample an action from the distribution 
    rng = random.Random(f"policy seed-{seed}")

    # split the dict into two lists
    actions = list(probs.keys())
    weights = list(probs.values())

    action = rng.choices(actions, weights)[0]

    return action