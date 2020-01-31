import csv
from os import chdir

from datetime import *
chdir('C:/Users/SONY/PycharmProjects/helloworldtests/data files new')


header = ['symbol', 'golden', 'deaths', "last_update"]
with open('success.csv', "w", newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(header)




