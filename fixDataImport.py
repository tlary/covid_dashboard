import pandas as pd

# load data
history = pd.read_csv("history.csv")

# remove latest date
latest = history.date.max()
not_latest = history.date != latest
history = history[not_latest]

# save as .csv again
history.to_csv("history.csv")