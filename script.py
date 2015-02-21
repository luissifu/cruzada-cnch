# -*- coding: utf-8 -*-
import re
import os
import codecs
import dryscrape
import urllib
import unicodecsv as csv
import StringIO
from bs4 import BeautifulSoup

def returnEstados():
    returnvalue = {}
    sess = dryscrape.Session(base_url = 'http://200.77.229.154:8080')
    sess.visit('ip_cnch/')

    workingbody = sess.body()

    soup = BeautifulSoup(workingbody)
    select_node = soup.findAll('select', attrs={'id': 'select_edo'})

    if select_node:
        for option in select_node[0].findAll('option'):
            value = option['value']
            text = option.text
            text = text.strip()
            returnvalue[value] = text

    returnvalue.pop("0")

    return returnvalue

def returnMunicipios(Entidad):
    returnvalue = []

    url = "http://200.77.229.154:8080/ip_cnch/municipios.jsp?cve_edo="+ Entidad + "&seccion_cnch=PAE"
    urllib.urlretrieve(url, filename="temp/server.csv")
    file_to_utf8("temp/server.csv","temp/server_utf8.csv")

    with open('temp/server_utf8.csv', 'rb') as csvfile:
        for line in csvfile:
            if not line:
                pass

            clean_line = re.sub(r' +\|', '\n', line)
            reader = csv.reader(StringIO.StringIO(clean_line.strip()), delimiter='|')

            for row in reader:
                returnvalue.append(row[0])

    return returnvalue

def returnLocalidades(municipio):
    returnvalue = []
    url = "http://200.77.229.154:8080/ip_cnch/localidades.jsp?cve_mpo=%s&seccion_cnch=PAE2" % municipio
    urllib.urlretrieve(url, filename="temp/server.csv")
    file_to_utf8("temp/server.csv","temp/server_utf8.csv")

    with open('temp/server_utf8.csv', 'rb') as csvfile:
        for line in csvfile:
            if not line:
                pass

            clean_line = re.sub(r' +\|', '\n', line)
            reader = csv.reader(StringIO.StringIO(clean_line.strip()), delimiter='|')

            for row in reader:
                returnvalue.append(row[0])

    return returnvalue

def writeinfo(localidad):# (keyEntidad, Entidad, Subsistema):
    #Visita la pagina de la tabla, virtualmente, y extrae el html de la pagina.
    placeholder = []

    url = "http://200.77.229.154:8080/ip_cnch/descarga_csv.jsp?cve_loc=%s&seccion_cnch=PAE" % localidad
    filename = "temp/localidad.csv"

    urllib.urlretrieve (url, filename)

    file_to_utf8("temp/localidad.csv", "temp/localidad_utf8.csv")

    with open('output_cruzada.csv', 'a') as outfile:
        with open('temp/localidad_utf8.csv') as infile:
            skipped = False
            for line in infile:
              if not skipped:
                  skipped = True
                  pass
              if not line or not line.strip():
                  pass
              outfile.write(line)

def file_to_utf8(source, target):
    # or some other, desired size in bytes
    BLOCKSIZE = 1048576
    with codecs.open(source, "r", "windows-1252") as sourceFile:
        with codecs.open(target, "w", "utf-8") as targetFile:
            while True:
                contents = sourceFile.read(BLOCKSIZE)
                if not contents:
                    break
                targetFile.write(contents)


# main
with open('output_cruzada.csv', 'a') as outfile:
    outfile.write('"No.","Clave Localidad","Nombre de la Localidad","Nombre del beneficiario","Primer Apellido","Segundo Apellido","Programas que lo atienden"')

print "Obteniendo lista de estados..."
Estados = returnEstados()
k = 1
k_max = len(Estados)
for keyEstado, Estado in Estados.iteritems():
    print "Obteniendo lista de municipios..."
    municipios = returnMunicipios(keyEstado)
    i = 1
    i_max = len(municipios)
    for municipio in municipios:
        print "Obteniendo lista de localidades..."
        localidades = returnLocalidades(municipio)
        j = 1
        j_max = len(localidades)
        for localidad in localidades:
            print "Obteniendo archivo del Estado %d/%d, Municipio %d/%d, Localidad %d/%d" % (k,k_max,i,i_max,j,j_max)
            writeinfo(localidad)
            j = j+1
        i = i+1
    k = k + 1
