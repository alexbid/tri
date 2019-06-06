#%matplotlib inline

import sys
etc = sys.path[0].replace('/lib','/etc')
sys.path.append(etc)

import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import operator
from datetime import date
import collections
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY
np.set_printoptions(precision=5, suppress=True)
originDate = date.today()

from common import *

class immo_rent(curve):

    def __init__(self, file_properties, eco_file_properties):
        self.rent = properties(file_properties)
        self.eco = properties(eco_file_properties)
        
        print self.rent
        print self.eco
        
        self.generate_flows()

    def generate_flows(self):

    	f = flows()
    	for date in rrule(MONTHLY, bymonthday=1, count=self.eco.infine):
            date = date.date()
            f.addFlow(date, -self.rent.loyer * np.power(1 + self.eco.infla, (date - originDate).days / 365.0))
            f.addFlow(date, -self.rent.cout_mensuel_charges * np.power(1 + self.eco.infla, (date - originDate).days / 365.0))

        # f = flows()
        # for imonth in range(1, self.eco.infine):
        #     f.addFlow(originDate + relativedelta(months=+imonth), -self.rent.loyer * np.power(1 + self.eco.infla, imonth / 12.0))
        #     f.addFlow(originDate + relativedelta(months=+imonth), -self.rent.cout_mensuel_charges * np.power(1 + self.eco.infla, imonth / 12.0))
            
        print f
        print "NPV:", f.getTRI_NNN(self.eco.discount_rate)

    def get_tri_location(self, discount_rate, maturite, inflation, infine='', output='Pct'):
        if infine == '': infine = maturite
        f = flows()
        for imonth in range(1, infine):
            if imonth <= maturite:
                f.addFlow(originDate + relativedelta(months=+imonth), 0)
            f.addFlow(originDate + relativedelta(months=+imonth), -self.valeur_locative * np.power(1 + inflation, imonth / 12.0))
            f.addFlow(originDate + relativedelta(months=+imonth), -self.cout_mensuel_charges * 0.25 * np.power(1 + inflation, imonth / 12.0))

        # print f
        if output == 'Pct': return f.getTRI_Pct()
        else: return f.getTRI_NNN(discount_rate)

    def get_tri_location_with_placement(self, discount_rate, maturite, inflation, infine='', output='Pct'):
        if infine == '': infine = maturite
        f = flows()
        for imonth in range(1, infine):
            if imonth <= maturite:
                f.addFlow(originDate + relativedelta(months=+imonth), 0)

            f.addFlow(originDate + relativedelta(months=+imonth), (self.mensualite - self.valeur_locative)* np.power(1 + discount_rate, imonth / 12.0))
            f.addFlow(originDate + relativedelta(months=+imonth), -self.valeur_locative * np.power(1 + inflation, imonth / 12.0))
            f.addFlow(originDate + relativedelta(months=+imonth), -self.cout_mensuel_charges * 0.25 * np.power(1 + inflation, imonth / 12.0))

        # print f
        if output == 'Pct': return f.getTRI_Pct()
        else: return f.getTRI_NNN(self.eco.discount_rate)

    def __str__(self):
        tstring = ''
        #tstring = 'buy_price: ' + str(self.achat.prix)
        #tstring = tstring + '\nbuy_price_all_in: ' + str(self.buy_price_allin)
        #tstring = tstring + '\ntaxe_fonciere: ' + str(self.taxe_fonciere)
        return tstring

if __name__=='__main__':
    if True:
        a = immo_rent('rent.properties', 'eco.properties')
        print a


