from flask import Flask, render_template, request
import rdflib

app = Flask(__name__)

# Load RDF graphs from Turtle (.ttl) files
g = rdflib.Graph()
g.parse("si.ttl", format="ttl")
g.parse("quantities.ttl", format="ttl")
g.parse("decisions.ttl", format="ttl")
g.parse("constants.ttl", format="ttl")
g.parse("units.ttl", format="ttl")
g.parse("prefixes.ttl", format="ttl")


def remove_url_prefix(uri):
    """
    Helper function to clean URL prefixes for display.
    Removes namespaces and keeps only the relevant part of the URI.
    """
    return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]


@app.route('/')
def index():
    """
    Renders the homepage where users can enter an SI unit for searching.
    """
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """
    Handles the search request.
    Takes an SI unit as input, queries the RDF graph, and returns relevant information.
    """
    si_unit = request.form.get('si_unit', '').strip().lower()

    try:
        # SPARQL query to fetch relevant data related to the given SI unit
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

        # Execute the query on the RDF graph
        results = g.query(query)

        # Dictionary to store processed results
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
            subj = str(result[0])  # Subject
            pred = str(result[1])  # Predicate
            obj = str(result[2])  # Object

            if "hasSymbol" in pred:
                processed_results["Symbol"] = remove_url_prefix(obj)
            elif "hasQuantity" in pred:
                processed_results["Quantity"] = remove_url_prefix(obj)
            elif "hasDefiningConstant" in pred:
                # Construct the BIPM URL for the defining constant
                processed_results["Defining Constant"] = f'<a href="https://www.bipm.org/en/-/resolution-cgpm-{remove_url_prefix(obj)}" target="_blank">{remove_url_prefix(obj)}</a>'
            elif "hasDefiningResolution" in pred:
                # Construct the BIPM URL for the defining resolution
                processed_results["Defining Resolution"] = f'<a href="https://www.bipm.org/en/-/resolution-cgpm-{remove_url_prefix(obj)}" target="_blank">{remove_url_prefix(obj)}</a>'
            elif "hasUnitTypeAsString" in pred:
                processed_results["Unit Type"] = remove_url_prefix(obj)
            elif "hasUnit" in pred:
                processed_results["Unit"] = remove_url_prefix(obj)
            elif "hasDefiningEquation" in pred:
                # Keep equation as plain text for MathJax rendering
                processed_results["Defining Equation"] = obj.strip()

        # If no relevant data is found, return a message
        if all(value is None for value in processed_results.values()):
            message = f"No information found for SI unit: {si_unit}"
            return render_template('results2.html', si_unit=si_unit, results=None, message=message)

        # Render the results on the results2.html page
        return render_template('results2.html', si_unit=si_unit, results=processed_results, message=None)

    except Exception as e:
        print(f"Error during query execution: {e}")
        return f"An error occurred: {e}"


@app.route('/resolution')
def resolution():
    """
    Handles requests for detailed information about a selected constant or resolution.
    Queries the RDF graph and returns additional details.
    """
    obj_value = request.args.get('value', '').strip()

    if not obj_value:
        return render_template('resolution.html', heading="No Value Provided", data=[])

    try:
        # SPARQL query to fetch information about the object from the graph
        query = f"""
        SELECT ?pred ?obj
        WHERE {{
            <{obj_value}> ?pred ?obj .
        }}
        """
        results = g.query(query)

        # Process query results into a structured list of dictionaries
        data = [{"Predicate": remove_url_prefix(str(row[0])), "Object": remove_url_prefix(str(row[1]))} for row in results]

        # Set the heading to display the object's value
        heading = f"Information about: {remove_url_prefix(obj_value)}"

        # If no data is found, show an appropriate message
        if not data:
            heading = f"No information found for {remove_url_prefix(obj_value)}"
            return render_template('resolution.html', heading=heading, data=[])

        # Render the resolution.html page with the retrieved data
        return render_template('resolution.html', heading=heading, data=data)

    except Exception as e:
        print(f"Error querying RDF data: {e}")
        return render_template('resolution.html', heading="Error Occurred", data=[])


if __name__ == "__main__":
    # Run the Flask app on port 8080, accessible on all network interfaces
    app.run(host="0.0.0.0", port=8080)  # Updated for external access








# from flask import Flask, render_template, request, jsonify
# import requests
# from bs4 import BeautifulSoup

# app = Flask(__name__)

# # Function to scrape and format BIPM data
# def scrape_bipm_data():
#     url = 'https://www.bipm.org/en/-/resolution-cgpm-26-1'
#     response = requests.get(url)

#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'html.parser')

#         # Extract title
#         title = soup.find('title').get_text()

#         # Extract all paragraphs
#         paragraphs = soup.find_all('p')
#         content_list = [p.get_text() for p in paragraphs if p.get_text().strip()]

#         # Convert to structured format
#         formatted_content = "<br><br>".join(f"<strong>• {p}</strong>" for p in content_list)

#         return {"title": title, "content": formatted_content}
#     else:
#         return {"error": "Failed to retrieve data"}

# # Route to render homepage
# @app.route('/')
# def home():
#     return render_template('hello.html')

# # Route to fetch and return formatted data
# @app.route('/get-data', methods=['GET'])
# def get_data():
#     data = scrape_bipm_data()
#     return jsonify(data)  # Return JSON

# if __name__ == '__main__':
#     app.run(debug=True)

