import pandas as pd
import random
from environment import RiderEnv

def smoke_policy(obs, persona, seed):
    rng = random.Random(seed)

    return rng.choice(["standard", "reject", "wait_save"])

control = RiderEnv(intervention=False)
treatment = RiderEnv(intervention=True)

results = []

for env in (control, treatment):
    for seed in range(1000):
        env.reset(seed)
        action = smoke_policy(env._obs, env.persona, seed)
        record = env.step(action)
        results.append(record)


df = pd.DataFrame(results)
print(df.groupby("arm")["converted"].mean())
print("________________________________________")
print(df.groupby("arm")["mode"].value_counts())
print("________________________________________")
print(df.groupby("arm")["persona_type"].value_counts())