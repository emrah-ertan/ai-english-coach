import pandas as pd
import random

WORDS_CSV = "./data/words_levels_dataset.csv"

# Dataset URL: https://www.kaggle.com/datasets/nezahatkk/10-000-english-words-cerf-labelled


def get_random_word_by_level(level):
    df = pd.read_csv(WORDS_CSV)
    level_words = df[df["CEFR"] == level.upper()]
    return level_words.sample(1).iloc[0].to_dict()
