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
        self.seed = None 

    def reset(self, seed):
        # runs once per episode 
        # 1. make a random generator from the seed
        rng = random.Random(seed)

        # 2. sample persona
        self.seed = seed
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
        wait_more = None
        save_more = None 
        if self.intervention:
            wait_more = save_wait - standard_wait
            save_more = round(standard_price - save_price, 2)
            banner = f"Wait {wait_more} more minutes, save ${save_more}!"
        obs = {
            "options": [
                {"action": "standard", "price_usd": standard_price, "wait_min": standard_wait},
                {"action": "wait_save", "price_usd": save_price, "wait_min": save_wait},
                {"action": "reject", "price_usd": 0.0, "wait_min": None}
            ],
            "banner": banner,
            "wait_more": wait_more,
            "save_more": save_more,
            "trip_context": trip
        }
  
        # 6. store on self, return what the rider sees 
        self._obs = obs     # without storing, env.step will have nothing to read
        return obs


    def step(self, action: str):
        # 1. check if action is legal
        if action not in ("standard", "wait_save", "reject"):
            raise ValueError(f"Unknown action: {action!r}")

        # 2. lookup the option from obs
        options = self._obs["options"]      # list of dict
        for option in options:
            if option["action"] == action:
                break
        
        # 3. built the result as a dict
        record = {
            # user: which rider, which arm
            "seed": self.seed,
            "arm": self.intervention, 
            "persona_type": self.persona.persona_type,
            
            # trip: distance, time and weather
            "distance": self._obs["trip_context"]["distance"],
            "time": self._obs["trip_context"]["time"],
            "bad_weather": self._obs["trip_context"]["bad_weather"],

            # user decision
            "mode": action,
            "converted": action != "reject",
            "revenue": option["price_usd"],
            "wait_time": option["wait_min"],

            # banner information
            "wait_more": self._obs["wait_more"],
            "save_more": self._obs["save_more"]


        }

        return record 
    
    
    
