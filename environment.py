import random 
from dataclasses import dataclass




# env = RiderEnv(intervention=True)
# obs = env.reset(seed=7)
# action = policy(obs, env.persona)
# outcome = env.step(action)

@dataclass(frozen=True)
class Persona:
    persona_type: str
    description: str
    ride_value: float 
    price_sens: float
    time_sens: float 
    share: float

PERSONAS = [
    Persona("student", "On a tight budget. Rarely in a hurry.",
            ride_value=3.5, price_sens=0.40, time_sens=0.08, share=0.4),
    Persona("commuter", "Rides to work most days. Cannot be late.",
            ride_value=5.0, price_sens=0.20, time_sens=0.25, share=0.4),
    Persona("business_traveler", "Trip is expensed. Wants the fastest pickup.",
            ride_value=8.0, price_sens=0.04, time_sens=0.50, share=0.2),
]


class RiderEnv: 
    def __init__(self, intervention=False):
        self.intervention = intervention 

        #episode states: filled with reset
        self.persona = None     
        self._obs = None 

    def reset(self, seed):
        # runs once per episode 
        # 1. make a random generator from the seed
        rng = random.Random(seed)

        # 2. sample persona
        weights =[p.share for p in PERSONAS]
        self.persona = rng.choices(PERSONAS, weights=weights)[0]

        # 3. sample trip context 
        trip = {
            "distance": round(rng.uniform(1,30),1),
            "time" : rng.randrange(24),
            "bad_weather": rng.random() < 0.15 

        }

        # 4. compute prices and wait times
        surge = 1.0
        if trip["time"] in (7,8,9,17,18,19):
            surge += 0.5
        if trip["bad_weather"]:
            surge += 0.8
        
        standard_price = round(trip["distance"] * 1.7 * surge, 2)
        save_price = round(standard_price * 0.85, 2)

        standard_wait = rng.randint(1,8)
        save_wait = standard_wait + rng.randint(5,15)

        # 5. assemble the obs dict
        banner = None
        if self.intervention:
            wait_more = save_wait - standard_wait
            save_more = standard_price - save_price
            banner = f"Wait {wait_more} more minutes, save ${save_more:.2f}!"
        obs = {
            "options": [
                {"action": "standard", "price_usd": standard_price, "wait_min": standard_wait},
                {"action": "wait_save", "price_usd": save_price, "wait_min": save_wait},
                {"action": "reject"}
            ],
            "banner": banner,
            "trip_context": trip
        }

        # 6. store on self, return what the rider sees 
        self._obs = obs     # without storing, env.step will have nothing to read
        return obs

    
    
