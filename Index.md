# Introduction #

Busca Vuelos is small script for batch mode flight searching.
It supports resuming previous searches and implements exponential backoff in order to avoid being banned by the gateway.
Only works with despegar.com.ar
Interactive mode is recommended however it can be used from a batch console.

Prices are always in us dollars. Airport Code must be IATA Code.

# Install #

**Download the source code from [here](http://code.google.com/p/busca-vuelos/downloads/list)**

**Extract the source code**

**Copy busca\_vuelo to your python modules folder.**

# Examples #


## Interactive Mode ##
```python

In [11]: import busca_vuelo
In [12]: busca_vuelo.get_flights()
#Fecha de Partida( en formato YYYYMMDD)
20111229
#Fecha de Vuelta( en formato YYYYMMDD)
20120902
#Ingrese Aeropuerto Origen
Buenos Aires
#Ingrese Aeropuerto Destino
Tokyo
http://www.despegar.com.ar/Flights.Services/Flights/Flights.svc/ClusteredFlights/BUE/TYO/2011-12-30/2012-09-02/1/0/0

0.00 % completo
Out[12]:
[({'arrivando': '02/09/2012',
'compania': [u'Alitalia'],
'dest': u'Tokyo',
'escalas': 2,
'numero': [u'681', u'784'],
'precio': 2807,
'saliendo': '30/12/2011'},
{'arrivando': '02/09/2012',
'compania': [u'Alitalia'],
'dest': u'Tokyo',
'escalas': 2,
'numero': [u'681', u'784'],
'precio': 2807,
'saliendo': '30/12/2011'})]
```

## Using Time Deltas ##
Use a time delta to look for the cheapest flight within a time interval

### Negative time delta ###
It will search flights into the time interval [date, return date (+,-,delta)](departure.md)
```
import busca_vuelo
#airport codes must be iata codes
kwargs = {"source":"BUE","destination":"FRA","delta_dt_vuelta":12,"silent":True}
vuelos = busca_vuelo.get_flights(**kwargs)
#Prompt for dates
Fecha de Partida( en formato YYYYMMDD)
20111228
Fecha de Vuelta( en formato YYYYMMDD)
20120530
#Sort result using price 
for r in sorted(vuelos,key=lambda x: x[0]["precio"])[0:5]:
	v = r[0]
	print "%s %s USD a %s el %s en %s escalas volviendo %s" % ("-".join(v["compania"]),v["precio"], v["dest"], v["saliendo"],v["escalas"]-1,v["arrivando"])

```
Outputs the top 5 cheapest flights

**Lufthansa 1323 USD a Frankfurt el 28/12/2011 en 0 escalas volviendo 29/05/2012**

**Lufthansa 1323 USD a Frankfurt el 28/12/2011 en 0 escalas volviendo 22/05/2012**

**Lufthansa 1372 USD a Frankfurt el 28/12/2011 en 0 escalas volviendo 30/05/2012**

**Lufthansa 1372 USD a Frankfurt el 28/12/2011 en 0 escalas volviendo 28/05/2012**

**Lufthansa 1372 USD a Frankfurt el 28/12/2011 en 0 escalas volviendo 25/05/2012**

## Positive Time Delta ##
The same idea but moving forward the departure date. This example will search flights into the interval [departure\_date(+,-,5),return\_date(+-,15)]
```
kwargs ={"source":"BUE","destination":"FRA","delta_dt_ida":5,"delta_dt_vuelta":12,"silent":True}
vuelos = busca_vuelo.get_flights(**kwargs)
#It takes a little while...
#using silent=False prints search progress
#Prompts for departue and return date
Fecha de Partida( en formato YYYYMMDD)
20111228
Fecha de Vuelta( en formato YYYYMMDD)
20120530

for r in sorted(vuelos,key=lambda x: x[0]["precio"])[0:5]:
	v = r[0]
	print "%s %s USD a %s el %s en %s escalas volviendo %s" % ("-".join(v["compania"]),v["precio"], v["dest"], v["saliendo"],v["escalas"]-1,v["arrivando"])
```

### Exponential Backoff ###
It's possible to disable exponential backoff.
Disabling exponential backoff is recommended in case it is used with silent mode on.
Just add the parameters backoff= False or add it to the kwargs dictionary.