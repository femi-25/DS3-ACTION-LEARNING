#!/usr/bin/env python3
import os
import random
import string

import numpy as np
import pandas as pd

RAW_DIR = "/opt/airflow/data/raw_data"
os.makedirs(RAW_DIR, exist_ok=True)

# === 1) Define schema (everything except `overall`) ===
NUMERIC_COLUMNS = {
    "age": (16, 40),
    "height_cm": (160, 200),
    "weight_kg": (55, 100),
    "potential": (50, 95),
    "weak_foot": (1, 5),
    "skill_moves": (1, 5),

    # continuous (float) – we’ll generate these to one decimal place
    "pace": (20.0, 100.0),
    "shooting": (20.0, 100.0),
    "passing": (20.0, 100.0),
    "dribbling": (20.0, 100.0),
    "defending": (10.0, 100.0),
    "physic": (10.0, 100.0),

    # attacking (int)
    "attacking_crossing": (1, 100),
    "attacking_finishing": (1, 100),
    "attacking_heading_accuracy": (1, 100),
    "attacking_short_passing": (1, 100),
    "attacking_volleys": (1, 100),

    # skill (int)
    "skill_dribbling": (1, 100),
    "skill_curve": (1, 100),
    "skill_fk_accuracy": (1, 100),
    "skill_long_passing": (1, 100),
    "skill_ball_control": (1, 100),

    # movement (int)
    "movement_acceleration": (1, 100),
    "movement_sprint_speed": (1, 100),
    "movement_agility": (1, 100),
    "movement_reactions": (1, 100),
    "movement_balance": (1, 100),

    # power (int)
    "power_shot_power": (1, 100),
    "power_jumping": (1, 100),
    "power_stamina": (1, 100),
    "power_strength": (1, 100),
    "power_long_shots": (1, 100),

    # mentality (int)
    "mentality_aggression": (1, 100),
    "mentality_interceptions": (1, 100),
    "mentality_positioning": (1, 100),
    "mentality_vision": (1, 100),
    "mentality_penalties": (1, 100),
    "mentality_composure": (1, 100),

    # defending (int)
    "defending_standing_tackle": (1, 100),
    "defending_sliding_tackle": (1, 100),
}

CATEGORICAL_COLUMNS = {
    "preferred_foot": ["Left", "Right"],
    "main_position": ["CB","LB","RB","CM","CDM","CAM","LW","RW","ST"],
    "att_work_rate": ["Low","Medium","High"],
    "def_work_rate": ["Low","Medium","High"],
    "nationality_grouped": ["Argentina","Brazil","Portugal","Poland","Other"],
}


def make_clean_df(n=100):
    df = pd.DataFrame({col: np.random.randint(lo, hi+1, size=n)
                       for col, (lo, hi) in NUMERIC_COLUMNS.items()})
    # floats
    df["pace"]      = np.random.uniform(*NUMERIC_COLUMNS["pace"], size=n).round(1)
    df["shooting"]  = np.random.uniform(*NUMERIC_COLUMNS["shooting"], size=n).round(1)
    df["passing"]   = np.random.uniform(*NUMERIC_COLUMNS["passing"], size=n).round(1)
    df["dribbling"] = np.random.uniform(*NUMERIC_COLUMNS["dribbling"], size=n).round(1)
    df["defending"] = np.random.uniform(*NUMERIC_COLUMNS["defending"], size=n).round(1)
    df["physic"]    = np.random.uniform(*NUMERIC_COLUMNS["physic"], size=n).round(1)
    # categoricals
    for col, vals in CATEGORICAL_COLUMNS.items():
        df[col] = np.random.choice(vals, size=n)
    return df


def inject_error(df, error_type):
    n = len(df)
    if error_type == "missing_column":
        # drop one random column
        col = random.choice(df.columns)
        print(f"→ Injecting MISSING_COLUMN: dropping {col}")
        return df.drop(columns=[col])
    elif error_type == "extra_column":
        # add a useless column full of random strings
        print("→ Injecting EXTRA_COLUMN: adding `foo_bar`")
        df2 = df.copy()
        df2["foo_bar"] = [ "".join(random.choices(string.ascii_letters, k=5)) for _ in range(n) ]
        return df2
    elif error_type == "nulls":
        # inject nulls into 10% of rows of a required numeric column
        col = random.choice(list(NUMERIC_COLUMNS.keys()))
        idx = df.sample(frac=0.1).index
        print(f"→ Injecting NULLS in {col} at {len(idx)} rows")
        df2 = df.copy()
        df2.loc[idx, col] = None
        return df2
    elif error_type == "bad_type":
        # pick a numeric column, replace 5% of entries with a string
        col = random.choice(list(NUMERIC_COLUMNS.keys()))
        idx = df.sample(frac=0.05).index
        print(f"→ Injecting BAD_TYPE in {col} at {len(idx)} rows")
        df2 = df.copy()
        df2.loc[idx, col] = "N/A"
        return df2
    elif error_type == "invalid_category":
        # pick a categorical column, put invalid category in 10% rows
        col = random.choice(list(CATEGORICAL_COLUMNS.keys()))
        idx = df.sample(frac=0.1).index
        print(f"→ Injecting INVALID_CATEGORY in {col} at {len(idx)} rows")
        df2 = df.copy()
        df2.loc[idx, col] = "INVALID_VALUE"
        return df2
    else:
        return df


if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)

    error_types = ["missing_column", "extra_column", "nulls", "bad_type", "invalid_category"]

    for i, err in enumerate(error_types, start=1):
        df = make_clean_df(n=100)
        df_err = inject_error(df, err)
        path = os.path.join(RAW_DIR, f"players_{i}.csv")
        df_err.to_csv(path, index=False)
        print(f"── Wrote {path} ({err})")
