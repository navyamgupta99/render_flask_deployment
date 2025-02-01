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


def process_as_hyperlink(obj, route=None):
    """Check if the object is a valid URL and return HTML anchor tag as string."""
    if route:
        return f'<a href="{route}?value={obj}" target="_blank">{remove_url_prefix(obj)}</a>'
    elif obj.startswith("http://") or obj.startswith("https://"):
        return f'<a href="{obj}" target="_blank">{remove_url_prefix(obj)}</a>'
    else:
        return remove_url_prefix(obj)


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
        results = g.query(query)

        # Initialize the processed results
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
                processed_results["Quantity"] = process_as_hyperlink(obj, route="/quantity_details")
            elif "hasDefiningConstant" in pred:
                processed_results["Defining Constant"] = process_as_hyperlink(obj)
            elif "hasDefiningResolution" in pred:
                processed_results["Defining Resolution"] = process_as_hyperlink(obj)
            elif "hasUnitTypeAsString" in pred:
                processed_results["Unit Type"] = remove_url_prefix(obj)
            elif "hasUnit" in pred:
                processed_results["Unit"] = remove_url_prefix(obj)
            elif "hasDefiningEquation" in pred:
                processed_results["Defining Equation"] = obj  # Keep as plain text for MathJax rendering

        # Debugging output
        print(f"Processed Results: {processed_results}")

        # If no data is found, return a message
        if all(value is None for value in processed_results.values()):
            message = f"No information found for SI unit: {si_unit}"
            return render_template('results2.html', si_unit=si_unit, results=None, message=message)

        # Render the results
        return render_template('results2.html', si_unit=si_unit, results=processed_results, message=None)

    except Exception as e:
        print(f"Error during query execution: {e}")
        return f"An error occurred: {e}"


@app.route('/quantity_details')
def quantity_details():
    """Route to display detailed information about the Quantity."""
    obj_value = request.args.get('value', '').strip()

    if not obj_value:
        return render_template('quantity_details.html', heading="No Quantity Provided", data=[])

    try:
        # SPARQL query to fetch details about the Quantity
        query = f"""
        SELECT ?pred ?obj
        WHERE {{
            <{obj_value}> ?pred ?obj .
        }}
        """
        results = g.query(query)

        # Debugging output
        print(f"Query Results for Quantity: {list(results)}")

        # Process the results into a list of dictionaries
        data = [{"Predicate": remove_url_prefix(str(row[0])), "Object": remove_url_prefix(str(row[1]))} for row in results]

        # Set the heading to the Quantity object value
        heading = f"Details about Quantity: {remove_url_prefix(obj_value)}"

        # If no data is found
        if not data:
            heading = f"No details found for {remove_url_prefix(obj_value)}"
            return render_template('quantity_details.html', heading=heading, data=[])

        # Render the template with the data
        return render_template('quantity_details.html', heading=heading, data=data)

    except Exception as e:
        print(f"Error querying RDF data: {e}")
        return render_template('quantity_details.html', heading="Error Occurred", data=[])


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
#                 processed_results["Defining Equation"] = obj  # Keep as plain text for MathJax rendering

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
# g.parse("quantities.ttl", format="ttl")  # Ensure the quantities.ttl file is included
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
#                 # Process the quantity value
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
#                 processed_results["Defining Equation"] = obj.strip()  # Keep as plain text for MathJax rendering

#         # If no data is found, return a message
#         if all(value is None for value in processed_results.values()):
#             message = f"No information found for SI unit: {si_unit}"
#             return render_template('results.html', si_unit=si_unit, results=None, message=message)

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
#     app.run(debug=False)






# from flask import Flask, render_template, request
# import rdflib

# app = Flask(_name_)

# # Load RDF graphs for all the required TTL files
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
#     """Root route to display the SI unit search form."""
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
#                 processed_results["Defining Constant"] = remove_url_prefix(obj)
#             elif "hasDefiningResolution" in pred:
#                 processed_results["Defining Resolution"] = remove_url_prefix(obj)
#             elif "hasUnitTypeAsString" in pred:
#                 processed_results["Unit Type"] = remove_url_prefix(obj)
#             elif "hasUnit" in pred:
#                 processed_results["Unit"] = remove_url_prefix(obj)
#             elif "hasDefiningEquation" in pred:
#                 # Assume the defining equation is a LaTeX string or can be converted to one
#                 processed_results["Defining Equation"] = f"\\[{obj}\\]"

#         if all(value is None for value in processed_results.values()):
#             message = f"No information found for SI unit: {si_unit}"
#             return render_template('results.html', si_unit=si_unit, results=None, message=message)

#         return render_template('results.html', si_unit=si_unit, results=processed_results, message=None)

#     except Exception as e:
#         print(f"Error during query execution: {e}")
#         return f"An error occurred: {e}"


# if _name_ == "_main_":
#     app.run(debug=True)






# from flask import Flask, render_template, request
# import rdflib

# app = Flask(_name_)

# # Load RDF graphs for all the required TTL files
# g = rdflib.Graph()
# g.parse("si.ttl", format="ttl")         # SI Units Data
# g.parse("quantities.ttl", format="ttl")  # Quantities Data
# g.parse("decisions.ttl", format="ttl")   # Decisions Data
# g.parse("constants.ttl", format="ttl")   # Constants Data
# g.parse("units.ttl", format="ttl")       # Units Data
# g.parse("prefixes.ttl", format="ttl")    # Prefixes Data

# # Helper function to remove URL prefixes for better display
# def remove_url_prefix(uri):
#     return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]

# @app.route('/')
# def index():
#     # This route will display a form where users can input the SI unit to search
#     return render_template('index.html')

# @app.route('/search', methods=['POST'])
# def search():
#     si_unit = request.form.get('si_unit', '').strip().lower()

#     try:
#         # SPARQL query to search for SI unit, prefix, or related data, including constants and decisions
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
#                 <https://si-digital-framework.org/SI#hasDefiningEquation>,
#                 <https://si-digital-framework.org/quantities#hasQuantity>,  # Added for quantities.ttl
#                 <https://si-digital-framework.org/decisions#hasDecision>, # Added for decisions.ttl
#                 <https://si-digital-framework.org/constants#hasConstant>,  # Added for constants.ttl
#                 <https://si-digital-framework.org/units#hasUnit>,  # Added for units.ttl
#                 <https://si-digital-framework.org/prefixes#hasPrefix>  # Added for prefixes.ttl
#             ))
#         }}
#         """
#         results = g.query(query)

#         # Initialize the results dictionary with the default values for each attribute
#         processed_results = {
#             "Unit": None,
#             "Symbol": None,
#             "Quantity": None,
#             "Defining Constant": None,
#             "Defining Resolution": None,
#             "Unit Type": None,
#             "Defining Equation": None
#         }

#         # Process the results and populate the dictionary
#         for result in results:
#             subj = str(result[0])
#             pred = str(result[1])
#             obj = str(result[2])

#             # Update processed results for each predicate
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
#                 processed_results["Defining Equation"] = obj

#         # If no results found, set a message
#         if all(value is None for value in processed_results.values()):
#             message = f"No information found for SI unit: {si_unit}"
#             return render_template('results.html', si_unit=si_unit, results=None, message=message)

#         # If Quantity is missing, set a fallback message
#         if processed_results["Quantity"] is None:
#             # Check quantities.ttl file for the Quantity
#             quantity_query = f"""
#             SELECT ?obj
#             WHERE {{
#                 ?subj <https://si-digital-framework.org/quantities#hasQuantity> ?obj .
#                 FILTER(CONTAINS(LCASE(STR(?subj)), "{si_unit}"))
#             }}
#             """
#             quantity_results = g.query(quantity_query)
            
#             # If Quantity found in quantities.ttl, use it
#             if quantity_results:
#                 processed_results["Quantity"] = remove_url_prefix(next(iter(quantity_results))[0])
#             else:
#                 processed_results["Quantity"] = "Quantity not found"

#         # Also check for the unit in the units.ttl file
#         unit_query = f"""
#         SELECT ?obj
#         WHERE {{
#             ?subj <https://si-digital-framework.org/units#hasUnit> ?obj .
#             FILTER(CONTAINS(LCASE(STR(?subj)), "{si_unit}"))
#         }}
#         """
#         unit_results = g.query(unit_query)
#         if unit_results:
#             processed_results["Unit"] = remove_url_prefix(next(iter(unit_results))[0])

#         return render_template('results.html', si_unit=si_unit, results=processed_results, message=None)

#     except Exception as e:
#         print(f"Error during query execution: {e}")
#         return f"An error occurred: {e}"

# if _name_ == "_main_":
    # app.run(debug=False)





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








# from flask import Flask, render_template, request
# import rdflib

# app = Flask(_name_)

# # Load RDF graphs for all the required TTL files
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
#     """Root route to display the SI unit search form."""
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
#                 processed_results["Defining Constant"] = remove_url_prefix(obj)
#             elif "hasDefiningResolution" in pred:
#                 processed_results["Defining Resolution"] = remove_url_prefix(obj)
#             elif "hasUnitTypeAsString" in pred:
#                 processed_results["Unit Type"] = remove_url_prefix(obj)
#             elif "hasUnit" in pred:
#                 processed_results["Unit"] = remove_url_prefix(obj)
#             elif "hasDefiningEquation" in pred:
#                 # Assume the defining equation is a LaTeX string or can be converted to one
#                 processed_results["Defining Equation"] = f"\\[{obj}\\]"

#         if all(value is None for value in processed_results.values()):
#             message = f"No information found for SI unit: {si_unit}"
#             return render_template('results.html', si_unit=si_unit, results=None, message=message)

#         return render_template('results.html', si_unit=si_unit, results=processed_results, message=None)

#     except Exception as e:
#         print(f"Error during query execution: {e}")
#         return f"An error occurred: {e}"


# if _name_ == "_main_":
#     app.run(debug=True)






# from flask import Flask, render_template, request
# import rdflib

# app = Flask(_name_)

# # Load RDF graphs for all the required TTL files
# g = rdflib.Graph()
# g.parse("si.ttl", format="ttl")         # SI Units Data
# g.parse("quantities.ttl", format="ttl")  # Quantities Data
# g.parse("decisions.ttl", format="ttl")   # Decisions Data
# g.parse("constants.ttl", format="ttl")   # Constants Data
# g.parse("units.ttl", format="ttl")       # Units Data
# g.parse("prefixes.ttl", format="ttl")    # Prefixes Data

# # Helper function to remove URL prefixes for better display
# def remove_url_prefix(uri):
#     return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]

# @app.route('/')
# def index():
#     # This route will display a form where users can input the SI unit to search
#     return render_template('index.html')

# @app.route('/search', methods=['POST'])
# def search():
#     si_unit = request.form.get('si_unit', '').strip().lower()

#     try:
#         # SPARQL query to search for SI unit, prefix, or related data, including constants and decisions
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
#                 <https://si-digital-framework.org/SI#hasDefiningEquation>,
#                 <https://si-digital-framework.org/quantities#hasQuantity>,  # Added for quantities.ttl
#                 <https://si-digital-framework.org/decisions#hasDecision>, # Added for decisions.ttl
#                 <https://si-digital-framework.org/constants#hasConstant>,  # Added for constants.ttl
#                 <https://si-digital-framework.org/units#hasUnit>,  # Added for units.ttl
#                 <https://si-digital-framework.org/prefixes#hasPrefix>  # Added for prefixes.ttl
#             ))
#         }}
#         """
#         results = g.query(query)

#         # Initialize the results dictionary with the default values for each attribute
#         processed_results = {
#             "Unit": None,
#             "Symbol": None,
#             "Quantity": None,
#             "Defining Constant": None,
#             "Defining Resolution": None,
#             "Unit Type": None,
#             "Defining Equation": None
#         }

#         # Process the results and populate the dictionary
#         for result in results:
#             subj = str(result[0])
#             pred = str(result[1])
#             obj = str(result[2])

#             # Update processed results for each predicate
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
#                 processed_results["Defining Equation"] = obj

#         # If no results found, set a message
#         if all(value is None for value in processed_results.values()):
#             message = f"No information found for SI unit: {si_unit}"
#             return render_template('results.html', si_unit=si_unit, results=None, message=message)

#         # If Quantity is missing, set a fallback message
#         if processed_results["Quantity"] is None:
#             # Check quantities.ttl file for the Quantity
#             quantity_query = f"""
#             SELECT ?obj
#             WHERE {{
#                 ?subj <https://si-digital-framework.org/quantities#hasQuantity> ?obj .
#                 FILTER(CONTAINS(LCASE(STR(?subj)), "{si_unit}"))
#             }}
#             """
#             quantity_results = g.query(quantity_query)
            
#             # If Quantity found in quantities.ttl, use it
#             if quantity_results:
#                 processed_results["Quantity"] = remove_url_prefix(next(iter(quantity_results))[0])
#             else:
#                 processed_results["Quantity"] = "Quantity not found"

#         # Also check for the unit in the units.ttl file
#         unit_query = f"""
#         SELECT ?obj
#         WHERE {{
#             ?subj <https://si-digital-framework.org/units#hasUnit> ?obj .
#             FILTER(CONTAINS(LCASE(STR(?subj)), "{si_unit}"))
#         }}
#         """
#         unit_results = g.query(unit_query)
#         if unit_results:
#             processed_results["Unit"] = remove_url_prefix(next(iter(unit_results))[0])

#         return render_template('results.html', si_unit=si_unit, results=processed_results, message=None)

#     except Exception as e:
#         print(f"Error during query execution: {e}")
#         return f"An error occurred: {e}"

# if _name_ == "_main_":
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
#     app.run(host="0.0.0.0", port=8080, debug=False)





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
#     app.run(host="192.168.1.100", port=8080, debug=False)





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
#     app.run(host="0.0.0.0", port=8080, debug=False)







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

def process_defining_equation(equation):
    """
    Prepares the defining equation for LaTeX rendering.
    """
    # Replace LaTeX special characters with proper formatting
    equation = equation.replace("\\", "\\\\")  # Escape backslashes
    equation = equation.replace("{", "\\{").replace("}", "\\}")  # Escape braces
    return equation


@app.route('/search', methods=['POST'])
def search():
    si_unit = request.form.get('si_unit', '').strip().lower()

    try:
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
        results = g.query(query)

        processed_results = {
            "Unit": None,
            "Symbol": None,
            "Quantity": None,
            "Defining Constant": None,
            "Defining Resolution": None,
            "Unit Type": None,
            "Defining Equation": None
        }

        for result in results:

            subj = str(result[0])
            pred = str(result[1])
            obj = str(result[2])

            if "hasSymbol" in pred:
                processed_results["Symbol"] = remove_url_prefix(obj)
            elif "hasQuantity" in pred:
                processed_results["Quantity"] = remove_url_prefix(obj)
            elif "hasDefiningConstant" in pred:
                processed_results["Defining Constant"] = remove_url_prefix(obj)
            elif "hasDefiningResolution" in pred:
                processed_results["Defining Resolution"] = remove_url_prefix(obj)
            elif "hasUnitTypeAsString" in pred:
                processed_results["Unit Type"] = remove_url_prefix(obj)
            elif "hasUnit" in pred:
                processed_results["Unit"] = remove_url_prefix(obj)
            elif "hasDefiningEquation" in pred:
                # Process equation for LaTeX rendering
                processed_results["Defining Equation"] = process_defining_equation(obj)

        if all(value is None for value in processed_results.values()):
            message = f"No information found for SI unit: {si_unit}"
            return render_template('results.html', si_unit=si_unit, results=None, message=message)

        return render_template('results.html', si_unit=si_unit, results=processed_results, message=None)

    except Exception as e:
        print(f"Error during query execution: {e}")
        return f"An error occurred: {e}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)








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
#     app.run(debug=False)






