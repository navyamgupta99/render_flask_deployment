from flask import Flask, render_template, request
import rdflib

app = Flask(__name__)

# Load RDF graphs
g = rdflib.Graph()
g.parse("si.ttl", format="ttl")
g.parse("quantities.ttl", format="ttl")
g.parse("decisions.ttl", format="ttl")
g.parse("constants.ttl", format="ttl")
g.parse("units.ttl", format="ttl")
g.parse("prefixes.ttl", format="ttl")


def remove_url_prefix(uri):
    """Helper function to clean URL prefixes for display."""
    return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    si_unit = request.form.get('si_unit', '').strip().lower()

    try:
        # SPARQL query to fetch relevant data
        query = f"""
        SELECT ?subj ?pred ?obj
        WHERE {{
            ?subj ?pred ?obj .
            FILTER(
                CONTAINS(LCASE(STR(?subj)), "{si_unit}") || 
                CONTAINS(LCASE(STR(?obj)), "{si_unit}")
            ) .
            FILTER (?pred IN (
                <https://si-digital-framework.org/SI#hasSymbol>,
                <https://si-digital-framework.org/SI#hasQuantity>,
                <https://si-digital-framework.org/SI#hasDefiningConstant>,
                <https://si-digital-framework.org/SI#hasDefiningResolution>,
                <https://si-digital-framework.org/SI#hasUnitTypeAsString>,
                <https://si-digital-framework.org/SI#hasUnit>,
                <https://si-digital-framework.org/SI#hasDefiningEquation>
            ))
        }}
        """
        
        # Execute the query on the graph
        results = g.query(query)

        # Initialize the processed results dictionary
        processed_results = {
            "Unit": None,
            "Symbol": None,
            "Quantity": None,
            "Defining Constant": None,
            "Defining Resolution": None,
            "Unit Type": None,
            "Defining Equation": None
        }

        # Process the query results
        for result in results:
            subj = str(result[0])
            pred = str(result[1])
            obj = str(result[2])

            if "hasSymbol" in pred:
                processed_results["Symbol"] = remove_url_prefix(obj)
            elif "hasQuantity" in pred:
                processed_results["Quantity"] = remove_url_prefix(obj)
            elif "hasDefiningConstant" in pred:
                # Link to the /resolution page with query parameter
                processed_results["Defining Constant"] = f'<a href="/resolution?value={obj}" target="_blank">{remove_url_prefix(obj)}</a>'
            elif "hasDefiningResolution" in pred:
                # Link to the /resolution page with query parameter
                processed_results["Defining Resolution"] = f'<a href="/resolution?value={obj}" target="_blank">{remove_url_prefix(obj)}</a>'
            elif "hasUnitTypeAsString" in pred:
                processed_results["Unit Type"] = remove_url_prefix(obj)
            elif "hasUnit" in pred:
                processed_results["Unit"] = remove_url_prefix(obj)
            elif "hasDefiningEquation" in pred:
                processed_results["Defining Equation"] = obj.strip()  # Keep as plain text for MathJax rendering

        # If no data is found, return a message
        if all(value is None for value in processed_results.values()):
            message = f"No information found for SI unit: {si_unit}"
            return render_template('results2.html', si_unit=si_unit, results=None, message=message)

        # Render the results
        return render_template('results2.html', si_unit=si_unit, results=processed_results, message=None)

    except Exception as e:
        print(f"Error during query execution: {e}")
        return f"An error occurred: {e}"


@app.route('/resolution')
def resolution():
    """Route to display information about the selected value (object)."""
    # Get the object value from the query parameter
    obj_value = request.args.get('value', '').strip()

    if not obj_value:
        return render_template('resolution.html', heading="No Value Provided", data=[])

    try:
        # SPARQL query to fetch information about the object from constants.ttl
        query = f"""
        SELECT ?pred ?obj
        WHERE {{
            <{obj_value}> ?pred ?obj .
        }}
        """
        results = g.query(query)

        # Process the query results into a list of dictionaries
        data = [{"Predicate": remove_url_prefix(str(row[0])), "Object": remove_url_prefix(str(row[1]))} for row in results]

        # Set the heading to the object's value
        heading = f"Information about: {remove_url_prefix(obj_value)}"

        # If no data is found, return a message
        if not data:
            heading = f"No information found for {remove_url_prefix(obj_value)}"
            return render_template('resolution.html', heading=heading, data=[])

        # Render the resolution.html template with the data
        return render_template('resolution.html', heading=heading, data=data)

    except Exception as e:
        print(f"Error querying RDF data: {e}")
        return render_template('resolution.html', heading="Error Occurred", data=[])


if __name__ == "__main__":
    app.run(debug=False)  









# from flask import Flask, render_template, request
# import rdflib

# app = Flask(__name__)

# # Load RDF graphs
# g = rdflib.Graph()
# g.parse("si.ttl", format="ttl")
# g.parse("quantities.ttl", format="ttl")
# g.parse("decisions.ttl", format="ttl")
# g.parse("constants.ttl", format="ttl")
# g.parse("units.ttl", format="ttl")
# g.parse("prefixes.ttl", format="ttl")


# def remove_url_prefix(uri):
#     """Helper function to clean URL prefixes for display."""
#     return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]


# @app.route('/')
# def index():
#     """Render the index page."""
#     return render_template('index.html')


# @app.route('/search', methods=['POST'])
# def search():
#     """Handle the search form and display results."""
#     si_unit = request.form.get('si_unit', '').strip().lower()

#     try:
#         # SPARQL query to fetch relevant data
#         query = f"""
#         SELECT ?subj ?pred ?obj
#         WHERE {{
#             ?subj ?pred ?obj .
#             FILTER(
#                 CONTAINS(LCASE(STR(?subj)), "{si_unit}") || 
#                 CONTAINS(LCASE(STR(?obj)), "{si_unit}")
#             ) .
#             FILTER (?pred IN (
#                 <https://si-digital-framework.org/SI#hasSymbol>,
#                 <https://si-digital-framework.org/SI#hasQuantity>,
#                 <https://si-digital-framework.org/SI#hasDefiningConstant>,
#                 <https://si-digital-framework.org/SI#hasDefiningResolution>,
#                 <https://si-digital-framework.org/SI#hasUnitTypeAsString>,
#                 <https://si-digital-framework.org/SI#hasUnit>,
#                 <https://si-digital-framework.org/SI#hasDefiningEquation>
#             ))
#         }}
#         """
#         results = g.query(query)

#         # Initialize the processed results dictionary
#         processed_results = {}

#         # Process the query results
#         for result in results:
#             pred = remove_url_prefix(str(result[1]))
#             obj = remove_url_prefix(str(result[2]))
#             if "hasDefiningConstant" in pred:
#                 # Make Defining Constant clickable
#                 processed_results[pred] = f'<a href="/resolution?value={result[2]}" target="_blank">{obj}</a>'
#             else:
#                 processed_results[pred] = obj

#         # If no data is found, return a message
#         if not processed_results:
#             message = f"No information found for SI unit: {si_unit}"
#             return render_template('results2.html', si_unit=si_unit, results=None, message=message)

#         # Render the results
#         return render_template('results2.html', si_unit=si_unit, results=processed_results, message=None)

#     except Exception as e:
#         print(f"Error during query execution: {e}")
#         return f"An error occurred: {e}"


# @app.route('/resolution')
# def resolution():
#     """Display specific attributes for the selected value (object)."""
#     # Get the object value from the query parameter
#     obj_value = request.args.get('value', '').strip()

#     if not obj_value:
#         return render_template('resolution.html', heading="No Value Provided", data=[])

#     try:
#         # SPARQL query to fetch only the required attributes
#         query = f"""
#         SELECT ?pred ?obj
#         WHERE {{
#             <{obj_value}> ?pred ?obj .
#             FILTER (?pred IN (
#                 <https://si-digital-framework.org/SI#hasValueAsString>,
#                 <https://si-digital-framework.org/SI#hasUpdatedDate>,
#                 <https://si-digital-framework.org/SI#hasSymbol>,
#                 <https://si-digital-framework.org/SI#hasUnit>,
#                 <http://www.w3.org/2004/02/skos/core#prefLabel>
#             ))
#         }}
#         """
#         results = g.query(query)

#         # Process the query results into a list of dictionaries
#         data = [{"Attribute": remove_url_prefix(str(row[0])), "Value": remove_url_prefix(str(row[1]))} for row in results]

#         # Set the heading to the object's value
#         heading = f"Information about: {remove_url_prefix(obj_value)}"

#         # If no data is found, return a message
#         if not data:
#             heading = f"No information found for {remove_url_prefix(obj_value)}"
#             return render_template('resolution.html', heading=heading, data=[])

#         # Render the resolution.html template with the data
#         return render_template('resolution.html', heading=heading, data=data)

#     except Exception as e:
#         print(f"Error querying RDF data: {e}")
#         return render_template('resolution.html', heading="Error Occurred", data=[])










# from flask import Flask, render_template, request
# import rdflib

# app = Flask(__name__)

# # Load RDF graphs
# g = rdflib.Graph()
# g.parse("si.ttl", format="ttl")
# g.parse("quantities.ttl", format="ttl")
# g.parse("decisions.ttl", format="ttl")
# g.parse("constants.ttl", format="ttl")
# g.parse("units.ttl", format="ttl")
# g.parse("prefixes.ttl", format="ttl")


# def remove_url_prefix(uri):
#     """Helper function to clean URL prefixes for display."""
#     return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]


# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/search', methods=['POST'])
# def search():
#     si_unit = request.form.get('si_unit', '').strip().lower()

#     try:
#         # SPARQL query to fetch relevant data
#         query = f"""
#         SELECT ?subj ?pred ?obj
#         WHERE {{
#             ?subj ?pred ?obj .
#             FILTER(
#                 CONTAINS(LCASE(STR(?subj)), "{si_unit}") || 
#                 CONTAINS(LCASE(STR(?obj)), "{si_unit}")
#             ) .
#             FILTER (?pred IN (
#                 <https://si-digital-framework.org/SI#hasSymbol>,
#                 <https://si-digital-framework.org/SI#hasQuantity>,
#                 <https://si-digital-framework.org/SI#hasDefiningConstant>,
#                 <https://si-digital-framework.org/SI#hasDefiningResolution>,
#                 <https://si-digital-framework.org/SI#hasUnitTypeAsString>,
#                 <https://si-digital-framework.org/SI#hasUnit>,
#                 <https://si-digital-framework.org/SI#hasDefiningEquation>
#             ))
#         }}
#         """
        
#         # Execute the query on the graph
#         results = g.query(query)

#         # Initialize the processed results dictionary
#         processed_results = {
#             "Unit": None,
#             "Symbol": None,
#             "Quantity": None,
#             "Defining Constant": None,
#             "Defining Resolution": None,
#             "Unit Type": None,
#             "Defining Equation": None
#         }

#         # Process the query results
#         for result in results:
#             subj = str(result[0])
#             pred = str(result[1])
#             obj = str(result[2])

#             if "hasSymbol" in pred:
#                 processed_results["Symbol"] = remove_url_prefix(obj)
#             elif "hasQuantity" in pred:
#                 processed_results["Quantity"] = remove_url_prefix(obj)
#             elif "hasDefiningConstant" in pred:
#                 # Link to the `/resolution` page with query parameter
#                 processed_results["Defining Constant"] = f'<a href="/resolution?value={obj}" target="_blank">{remove_url_prefix(obj)}</a>'
#             elif "hasDefiningResolution" in pred:
#                 # Link to the `/resolution` page with query parameter
#                 processed_results["Defining Resolution"] = f'<a href="/resolution?value={obj}" target="_blank">{remove_url_prefix(obj)}</a>'
#             elif "hasUnitTypeAsString" in pred:
#                 processed_results["Unit Type"] = remove_url_prefix(obj)
#             elif "hasUnit" in pred:
#                 processed_results["Unit"] = remove_url_prefix(obj)
#             elif "hasDefiningEquation" in pred:
#                 processed_results["Defining Equation"] = obj.strip()  # Keep as plain text for MathJax rendering

#         # If no data is found, return a message
#         if all(value is None for value in processed_results.values()):
#             message = f"No information found for SI unit: {si_unit}"
#             return render_template('results2.html', si_unit=si_unit, results=None, message=message)

#         # Render the results
#         return render_template('results2.html', si_unit=si_unit, results=processed_results, message=None)

#     except Exception as e:
#         print(f"Error during query execution: {e}")
#         return f"An error occurred: {e}"


# @app.route('/resolution')
# def resolution():
#     """Route to display information about the selected value (object)."""
#     # Get the object value from the query parameter
#     obj_value = request.args.get('value', '').strip()

#     if not obj_value:
#         return render_template('resolution.html', heading="No Value Provided", data=[])

#     try:
#         # SPARQL query to fetch information about the object from constants.ttl
#         query = f"""
#         SELECT ?pred ?obj
#         WHERE {{
#             <{obj_value}> ?pred ?obj .
#         }}
#         """
#         results = g.query(query)

#         # Process the query results into a list of dictionaries
#         data = [{"Predicate": remove_url_prefix(str(row[0])), "Object": remove_url_prefix(str(row[1]))} for row in results]

#         # Set the heading to the object's value
#         heading = f"Information about: {remove_url_prefix(obj_value)}"

#         # If no data is found, return a message
#         if not data:
#             heading = f"No information found for {remove_url_prefix(obj_value)}"
#             return render_template('resolution.html', heading=heading, data=[])

#         # Render the resolution.html template with the data
#         return render_template('resolution.html', heading=heading, data=data)

#     except Exception as e:
#         print(f"Error querying RDF data: {e}")
#         return render_template('resolution.html', heading="Error Occurred", data=[])


# if __name__ == "__main__":
#     app.run(debug=False)




# from flask import Flask, render_template, request
# import rdflib

# app = Flask(__name__)

# # Load RDF graphs
# g = rdflib.Graph()
# g.parse("si.ttl", format="ttl")
# g.parse("quantities.ttl", format="ttl")
# g.parse("decisions.ttl", format="ttl")
# g.parse("constants.ttl", format="ttl")
# g.parse("units.ttl", format="ttl")
# g.parse("prefixes.ttl", format="ttl")


# def remove_url_prefix(uri):
#     """Helper function to clean URL prefixes for display."""
#     return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]


# def process_as_hyperlink(obj):
#     """
#     Check if the object is a valid URL and return HTML anchor tag as string.
#     """
#     if obj.startswith("http://") or obj.startswith("https://"):
#         url = obj
#         display = remove_url_prefix(obj)
#         return f'<a href="{url}" target="_blank">{display}</a>'
#     else:
#         return remove_url_prefix(obj)


# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/search', methods=['POST'])
# def search():
#     si_unit = request.form.get('si_unit', '').strip().lower()

#     try:
#         # SPARQL query to fetch relevant data
#         query = f"""
#         SELECT ?subj ?pred ?obj
#         WHERE {{
#             ?subj ?pred ?obj .
#             FILTER(
#                 CONTAINS(LCASE(STR(?subj)), "{si_unit}") || 
#                 CONTAINS(LCASE(STR(?obj)), "{si_unit}")
#             ) .
#             FILTER (?pred IN (
#                 <https://si-digital-framework.org/SI#hasSymbol>,
#                 <https://si-digital-framework.org/SI#hasQuantity>,
#                 <https://si-digital-framework.org/SI#hasDefiningConstant>,
#                 <https://si-digital-framework.org/SI#hasDefiningResolution>,
#                 <https://si-digital-framework.org/SI#hasUnitTypeAsString>,
#                 <https://si-digital-framework.org/SI#hasUnit>,
#                 <https://si-digital-framework.org/SI#hasDefiningEquation>
#             ))
#         }}
#         """
#         results = g.query(query)

#         # Initialize the processed results
#         processed_results = {
#             "Unit": None,
#             "Symbol": None,
#             "Quantity": None,
#             "Defining Constant": None,
#             "Defining Resolution": None,
#             "Unit Type": None,
#             "Defining Equation": None
#         }

#         # Process the query results
#         for result in results:
#             subj = str(result[0])
#             pred = str(result[1])
#             obj = str(result[2])

#             if "hasSymbol" in pred:
#                 processed_results["Symbol"] = remove_url_prefix(obj)
#             elif "hasQuantity" in pred:
#                 processed_results["Quantity"] = process_as_hyperlink(obj)
#             elif "hasDefiningConstant" in pred:
#                 processed_results["Defining Constant"] = process_as_hyperlink(obj)
#             elif "hasDefiningResolution" in pred:
#                 processed_results["Defining Resolution"] = process_as_hyperlink(obj)
#             elif "hasUnitTypeAsString" in pred:
#                 processed_results["Unit Type"] = remove_url_prefix(obj)
#             elif "hasUnit" in pred:
#                 processed_results["Unit"] = remove_url_prefix(obj)
#             elif "hasDefiningEquation" in pred:
#                 # Pass LaTeX directly for MathJax rendering
#                 processed_results["Defining Equation"] = obj.strip()

#         # If no data is found, return a message
#         if all(value is None for value in processed_results.values()):
#             message = f"No information found for SI unit: {si_unit}"
#             return render_template('results2.html', si_unit=si_unit, results=None, message=message)

#         # Render the results
#         return render_template('results2.html', si_unit=si_unit, results=processed_results, message=None)

#     except Exception as e:
#         print(f"Error during query execution: {e}")
#         return f"An error occurred: {e}"


# if __name__ == "__main__":
#     app.run(debug=False)







# from flask import Flask, render_template, request
# import rdflib

# app = Flask(__name__)

# # Load RDF graphs
# g = rdflib.Graph()
# g.parse("si.ttl", format="ttl")
# g.parse("quantities.ttl", format="ttl")
# g.parse("decisions.ttl", format="ttl")
# g.parse("constants.ttl", format="ttl")
# g.parse("units.ttl", format="ttl")
# g.parse("prefixes.ttl", format="ttl")


# def remove_url_prefix(uri):
#     """Helper function to clean URL prefixes for display."""
#     return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]


# def process_as_hyperlink(obj):
#     """
#     Check if the object is a valid URL and return hyperlink details.
#     """
#     if obj.startswith("http://") or obj.startswith("https://"):
#         return {
#             "type": "link",
#             "url": obj,
#             "display": remove_url_prefix(obj)
#         }
#     else:
#         return {
#             "type": "text",
#             "display": remove_url_prefix(obj)
#         }


# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/search', methods=['POST'])
# def search():
#     si_unit = request.form.get('si_unit', '').strip().lower()

#     try:
#         # SPARQL query to fetch relevant data
#         query = f"""
#         SELECT ?subj ?pred ?obj
#         WHERE {{
#             ?subj ?pred ?obj .
#             FILTER(
#                 CONTAINS(LCASE(STR(?subj)), "{si_unit}") || 
#                 CONTAINS(LCASE(STR(?obj)), "{si_unit}")
#             ) .
#             FILTER (?pred IN (
#                 <https://si-digital-framework.org/SI#hasSymbol>,
#                 <https://si-digital-framework.org/SI#hasQuantity>,
#                 <https://si-digital-framework.org/SI#hasDefiningConstant>,
#                 <https://si-digital-framework.org/SI#hasDefiningResolution>,
#                 <https://si-digital-framework.org/SI#hasUnitTypeAsString>,
#                 <https://si-digital-framework.org/SI#hasUnit>,
#                 <https://si-digital-framework.org/SI#hasDefiningEquation>
#             ))
#         }}
#         """
#         results = g.query(query)

#         # Initialize the processed results
#         processed_results = {
#             "Unit": None,
#             "Symbol": None,
#             "Quantity": None,
#             "Defining Constant": None,
#             "Defining Resolution": None,
#             "Unit Type": None,
#             "Defining Equation": None
#         }

#         # Process the query results
#         for result in results:
#             subj = str(result[0])
#             pred = str(result[1])
#             obj = str(result[2])

#             if "hasSymbol" in pred:
#                 processed_results["Symbol"] = remove_url_prefix(obj)
#             elif "hasQuantity" in pred:
#                 processed_results["Quantity"] = process_as_hyperlink(obj)
#             elif "hasDefiningConstant" in pred:
#                 processed_results["Defining Constant"] = process_as_hyperlink(obj)
#             elif "hasDefiningResolution" in pred:
#                 processed_results["Defining Resolution"] = process_as_hyperlink(obj)
#             elif "hasUnitTypeAsString" in pred:
#                 processed_results["Unit Type"] = remove_url_prefix(obj)
#             elif "hasUnit" in pred:
#                 processed_results["Unit"] = remove_url_prefix(obj)
#             elif "hasDefiningEquation" in pred:
#                 processed_results["Defining Equation"] = obj  # Keep as plain text for MathJax rendering

#         # If no data is found, return a message
#         if all(value is None for value in processed_results.values()):
#             message = f"No information found for SI unit: {si_unit}"
#             return render_template('results.html', si_unit=si_unit, results=None, message=message)

#         # Render the results
#         return render_template('results.html', si_unit=si_unit, results=processed_results, message=None)

#     except Exception as e:
#         print(f"Error during query execution: {e}")
#         return f"An error occurred: {e}"


# if __name__ == "__main__":
#     app.run(debug=False)





# from flask import Flask, render_template, request
# import rdflib

# app = Flask(__name__)

# # Load RDF graphs
# g = rdflib.Graph()
# g.parse("si.ttl", format="ttl")
# g.parse("quantities.ttl", format="ttl")
# g.parse("decisions.ttl", format="ttl")
# g.parse("constants.ttl", format="ttl")
# g.parse("units.ttl", format="ttl")
# g.parse("prefixes.ttl", format="ttl")


# def remove_url_prefix(uri):
#     """Helper function to clean URL prefixes for display."""
#     return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]


# def process_as_hyperlink(obj):
#     """
#     Check if the object is a valid URL and return hyperlink details.
#     """
#     if obj.startswith("http://") or obj.startswith("https://"):
#         return {
#             "type": "link",
#             "url": obj,
#             "display": remove_url_prefix(obj)
#         }
#     else:
#         return {
#             "type": "text",
#             "display": remove_url_prefix(obj)
#         }


# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/search', methods=['POST'])
# def search():
#     si_unit = request.form.get('si_unit', '').strip().lower()

#     try:
#         query = f"""
#         SELECT ?subj ?pred ?obj
#         WHERE {{
#             ?subj ?pred ?obj .
#             FILTER(
#                 CONTAINS(LCASE(STR(?subj)), "{si_unit}") || 
#                 CONTAINS(LCASE(STR(?obj)), "{si_unit}")
#             ) .
#             FILTER (?pred IN (
#                 <https://si-digital-framework.org/SI#hasSymbol>,
#                 <https://si-digital-framework.org/SI#hasQuantity>,
#                 <https://si-digital-framework.org/SI#hasDefiningConstant>,
#                 <https://si-digital-framework.org/SI#hasDefiningResolution>,
#                 <https://si-digital-framework.org/SI#hasUnitTypeAsString>,
#                 <https://si-digital-framework.org/SI#hasUnit>,
#                 <https://si-digital-framework.org/SI#hasDefiningEquation>
#             ))
#         }}
#         """
#         results = g.query(query)

#         processed_results = {
#             "Unit": None,
#             "Symbol": None,
#             "Quantity": None,
#             "Defining Constant": None,
#             "Defining Resolution": None,
#             "Unit Type": None,
#             "Defining Equation": None
#         }

#         for result in results:
#             subj = str(result[0])
#             pred = str(result[1])
#             obj = str(result[2])

#             if "hasSymbol" in pred:
#                 processed_results["Symbol"] = remove_url_prefix(obj)
#             elif "hasQuantity" in pred:
#                 # Parse Quantity as a hyperlink
#                 processed_results["Quantity"] = process_as_hyperlink(obj)
#             elif "hasDefiningConstant" in pred:
#                 # Parse Defining Constant as a hyperlink
#                 processed_results["Defining Constant"] = process_as_hyperlink(obj)
#             elif "hasDefiningResolution" in pred:
#                 # Parse Defining Resolution as a hyperlink
#                 processed_results["Defining Resolution"] = process_as_hyperlink(obj)
#             elif "hasUnitTypeAsString" in pred:
#                 processed_results["Unit Type"] = remove_url_prefix(obj)
#             elif "hasUnit" in pred:
#                 processed_results["Unit"] = remove_url_prefix(obj)
#             elif "hasDefiningEquation" in pred:
#                 processed_results["Defining Equation"] = obj  # Keep as plain text for MathJax rendering

#         if all(value is None for value in processed_results.values()):
#             message = f"No information found for SI unit: {si_unit}"
#             return render_template('results2.html', si_unit=si_unit, results=None, message=message)

#         return render_template('results2.html', si_unit=si_unit, results=processed_results, message=None)

#     except Exception as e:
#         print(f"Error during query execution: {e}")
#         return f"An error occurred: {e}"


# if __name__ == "__main__":
#     app.run(debug=False)







# from flask import Flask, render_template, request
# import rdflib

# app = Flask(__name__)

# # Load RDF graphs
# g = rdflib.Graph()
# g.parse("si.ttl", format="ttl")
# g.parse("quantities.ttl", format="ttl")
# g.parse("decisions.ttl", format="ttl")
# g.parse("constants.ttl", format="ttl")
# g.parse("units.ttl", format="ttl")
# g.parse("prefixes.ttl", format="ttl")


# def remove_url_prefix(uri):
#     """Helper function to clean URL prefixes for display."""
#     return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]


# def process_as_hyperlink(obj):
#     """
#     Check if the object is a valid URL and return hyperlink details.
#     """
#     if obj.startswith("http://") or obj.startswith("https://"):
#         return {
#             "type": "link",
#             "url": obj,
#             "display": remove_url_prefix(obj)
#         }
#     else:
#         return {
#             "type": "text",
#             "display": remove_url_prefix(obj)
#         }


# def process_defining_equation(equation):
#     """
#     Prepares the defining equation for LaTeX rendering.
#     """
#     # Replace LaTeX special characters with proper formatting
#     equation = equation.replace("\\", "\\\\")  # Escape backslashes
#     equation = equation.replace("{", "\\{").replace("}", "\\}")  # Escape braces
#     return equation


# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/search', methods=['POST'])
# def search():
#     si_unit = request.form.get('si_unit', '').strip().lower()

#     try:
#         query = f"""
#         SELECT ?subj ?pred ?obj
#         WHERE {{
#             ?subj ?pred ?obj .
#             FILTER(
#                 CONTAINS(LCASE(STR(?subj)), "{si_unit}") || 
#                 CONTAINS(LCASE(STR(?obj)), "{si_unit}")
#             ) .
#             FILTER (?pred IN (
#                 <https://si-digital-framework.org/SI#hasSymbol>,
#                 <https://si-digital-framework.org/SI#hasQuantity>,
#                 <https://si-digital-framework.org/SI#hasDefiningConstant>,
#                 <https://si-digital-framework.org/SI#hasDefiningResolution>,
#                 <https://si-digital-framework.org/SI#hasUnitTypeAsString>,
#                 <https://si-digital-framework.org/SI#hasUnit>,
#                 <https://si-digital-framework.org/SI#hasDefiningEquation>
#             ))
#         }}
#         """
#         results = g.query(query)

#         processed_results = {
#             "Unit": None,
#             "Symbol": None,
#             "Quantity": None,
#             "Defining Constant": None,
#             "Defining Resolution": None,
#             "Unit Type": None,
#             "Defining Equation": None
#         }

#         for result in results:
#             subj = str(result[0])
#             pred = str(result[1])
#             obj = str(result[2])

#             if "hasSymbol" in pred:
#                 processed_results["Symbol"] = remove_url_prefix(obj)
#             elif "hasQuantity" in pred:
#                 processed_results["Quantity"] = remove_url_prefix(obj)
#             elif "hasDefiningConstant" in pred:
#                 # Parse Defining Constant as a hyperlink
#                 processed_results["Defining Constant"] = process_as_hyperlink(obj)
#             elif "hasDefiningResolution" in pred:
#                 # Parse Defining Resolution as a hyperlink
#                 processed_results["Defining Resolution"] = process_as_hyperlink(obj)
#             elif "hasUnitTypeAsString" in pred:
#                 processed_results["Unit Type"] = remove_url_prefix(obj)
#             elif "hasUnit" in pred:
#                 processed_results["Unit"] = remove_url_prefix(obj)
#             elif "hasDefiningEquation" in pred:
#                 # Process defining equation for LaTeX rendering
#                 processed_results["Defining Equation"] = process_defining_equation(obj)

#         if all(value is None for value in processed_results.values()):
#             message = f"No information found for SI unit: {si_unit}"
#             return render_template('results2.html', si_unit=si_unit, results=None, message=message)

#         return render_template('results2.html', si_unit=si_unit, results=processed_results, message=None)

#     except Exception as e:
#         print(f"Error during query execution: {e}")
#         return f"An error occurred: {e}"


# if __name__ == "__main__":
#     app.run(debug=False)





# from flask import Flask, render_template, request
# import rdflib

# app = Flask(__name__)

# # Load RDF graphs
# g = rdflib.Graph()
# g.parse("quantities.ttl", format="ttl")  # Focus on quantities.ttl

# def remove_url_prefix(uri):
#     """Helper function to clean URL prefixes for display."""
#     return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]


# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/search', methods=['POST'])
# def search():
#     si_unit = request.form.get('si_unit', '').strip().lower()

#     try:
#         # Adjusted SPARQL query to focus on data from quantities.ttl
#         query = f"""
#         SELECT ?subj ?pred ?obj
#         WHERE {{
#             ?subj ?pred ?obj .
#             FILTER(
#                 CONTAINS(LCASE(STR(?subj)), "{si_unit}") || 
#                 CONTAINS(LCASE(STR(?obj)), "{si_unit}")
#             ) .
#             FILTER (?pred IN (
#                 <https://si-digital-framework.org/SI#hasSymbol>,
#                 <https://si-digital-framework.org/SI#hasQuantity>,
#                 <https://si-digital-framework.org/SI#hasUnit>,
#                 <https://si-digital-framework.org/SI#hasDefiningEquation>,
#                 <https://si-digital-framework.org/SI#hasDescription>
#             ))
#         }}
#         """
#         results = g.query(query)

#         results_list = []
#         for result in results:
#             subj = remove_url_prefix(str(result[0]))
#             pred = remove_url_prefix(str(result[1]))
#             obj = remove_url_prefix(str(result[2]))

#             results_list.append({
#                 "Subject": subj,
#                 "Predicate": pred,
#                 "Object": obj
#             })

#         if not results_list:
#             message = f"No information found for SI unit or term: {si_unit}"
#             return render_template('results.html', si_unit=si_unit, results=None, message=message)

#         return render_template('results.html', si_unit=si_unit, results=results_list, message=None)

#     except Exception as e:
#         print(f"Error during query execution: {e}")
#         return f"An error occurred: {e}"


# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=8080, debug=False)





# from flask import Flask, render_template, request
# import rdflib

# app = Flask(__name__)

# # Load RDF graphs
# g = rdflib.Graph()
# g.parse("si.ttl", format="ttl")
# g.parse("quantities.ttl", format="ttl")
# g.parse("decisions.ttl", format="ttl")
# g.parse("constants.ttl", format="ttl")
# g.parse("units.ttl", format="ttl")
# g.parse("prefixes.ttl", format="ttl")


# def remove_url_prefix(uri):
#     """Helper function to clean URL prefixes for display."""
#     return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]


# @app.route('/')
# def index():
#     return render_template('index.html')

# def process_defining_equation(equation):
#     """
#     Prepares the defining equation for LaTeX rendering.
#     """
#     # Replace LaTeX special characters with proper formatting
#     equation = equation.replace("\\", "\\\\")  # Escape backslashes
#     equation = equation.replace("{", "\\{").replace("}", "\\}")  # Escape braces
#     return equation


# @app.route('/search', methods=['POST'])
# def search():
#     si_unit = request.form.get('si_unit', '').strip().lower()

#     try:
#         query = f"""
#         SELECT ?subj ?pred ?obj
#         WHERE {{
#             ?subj ?pred ?obj .
#             FILTER(
#                 CONTAINS(LCASE(STR(?subj)), "{si_unit}") || 
#                 CONTAINS(LCASE(STR(?obj)), "{si_unit}")
#             ) .
#             FILTER (?pred IN (
#                 <https://si-digital-framework.org/SI#hasSymbol>,
#                 <https://si-digital-framework.org/SI#hasQuantity>,
#                 <https://si-digital-framework.org/SI#hasDefiningConstant>,
#                 <https://si-digital-framework.org/SI#hasDefiningResolution>,
#                 <https://si-digital-framework.org/SI#hasUnitTypeAsString>,
#                 <https://si-digital-framework.org/SI#hasUnit>,
#                 <https://si-digital-framework.org/SI#hasDefiningEquation>
#             ))
#         }}
#         """
#         results = g.query(query)

#         processed_results = {
#             "Unit": None,
#             "Symbol": None,
#             "Quantity": None,
#             "Defining Constant": None,
#             "Defining Resolution": None,
#             "Unit Type": None,
#             "Defining Equation": None
#         }

#         for result in results:

#             subj = str(result[0])
#             pred = str(result[1])
#             obj = str(result[2])

#             if "hasSymbol" in pred:
#                 processed_results["Symbol"] = remove_url_prefix(obj)
#             elif "hasQuantity" in pred:
#                 processed_results["Quantity"] = remove_url_prefix(obj)
#             elif "hasDefiningConstant" in pred:
#                 processed_results["Defining Constant"] = remove_url_prefix(obj)
#             elif "hasDefiningResolution" in pred:
#                 processed_results["Defining Resolution"] = remove_url_prefix(obj)
#             elif "hasUnitTypeAsString" in pred:
#                 processed_results["Unit Type"] = remove_url_prefix(obj)
#             elif "hasUnit" in pred:
#                 processed_results["Unit"] = remove_url_prefix(obj)
#             elif "hasDefiningEquation" in pred:
#                 # Process equation for LaTeX rendering
#                 processed_results["Defining Equation"] = process_defining_equation(obj)

#         if all(value is None for value in processed_results.values()):
#             message = f"No information found for SI unit: {si_unit}"
#             return render_template('results.html', si_unit=si_unit, results=None, message=message)

#         return render_template('results.html', si_unit=si_unit, results=processed_results, message=None)

#     except Exception as e:
#         print(f"Error during query execution: {e}")
#         return f"An error occurred: {e}"


# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=8080, debug=False)