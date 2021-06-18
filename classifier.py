import numpy as np
import pandas as pd
import scipy as sp
import price_data as price
import chart
from sklearn.ensemble import RandomForestClassifier

#get bitcoin price data

training_data=chart.get_support_resistance(price.get_price_data(symbol='BTC/USDT', interval='4h'))
