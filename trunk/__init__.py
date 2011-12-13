import urllib2,urllib
import json
import datetime
import time
import random
import os

localdir = lambda : os.path.dirname(__file__) + "/"
def get_airports():
	
	f = open("%smisc/topAirlinesAndCities1.js"%localdir())
	lines = [l.strip() for l in f]
	f.close()
	ret = eval(lines[0].strip()[1:-1])
	return ret




def promt_airport(prompt):
	aeropuertos = get_airports()
	search_ae_kw = lambda x, k: map(lambda y: y[k],filter(lambda y: x.lower() in y["n"].lower(), aeropuertos))
	search_iate = lambda x: search_ae_kw(x,"m")
	search_city = lambda x: search_ae_kw(x,"n")

	somewhere = raw_input("%s\n" % prompt).strip()
	while len(search_iate(somewhere)) == 0:
		somewhere = raw_input("%s not found\n %s \n" % (somewhere, prompt) ).strip()
	iate_codes = search_iate(somewhere)
	cities = search_city(somewhere)
	if len(iate_codes) > 1:
			index = None
			while type(index) is not int or (index > len(iate_codes) + 1	and index <= 0):
				try:
					index = raw_input("Ingrese la opcion deseada: \n"+ "\n".join(["%s: %s" % (i+1,cities[i]) for i in xrange(0,len(iate_codes))])+"\n").strip()
					index = int(index)
					if index < len(iate_codes) + 1 and index > 0:
						break
				except Exception:
					pass
			return iate_codes[index-1]
	else:
			return iate_codes[0]

def promt_date(prompt):
		fech = None
		while fech is None:
			try: 
				fech = raw_input(prompt+"( en formato YYYYMMDD)\n").strip()
				return datetime.datetime.strptime(fech,"%Y%m%d")
			except Exception,e:
				raise e
		
def parse_search_results(results):
				format_par = lambda x: x.strftime("%d/%m/%Y")
				res = []
				cheapest = None
				shortest = None
				for r in results:
					d= {}
					d["saliendo"] = format_par(datetime.datetime.fromtimestamp(float(r["Dep"][0]["DepDate"][6:-2]) / 1000 ))	
					d["arrivando"] = format_par(datetime.datetime.fromtimestamp(float(r["Arr"][-1]["DepDate"][6:-2])/ 1000 ))
					d['escalas']= len(r['Dep'][0]['Segmts'])
					d['numero'] = [j["FliNum"] for i in r['Dep'] for j in i["Segmts"]]
					d["compania"] = list(set([j["AirNam"] for i in r['Dep'] for j in i["Segmts"]]))
					d["precio"] = 99999999
					d["dest"] = r["Dep"][0]["ArrAirp"]["Desc"]
					for it in r["Itns"]:
						d["precio"] = min(it["Tot"]["NonLoc"],d["precio"])
					try:
						if d["precio"] < cheapest["precio"]:
							cheapest = d
					except:
						cheapest = d
					try:
						if d["escalas"] < shortest["escalas"]:
							shortest = d
					except:
						shortest = d
				return (cheapest,shortest)

def search_flight(**kwargs):
	format_url = lambda x: x.strftime("%Y-%m-%d") 
	urlVuelos = '/Flights.Services/Flights/Flights.svc/ClusteredFlights/%s/%s/%s/%s/1/0/0' % (kwargs.get("source","BUE"),kwargs["destination"],format_url(kwargs["dt_go"]),format_url(kwargs["dt_return"]))
	r = urllib2.Request("http://www.despegar.com.ar%s"%urlVuelos)
	r.add_header("User-Agent","Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11")
	f = urllib2.urlopen(r)
	data = json.loads(f.read())
	return data


def get_flights(**kwargs):
	dt_ida = kwargs.get("dt_ida",promt_date("Fecha de Partida"))
	dt_vuelta = kwargs.get("dt_vuelta",promt_date("Fecha de Vuelta"))
	delta_dt_ida = kwargs.get("delta_dt_ida",1)
	delta_dt_vuelta = kwargs.get("delta_dt_vuelta",180 if dt_vuelta is None else 1)

	ae_src = kwargs.get("source",None)
	if ae_src is None:
		ae_src = promt_airport("Ingrese Aeropuerto Origen")

	ae_dest = kwargs.get("destination",None)
	if ae_dest is None:
		ae_dest = promt_airport("Ingrese Aeropuerto Destino")
	ae_dest = ae_dest if type(ae_dest) == list else [ae_dest]

	silent = kwargs.get("silent",False)
	ebackoff = kwargs.get("backoff",False)

	actual = 0
	total = delta_dt_vuelta *  delta_dt_ida * (len(ae_dest) if type(ae_dest) == list else 1)
	vuelos = []	

	dt_vuelta = dt_vuelta if dt_vuelta != None else dt_ida + datetime.timedelta(delta_dt_vuelta)
	if dt_ida - dt_vuelta >= datetime.timedelta(330):
		dt_vuelta = dt_ida + datetime.timedelta(320)
	for i in xrange(0,delta_dt_ida):
		dt_vuelta_f =  dt_vuelta
		for k in xrange(0,delta_dt_vuelta):		 		
			for dest in ae_dest:
				avance = "%.2f %% completo" % ((actual*100) / float(total) )
				try:
	 				try:				
						args = {"source":ae_src, "destination":dest,"dt_go":dt_ida,"dt_return":dt_vuelta_f}					
						data = search_flight(**args)
						mtime = 10
					except Exception,e:
						if ebackoff:
							if not silent:
								print "Sleeping %s" % mtime
							time.sleep(random.randint(0,mtime))
							mtime = 2 * mtime					
						raise Exception("HTTP Error",e)
					cheapest,shortest = parse_search_results(data["Boxs"])
					vuelos.append((cheapest,shortest))
					log = open("%s/resultados.log" % localdir(),"a")
					if cheapest:
						log.write(json.dumps(cheapest)+"\n")
					if shortest:
						log.write(json.dumps(shortest)+"\n")
					log.close()
				except Exception, e:
					print e
				finally:
					actual += 1
					if not silent:
						print avance
				dt_vuelta_f = dt_vuelta_f - datetime.timedelta(1)
		dt_ida = dt_ida + datetime.timedelta(1)
	return vuelos

