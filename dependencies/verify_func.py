from readb import _Getch
import re
import pickle
with open("meta", 'rb') as fp:
    state_list = pickle.load(fp)
print(len(state_list["X"]), len(state_list["y"]))
print(state_list["X"][501], state_list["y"][501])

#jumped, hike, rise,bullish, optimistic, rally, surge, soared, buy, higher, gains, lower, jumped
#slumped, fell, worry, bearish, miss, sell, losses, higher, warn
