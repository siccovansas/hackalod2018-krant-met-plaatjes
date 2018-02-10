#!/usr/bin/env python

from time import sleep
import shutil
import hashlib
import json
from pprint import pprint
import io

from SPARQLWrapper import SPARQLWrapper, JSON
import requests

# Retrieve all pages
sparql = SPARQLWrapper("http://lod.kb.nl/sparql")
sparql.setQuery("""
PREFIX dc: <http://purl.org/dc/elements/1.1/>
SELECT ?s, ?o, ?p
WHERE {
graph <http://lod.kb.nl/kranten/> {
 ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/dc/dcmitype/Text> .
 ?s <http://lod.kb.nl/ontology/largeImage> ?p.
}
} LIMIT 100
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
pprint(results)
print
print

for result in results["results"]["bindings"]:
    identifier = result['s']['value']
    print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    print identifier
    image = result['p']['value'].lstrip('http://resolver.kb.nl/resolve?urn=')


    # Retrieve all articles from a page
    sparql.setQuery("""
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    SELECT ?p
    WHERE {
    graph <http://lod.kb.nl/kranten/> {
     <%s> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/dc/dcmitype/Text> .
     <%s> <http://purl.org/dc/terms/hasPart> ?p.
    }
    } LIMIT 100
    """ % (identifier, identifier))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    pprint(results)
    print
    print
    
    articles = []
    for result in results["results"]["bindings"]:
        articles.append(result['p']['value'])
    
    
    # Retrieve title from article
    article_titles = []
    for article in articles:
        sparql.setQuery("""
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT ?p
        WHERE {
        graph <http://lod.kb.nl/kranten/> {
         <%s> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Article> .
         <%s> dc:title ?p.
        }
        } LIMIT 100
        """ % (article, article))
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        pprint(results)
        
        for result in results["results"]["bindings"]:
            article_titles.append(result['p']['value'])
    
    print article_titles
    
    print
    print
    
    with io.open('pages/%s.html' % (identifier.split('/')[-1]), 'w') as OUT:
        for article_title in article_titles:
            print article_title.split('.')[0]
            # FIX non asci query
            res = requests.post('http://api.opencultuurdata.nl/v0/search', data='{"query": "%s", "filters": {"media_content_type": {"terms": ["image/jpeg", "image/png"]}}}' % (article_title.split('.')[0]).encode('ascii', 'ignore')).json()
            for r in res['hits']['hits'][:1]:
                print r['_source']['title']
                if 'description' in r['_source']:
                    print r['_source']['description']
                if 'media_urls' in r['_source']:
                    print r['_source']['media_urls'][0]['url']
                    OUT.write(u'<div>')
                    OUT.write(u'<h1>Artikel titel: %s</h1>' % (article_title))
                    OUT.write(u'<br>')
                    OUT.write(u'<h1>Afbeelding titel: %s</h1>' % (r['_source']['title']))
                    OUT.write(u'<br>')
                    OUT.write(u'<img src="%s">' % r['_source']['media_urls'][0]['url'])
                    OUT.write(u'</div>\n')
                print '=================================='
                print '=================================='
        OUT.write(u'<img src="http://imageviewer.kb.nl/ImagingService/imagingService?&id=%s"?>' % (image))
