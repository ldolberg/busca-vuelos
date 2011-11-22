for r in sorted(get_flights(),key=lambda x: x[0]["precio"])[0:5]:
	v = r[0]
	print "%s %s USD a %s el %s en %s escalas volviendo %s" % ("-".join(v["compania"]),v["precio"], v["dest"], v["saliendo"],v["escalas"]-1,v["arrivando"])
