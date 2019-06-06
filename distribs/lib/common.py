

import sys
import os

lib = str(sys.path[0])
etc = lib.replace('/lib','/etc').replace('\\lib','\\etc')

import numpy as np
from datetime import date
from scipy.optimize import fsolve
import collections

class flows:
    # list of flows : date, flow, 
    def __init__(self):
        self.flowList = {}
        self.originDate = date.today()

    def __str__(self):
        self.flowList = collections.OrderedDict(sorted(self.flowList.items()))
        rtstring = ''
        for tdate, flow in self.flowList.iteritems():
            rtstring = rtstring + '\n' + tdate.strftime('%d/%m/%Y') + ' =>' + ", ".join(str(x) for x in flow)
        return str(rtstring)

    def addFlow(self, tdate, amount):
        if self.flowList.has_key(tdate):
            buff = self.flowList[tdate]
            buff.append(amount)
            self.flowList[tdate] = buff
        else:
            self.flowList[tdate] = [amount]

    def getTRI_NNN(self, discount_rate):
        np_buff = []
        for tdate, flow in self.flowList.iteritems():
            day_number = (tdate - self.originDate).days
            np_buff.append(np.sum(flow) / np.power(1 + discount_rate, day_number / 365.0))
        return np.sum(np_buff)

    def getTRI_Pct(self): return fsolve(self.getTRI_NNN, 0.0)

class curve:
    lineSpace = np.linspace(84,300, num=50)

    def getRate(self, maturity):
        credit = properties('credit.properties')
        xp = credit.curve.keys()
        fp = credit.curve.values()
        return np.interp(maturity, xp, fp)/100.0

    def getM(self, NNN, maturity, rate=False):
        if rate == False: rate = self.getRate(maturity)
        X = np.power(1 + rate, 1 / 12.0)
        return np.power(X, maturity) * NNN * (1 - X) / (1 - np.power(X,maturity))

    def getM_Residuel(self, NNN, maturity, rest_maturity, rate=False):
            if rate==False: 
                print 'rate:', self.getRate(maturity)
                rate = self.getRate(maturity)
            if rest_maturity <= 0: return NNN
            if rest_maturity >= maturity: return 0.0
            mensualite = self.getM(NNN, maturity, rate)
            for i in range(1, rest_maturity+1): NNN = NNN * np.power(1 + rate, 1 / 12.0) - mensualite
            return NNN

    def NDer(self, NNN, maturity):
        h=1
        return (self.getM(NNN, maturity+h) - self.getM(NNN,maturity-h))/(2*h)

    def NGamma(self, NNN, maturity):
        #h=1
        h=1e-10
        return (self.NDer(NNN, maturity+h) - self.NDer(NNN,maturity-h))/(2*h)

    def maxGamma(self, NNN):
        stats ={}
        for item in self.lineSpace:
            stats[item] = self.NGamma(NNN, item)
        return max(stats.iteritems(), key=operator.itemgetter(1))

class variable:
    def __init__(self, tlyne):
        # print 'init variable'
        temp = tlyne.split('=')
        if len(temp) == 2:
            self.field = str(temp[0])
            self.value = temp[1]

    def __str__(self):
        return str(self.field) + '#' + str(self.value)

class properties:
    def __init__(self, tfile):
        self.type = tfile
        self.read(tfile)

    def __str__(self):
        tstring = ''
        for keys, values in self.dico.items(): tstring = tstring + '\n' + keys + ': ' + str(values)
        return tstring + '\n'

    def todict(self,strDico):
        dico = {}
        for item in strDico.replace('{','').replace('}','').split(','):
            buff = item.split(':')
            dico[int(buff[0].strip())] = float(buff[1].strip())
        return dico

    def read(self, tfile):
        dico = {}
        for lyne in open(os.path.join(etc, tfile)):
            if (lyne[0]!='#') and (lyne[0]!='\n') and ('=' in lyne):
                lyne = lyne.replace('\n', '')
                v = variable(lyne)
                dico[v.field] = v.value
        self.dico = dico                

        if self.type == 'rent.properties':
            if dico.has_key('loyer'): self.loyer = float(dico['loyer'])
            if dico.has_key('cout_mensuel_charges'): self.cout_mensuel_charges = float(dico['cout_mensuel_charges'])
        elif self.type == 'buy.properties':
            if dico.has_key('prix'): self.prix = float(dico['prix'])
            if dico.has_key('maturite'): self.maturite = int(dico['maturite'])
            if dico.has_key('revente'): self.revente = int(dico['revente'])
            if dico.has_key('valeur_locative'): self.valeur_locative = int(dico['valeur_locative'])
            if dico.has_key('taxe_fonciere'): self.taxe_fonciere = int(dico['taxe_fonciere'])
            if dico.has_key('cout_mensuel_charges'): self.cout_mensuel_charges = float(dico['cout_mensuel_charges'])
        elif self.type == 'eco.properties':   
            if dico.has_key('infla'): self.infla = float(dico['infla'])
            if dico.has_key('discount_rate'): self.discount_rate = float(dico['discount_rate'])
            if dico.has_key('infine'): self.infine = int(dico['infine'])
        elif self.type == 'credit.properties':   
            if dico.has_key('mensualite'): self.mensualite = float(dico['mensualite'])
            if dico.has_key('maturite_credit'): self.maturite_credit = float(dico['maturite_credit'])
            if dico.has_key('apport'): self.apport = float(dico['apport'])
            if dico.has_key('curve'): self.curve = self.todict(dico['curve'])

if __name__=='__main__':
    p = properties('rent.properties')
    print p
    
