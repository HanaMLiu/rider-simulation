"""
synthetic_riders.py -- generate one row per rider from known three known rider types. 

At a company, the riders are returned by a data warehouse query function: return pd.read_sql(query, connection).

Each rider's true type is recorded, so k-means clustering results can be checked against ground truth. 

"""

from curses import beep
import numpy as np 
import pandas as pd 


TRUE_TYPES = {
    #                 share  trips  airport   wait_save  booked    km    rush
    "business":      (0.20,   4,    (6, 4),   (1, 30),   (18, 2),  20,   (2, 8)),
    "budget":        (0.35,   5,    (1, 30),  (6, 5),    (4, 6),    4,   (3, 7)),
    "commuter":      (0.45,  18,    (1, 40),  (2, 10),   (8, 2),    9,   (8, 2)),
}



def generate_riders(n_riders=3000, seed=0):
    rng = np.random.default_rng(seed)
    names = list(TRUE_TYPES.keys())
    shares = [TRUE_TYPES[t][0] for t in names]
    types = rng.choice(names, size=n_riders, p=shares)      

    rows = []
    for rider_id, t in enumerate(types):
        _, trips, airport, wait_save, booked, km, rush = TRUE_TYPES[t]
        rows.append({
            "rider_id": rider_id,
            "true_type": t,
            "trips_per_month": trips,

            # shares between 0 and 1: beta distributions
            "pct_airport": rng.beta(*airport),
            "pct_wait_save": rng.beta(*wait_save),
            "pct_booked": rng.beta(*booked),

            "avg_km": km,
            "pct_rush_hour": rng.beta(*rush)
        })

    riders = pd.DataFrame(rows)

    # realism: some riders were never offered Wait & Save
    # randomly blank out pct_wait_save for 10% of riders 
    never_offered = rng.random(n_riders) < 0.10     # generate a mask 
    riders.loc[never_offered, "pct_wait_save"] = np.nan     #.loc[row, column] takes either a mask or name to locate cells to set to NULL 
    
    return riders 

if __name__ == "__main__":
    riders = generate_riders()
    print(f"\n{len(riders)} riders")
    print(riders["true_type"].value_counts(normalize=True).round(2).to_string())