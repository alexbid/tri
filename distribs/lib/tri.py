#%matplotlib inline

import sys
etc = sys.path[0].replace('/lib','/etc')
sys.path.append(etc)

import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import operator
# from scipy.optimize import fsolve
from datetime import date
import collections
from dateutil.relativedelta import relativedelta
np.set_printoptions(precision=5, suppress=True)
originDate = date.today()

from common import *


class immo(curve):

    def getNotarialFees(self): return round(self.buy_price * 7.2 / 100.0, 1)

    def getCC(self):
        if self.valeur_locative * 0.08 < 50: return 50
        elif self.valeur_locative * 0.08 > 350: return 350
        else:
            return self.valeur_locative * 0.08

    def getTF(self):
    	if self.taxe_fonciere != 0: return self.taxe_fonciere 
        if self.valeur_locative * 0.95 < 500: return 500
        elif self.valeur_locative * 0.95 > 2500: return 2500
        else:
            return self.valeur_locative * 0.95

    def __init__(self, buy_price, valeur_locative, taxe_fonciere=0):
        self.return_over_charges = 0
        self.return_over_capital = 0
        self.mensualite = 0
		
        self.taxe_fonciere = taxe_fonciere
        self.buy_price = buy_price
        self.valeur_locative = valeur_locative
        self.buy_price_allin = self.buy_price + self.getNotarialFees()
        self.cout_mensuel_charges = self.getCC() + self.getTF()/12

    def get_return_over_capital(self, maturite):
        self.mensualite = self.getM(self.buy_price_allin, maturite)
        cout_total_credit = maturite * self.mensualite - self.buy_price_allin
        amortissement_frais_achat = self.buy_price_allin - self.buy_price
        cout_mensuel_credit = cout_total_credit / maturite
        amortissement_mensuel_frais_achat = amortissement_frais_achat / maturite
        # self.cout_mensuel_charges = self.getCC() + self.getTF()/12
        self.return_over_charges = self.valeur_locative - (cout_mensuel_credit + amortissement_mensuel_frais_achat + self.cout_mensuel_charges)
        self.return_over_capital = 100 * (12 * self.return_over_charges / self.buy_price)

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
        f.addFlow(originDate + relativedelta(months=+infine), self.buy_price * np.power(1 + inflation, infine / 12.0))
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
        f.addFlow(originDate + relativedelta(months=+infine), self.buy_price * np.power(1 + inflation, infine / 12.0))
        # valeur residuelle credit
        f.addFlow(originDate + relativedelta(months=+infine), -c.getM_Residuel(self.buy_price_allin, maturite, infine) * np.power(1 + inflation, infine / 12.0))
        # print f
        if output == 'Pct': return f.getTRI_Pct()
        else: return f.getTRI_NNN(discount_rate)

    def __str__(self):
        tstring = 'buy_price: ' + str(self.buy_price)
        tstring = tstring + '\nbuy_price_all_in: ' + str(self.buy_price_allin)
        tstring = tstring + '\nreturn_over_capital: ' + str(self.return_over_capital)
        return tstring

# # if __name__=='__main__':
# if False:
#     c = curve()
#     x = c.lineSpace

#     # price = 348000.0
#     # renting = 1175.0
#     price = 478000.0
#     renting = 1450.0
#     infla = 0.017
#     #print "max Gamma:", c.maxGamma(price)
#     #print "optimal funding:", c.maxGamma(price)[0], str(100*c.getRate(c.maxGamma(price)[0])) + '%', round(c.getM(price, c.maxGamma(price)[0]),1), "EUR"

#     i = immo(price, renting)
#     x = c.lineSpace

#     #plt.plot(x,c.getM(21591, x))
#     #plt.plot(x,c.NGamma(21591, x))
#     #plt.ylabel('Amount')
#     #plt.xlabel("months")
#     #plt.plot(x, i.get_return_over_capital(x))
#     #plt.show()

#     tmaturite = int(round(i.get_max_return_over_capital()[0],0))

#     print "price:", price
#     print "renting:", renting
#     print "infla:", infla
#     print 'get_max_return_over_capital:', i.get_max_return_over_capital()
#     print 'mensualite:', round(c.getM(price + i.getNotarialFees(),tmaturite),2), str(round(c.getRate(tmaturite)*100,2)) + '%'

#     tau_solution = i.get_percent_tri(infla, tmaturite)
#     print "The solution is Pctg TRI = %r for infla %s, price %s and renting %s" % (tau_solution[0] * 100.0, infla * 100.0, price, renting)
#     print "The solution is Amnt TRI:", i.get_tri(tau_solution[0], tmaturite, infla)
#     print "Infla from flat TRI:", i.get_infla_from_flat_tri(tmaturite)[0] * 100.0


#     print 'inputs:', tau_solution[0], tmaturite, infla
#     loc = i.get_tri_location(tau_solution[0], tmaturite, infla, 30)
#     achat = i.get_tri_achat(tau_solution[0], tmaturite, infla, 30)

#     print "loc:", loc
#     print "achat:", achat
#     print "gap:", achat - loc

# if False:
#     price = 400000.0
#     renting = 850
#     infla = 0.018

#     tmaturite = 220 #emprunt sur 18.33Y
#     selling_back = 12*5 # revente dans 30Y
#     discount_rate = 0.02 # taux sans risque

#     i = immo(price, renting)
#     c = curve()

#     print '', c.getM(price + i.getNotarialFees(),tmaturite)
#     print price + i.getNotarialFees(), c.getM_Residuel(price + i.getNotarialFees(), tmaturite, selling_back)

#     print "price %s, renting %s, infla %s, selling_back %s, discount_rate %s" % (price, renting, infla, selling_back, discount_rate)
#     print 'get_max_return_over_capital:', i.get_max_return_over_capital()
#     print 'get_tri_achat:', i.get_tri_achat(discount_rate, tmaturite, infla, selling_back, output=''), i.get_tri_achat(discount_rate, tmaturite, infla, selling_back, output='Pct')
#     print 'get_tri_location:', i.get_tri_location(discount_rate, tmaturite, infla, selling_back, output='')
#     print 'get_tri_location_with_placement:', i.get_tri_location_with_placement(discount_rate, tmaturite, infla, selling_back, output='')
#     print 'get_tri_investment:', i.get_tri(discount_rate, tmaturite, infla, selling_back, output='')#, i.get_tri(discount_rate, tmaturite,infla, selling_back, output='Pct')

#     #plt.plot(x,c.getM(21591, x))
#     #plt.plot(x,c.NGamma(21591, x))
#     #plt.ylabel('Amount')
#     #plt.xlabel("months")
#     x = np.linspace(-0.01,0.04, num=500)
#     y = []
#     for item in x:
#         y.append(i.get_tri_achat(discount_rate, tmaturite, item, selling_back, output=''))

#     plt.plot(x, y)
#     plt.show()

if True:
    location = properties('location.properties')
    achat = properties('achat.properties')
    eco = properties('eco.properties')


    print "loyer %s, prix achat %s" % (location.loyer, achat.prix)

    i = immo(achat.prix, location.loyer)
    print 'taxe fonciere: %s' % (i.getTF())

    c = curve()

    print 'mensualite %s' % c.getM(achat.prix + i.getNotarialFees(), achat.maturite)
    print 'prix achat AI %s, capital residuel %s apres %s mois' % (achat.prix + i.getNotarialFees(), c.getM_Residuel(achat.prix + i.getNotarialFees(), achat.maturite, achat.revente), achat.revente)
    print '\n'
    print "price %s, renting %s, infla %s, selling_back %s, discount_rate %s" % (achat.prix, location.loyer, eco.infla, achat.revente, eco.discount_rate)
    print 'get_max_return_over_capital:', i.get_max_return_over_capital()
    print 'get_tri_achat:', i.get_tri_achat(eco.discount_rate, achat.maturite, eco.infla, achat.revente, output=''), i.get_tri_achat(eco.discount_rate, achat.maturite, eco.infla, achat.revente, output='Pct')
    print 'get_tri_location:', i.get_tri_location(eco.discount_rate, achat.maturite, eco.infla, achat.revente, output='')
    print 'get_tri_location_with_placement:', i.get_tri_location_with_placement(eco.discount_rate, achat.maturite, eco.infla, achat.revente, output='')
    print 'get_tri_investment:', i.get_tri(eco.discount_rate, achat.maturite, eco.infla, achat.revente, output='')#, i.get_tri(discount_rate, tmaturite,infla, selling_back, output='Pct')



