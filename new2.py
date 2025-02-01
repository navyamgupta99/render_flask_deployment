+----------------------+
|      FlaskApp       |
|----------------------|
| +app: Flask         |
| +g: rdflib.Graph()  |
|----------------------|
| +index()            |
| +search()           |
| +resolution()       |
+----------------------+
          |
          | Uses
          v
+----------------------+
|      RDFGraph       |
|----------------------|
| +g: rdflib.Graph()  |
|----------------------|
| +parse(ttl_file)    |
| +query(sparql)      |
| +remove_url_prefix(uri) |
+----------------------+
          |
          | Generates
          v
+----------------------+
|      Templates      |
|----------------------|
| +index.html        |
| +results2.html     |
| +resolution.html   |
+----------------------+
