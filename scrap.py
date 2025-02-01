from flask import Flask, render_template, request
import rdflib

app = Flask(__name__)

# Load RDF graphs
g = rdflib.Graph()
g.parse("si.ttl", format="ttl")
g.parse("quantities.ttl", format="ttl")  # Ensure the quantities.ttl file is included
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
                # Link to the `/resolution` page
                processed_results["Defining Constant"] = f'<a href="/resolution" target="_blank">{remove_url_prefix(obj)}</a>'
            elif "hasDefiningResolution" in pred:
                # Link to the `/resolution` page
                processed_results["Defining Resolution"] = f'<a href="/resolution" target="_blank">{remove_url_prefix(obj)}</a>'
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
    """Route to display 'Hello, World!'."""
    return render_template('resolution.html')


if __name__ == "__main__":
    app.run(debug=False)






# from flask import Flask, render_template, request
# import rdflib

# app = Flask(__name__)

# # Load RDF graphs
# g = rdflib.Graph()
# g.parse("si.ttl", format="ttl")
# g.parse("quantities.ttl", format="ttl")  # Ensure the quantities.ttl file is included
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
#                 processed_results["Defining Constant"] = remove_url_prefix(obj)
#             elif "hasDefiningResolution" in pred:
#                 # Link to the `/resolution` page
#                 processed_results["Defining Resolution"] = f'<a href="/resolution" target="_blank">{remove_url_prefix(obj)}</a>'
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
#     """Route to display 'Hello, World!'."""
#     return render_template('resolution.html')


# if __name__ == "__main__":
#     app.run(debug=False)






# from flask import Flask, render_template, request
# import rdflib

# app = Flask(__name__)

# # Load RDF graphs
# g = rdflib.Graph()
# g.parse("si.ttl", format="ttl")
# g.parse("quantities.ttl", format="ttl")  # Ensure the quantities.ttl file is included
# g.parse("decisions.ttl", format="ttl")
# g.parse("constants.ttl", format="ttl")
# g.parse("units.ttl", format="ttl")
# g.parse("prefixes.ttl", format="ttl")


# def remove_url_prefix(uri):
#     """Helper function to clean URL prefixes for display."""
#     return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]


# def process_as_hyperlink(obj, route=None):
#     """
#     Check if the object is a valid URL and return HTML anchor tag as string.
#     If a route is provided, it links to the specified route.
#     """
#     if obj.startswith("http://") or obj.startswith("https://"):
#         url = route if route else obj
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
#                 processed_results["Quantity"] = process_as_hyperlink(obj)
#             elif "hasDefiningConstant" in pred:
#                 processed_results["Defining Constant"] = process_as_hyperlink(obj)
#             elif "hasDefiningResolution" in pred:
#                 # Update to link to a new Flask route
#                 processed_results["Defining Resolution"] = process_as_hyperlink(obj, route="/resolution")
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
#     """Route to display 'Hello, World!'."""
#     return render_template('resolution.html')


# if __name__ == "__main__":
#     app.run(debug=False)







