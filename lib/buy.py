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
np.set_printoptions(precision=5, suppress=True)
originDate = date.today()

from common import *

class immo_buy(curve):

    def __init__(self, file_properties, eco_file_properties):
        self.achat = properties(file_properties)
        self.eco = properties(eco_file_properties)
        self.mensualite = 1500
        self.maturite_credit = 240
        self.taxe_fonciere = 0
        self.valeur_locative = 0
        self.infine = 50000
        self.buy_price_allin = self.achat.prix + self.getNotarialFees()
        self.cout_mensuel_charges = self.getCC() + self.getTF()/12
        self.generate_flows()

    def generate_flows(self):
        f = flows()
        for imonth in range(1, self.infine):
            if imonth <= self.maturite_credit:
                f.addFlow(originDate + relativedelta(months=+imonth), -self.mensualite)
            f.addFlow(originDate + relativedelta(months=+imonth), self.valeur_locative * np.power(1 + self.eco.infla, imonth / 12.0))
            f.addFlow(originDate + relativedelta(months=+imonth), -self.cout_mensuel_charges * 0.75 * np.power(1 + self.eco.infla, imonth / 12.0))

        # ajout de la TF
        for iyear in range(1, self.infine/12):
            f.addFlow(originDate + relativedelta(years=+iyear),-self.valeur_locative * 0.8 * np.power(1 + self.eco.infla, iyear / 12.0))

        print f
        print f.getTRI_NNN(0.02)

    def getNotarialFees(self): return round(self.achat.prix * 7.2 / 100.0, 1)

    def getCC(self):
        if self.valeur_locative * 0.08 < 50: return 50
        elif self.valeur_locative * 0.08 > 350: return 350
        else:
            return self.valeur_locative * 0.08

    def getTF(self):
        print "self.get_valeur_locative():" , self.get_valeur_locative() 
    	if self.taxe_fonciere != 0: return self.taxe_fonciere 
        if self.get_valeur_locative() * 0.95 < 500: return 500
        elif self.get_valeur_locative() * 0.95 > 2500: return 2500
        else:
            return self.get_valeur_locative() * 0.95

    def get_valeur_locative(self):
        if self.valeur_locative != 0: return self.valeur_locative 
        return round(self.achat.prix * 0.0027, 1)

    def get_return_over_capital(self, maturite):
        self.mensualite = self.getM(self.buy_price_allin, maturite)
        cout_total_credit = maturite * self.mensualite - self.buy_price_allin
        amortissement_frais_achat = self.buy_price_allin - self.achat.prix 
        cout_mensuel_credit = cout_total_credit / maturite
        amortissement_mensuel_frais_achat = amortissement_frais_achat / maturite
        # self.cout_mensuel_charges = self.getCC() + self.getTF()/12
        self.return_over_charges = self.valeur_locative - (cout_mensuel_credit + amortissement_mensuel_frais_achat + self.cout_mensuel_charges)
        self.return_over_capital = 100 * (12 * self.return_over_charges / self.achat.prix)

        return self.return_over_capital

    def get_max_return_over_capital(self):
        x = self.lineSpace
        stats ={}
        for item in x:
            stats[item] = round(i.get_return_over_capital(item),3)
        #print 'alternative si doublons:', [key for key, valinstats.iteritems() if val == max(stats.values())]
        return max(stats.iteritems(), key=operator.itemgetter(1))

    def get_tri(self, discount_rate, maturite, inflation, infine='', output='Pct'):
        if infine == '': infine = maturite
        f = flows()
        for imonth in range(1, infine):
            if imonth <= maturite:
                f.addFlow(originDate + relativedelta(months=+imonth), -self.mensualite)
            f.addFlow(originDate + relativedelta(months=+imonth), self.valeur_locative * np.power(1 + inflation, imonth / 12.0))
            f.addFlow(originDate + relativedelta(months=+imonth), -self.cout_mensuel_charges * 0.75 * np.power(1 + inflation, imonth / 12.0))

        # ajout de la TF
        for iyear in range(1, infine/12):
            f.addFlow(originDate + relativedelta(years=+iyear),-self.valeur_locative * 0.8 * np.power(1 + inflation, iyear / 12.0))
        # sell back infine
        f.addFlow(originDate + relativedelta(months=+infine), self.achat.prix * np.power(1 + inflation, infine / 12.0))
        # valeur residuelle credit
        f.addFlow(originDate + relativedelta(months=+infine), -c.getM_Residuel(self.buy_price_allin, maturite, infine) * np.power(1 + inflation, infine / 12.0))
        # print f
        if output == 'Pct': return f.getTRI_Pct()
        else: return f.getTRI_NNN(discount_rate)

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
        else: return f.getTRI_NNN(discount_rate)

    def get_tri_achat(self, discount_rate, maturite, inflation, infine='', output='Pct'):
        if infine == '': infine = int(maturite)
        # print 'infine:', infine, type(infine)
        f = flows()
        for imonth in range(1, infine):
            if imonth <= maturite:
                f.addFlow(originDate + relativedelta(months=+imonth), -self.mensualite)
            # else:
                # f.addFlow(originDate + relativedelta(months=+imonth), -self.mensualite)

            f.addFlow(originDate + relativedelta(months=+imonth), -self.cout_mensuel_charges * 1.0 * np.power(1 + inflation, imonth / 12.0))

        # ajout de la TF
        for iyear in range(1, infine/12):
            f.addFlow(originDate + relativedelta(years=+iyear), -self.valeur_locative * 0.8 * np.power(1 + inflation, iyear / 12.0))
        # sell back infine
        f.addFlow(originDate + relativedelta(months=+infine), self.achat.prix * np.power(1 + inflation, infine / 12.0))
        # valeur residuelle credit
        f.addFlow(originDate + relativedelta(months=+infine), -c.getM_Residuel(self.buy_price_allin, maturite, infine) * np.power(1 + inflation, infine / 12.0))
        # print f
        if output == 'Pct': return f.getTRI_Pct()
        else: return f.getTRI_NNN(discount_rate)

    def __str__(self):
        tstring = 'buy_price: ' + str(self.achat.prix)
        tstring = tstring + '\nbuy_price_all_in: ' + str(self.buy_price_allin)
        tstring = tstring + '\ntaxe_fonciere: ' + str(self.getTF())
        return tstring

if __name__=='__main__':

    if True:
        a = immo_buy('buy.properties', 'eco.properties')
        print a

        # eco = properties('eco.properties')
        # print "loyer %s, prix achat %s" % (location.loyer, achat.prix)
        # i = immo(achat.prix, location.loyer)
        # print 'taxe fonciere: %s' % (i.getTF())


        # print 'mensualite %s' % c.getM(achat.prix + i.getNotarialFees(), achat.maturite)
        # print 'prix achat AI %s, capital residuel %s apres %s mois' % (achat.prix + i.getNotarialFees(), c.getM_Residuel(achat.prix + i.getNotarialFees(), achat.maturite, achat.revente), achat.revente)
        # print '\n'
        # print "price %s, renting %s, infla %s, selling_back %s, discount_rate %s" % (achat.prix, location.loyer, eco.infla, achat.revente, eco.discount_rate)
        # print 'get_max_return_over_capital:', i.get_max_return_over_capital()
        # print 'get_tri_achat:', i.get_tri_achat(eco.discount_rate, achat.maturite, eco.infla, achat.revente, output=''), i.get_tri_achat(eco.discount_rate, achat.maturite, eco.infla, achat.revente, output='Pct')
        # print 'get_tri_location:', i.get_tri_location(eco.discount_rate, achat.maturite, eco.infla, achat.revente, output='')
        # print 'get_tri_location_with_placement:', i.get_tri_location_with_placement(eco.discount_rate, achat.maturite, eco.infla, achat.revente, output='')
        # print 'get_tri_investment:', i.get_tri(eco.discount_rate, achat.maturite, eco.infla, achat.revente, output='')#, i.get_tri(discount_rate, tmaturite,infla, selling_back, output='Pct')



