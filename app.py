from flask import Flask, request, render_template, jsonify
import json
import urllib.request

app = Flask(__name__, static_folder="static")
app.debug = True


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/search-ebay", methods=["GET"])
def process_form():
    # Initialize flags and get parameters
    keyword = request.args.get("Keyword", "")
    price_from = request.args.get("from", "")
    price_to = request.args.get("to", "")
    conditions = request.args.getlist("cond")
    seller = request.args.get("ra", "")
    shipping = request.args.getlist("ship")
    sort_by = request.args.get("sort_by", "BestMatch")

    return_accepted = "true" if seller == "Return Accepted" else "false"
    free_shipping = "true" if "free" in shipping else "false"
    expedited_shipping = "true" if "expedited" in shipping else "false"

    # Build URL filters
    filters = []
    price_filter_index = 0

    # Price filters
    if price_from or price_to:
        if price_to:
            filters.append(
                f"&itemFilter({price_filter_index}).name=MaxPrice&itemFilter({price_filter_index}).value={price_to}&itemFilter({price_filter_index}).paramName=Currency&itemFilter({price_filter_index}).paramValue=USD"
            )
            price_filter_index += 1
        if price_from:
            filters.append(
                f"&itemFilter({price_filter_index}).name=MinPrice&itemFilter({price_filter_index}).value={price_from}&itemFilter({price_filter_index}).paramName=Currency&itemFilter({price_filter_index}).paramValue=USD"
            )
            price_filter_index += 1

    # Condition filters
    if conditions:
        condition_filter = f"&itemFilter({price_filter_index}).name=Condition"
        for i, condition in enumerate(conditions):
            condition_filter += f"&itemFilter({price_filter_index}).value({i})={condition}"
        filters.append(condition_filter)
        price_filter_index += 1

    # Return Accepted filter
    filters.append(
        f"&itemFilter({price_filter_index}).name=ReturnsAcceptedOnly&itemFilter({price_filter_index}).value(0)={return_accepted}"
    )
    price_filter_index += 1

    # Free Shipping filter
    filters.append(
        f"&itemFilter({price_filter_index}).name=FreeShippingOnly&itemFilter({price_filter_index}).value(0)={free_shipping}"
    )
    price_filter_index += 1

    # Expedited Shipping filter
    if expedited_shipping == "true":
        filters.append(
            f"&itemFilter({price_filter_index}).name=ExpeditedShippingType&itemFilter({price_filter_index}).value(0)=Expedited"
        )

    # Construct the eBay API URL

    base_url = "https://svcs.ebay.com/services/search/FindingService/v1?OPERATION-NAME=findItemsAdvanced&SERVICE-VERSION=1.0.0&SECURITY-APPNAME=TomasSad-betterse-PRD-980426f0d-6a936209&RESPONSE-DATA-FORMAT=JSON&REST-PAYLOAD"

    url = f"{base_url}&keywords={keyword}&paginationInput.entriesPerPage=25&sortOrder={sort_by}{''.join(filters)}"

    try:
        # Fetch and parse JSON data
        response = urllib.request.urlopen(url)
        data = json.load(response)

        # Extract search results
        search_response = data.get("findItemsAdvancedResponse", [{}])[0]
        search_result = search_response.get("searchResult", [{}])[0]

        if search_result.get("@count", "0") == "0":
            return jsonify(data={"count": "0"})

        items = search_result.get("item", [])
        response_items = []

        # Required keys
        required_keys = {
            "galleryURL",
            "title",
            "viewItemURL",
            "returnsAccepted",
            "primaryCategory",
            "condition",
            "topRatedListing",
            "sellingStatus",
            "shippingInfo",
            "location",
        }

        # Prepare response items
        for item in items[:10]:  # Limit to 10 items
            if not required_keys.issubset(item.keys()):
                continue

            response_item = {
                "galleryURL": item["galleryURL"][0],
                "title": item["title"][0],
                "viewItemURL": item["viewItemURL"][0],
                "returnsAccepted": item["returnsAccepted"][0],
                "categoryName": item["primaryCategory"][0]["categoryName"][0],
                "condition": item["condition"][0]["conditionDisplayName"][0],
                "topRatedListing": item["topRatedListing"][0],
                "currentPrice": item["sellingStatus"][0]["convertedCurrentPrice"][0]["__value__"],
                "shippingServiceCost": item["shippingInfo"][0].get("shippingServiceCost", [{}])[0].get("__value__", 0.0),
                "expeditedShipping": item["shippingInfo"][0]["expeditedShipping"][0],
                "location": item["location"][0],
            }
            response_items.append(response_item)

        # Pagination information
        total_entries = int(search_response.get("paginationOutput", [{}])[0].get("totalEntries", [0])[0])

        return jsonify(data={"keyword": keyword, "entries": total_entries, "items": response_items})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify(data={"error": str(e)}), 500
    

@app.route("/home", methods=["GET"])
def home():
    # Default keyword for homepage items
    keyword = "electronics"  # You can set a category or popular keyword
    sort_by = "BestMatch"

    # Construct the eBay API URL for default items
    base_url = "https://svcs.ebay.com/services/search/FindingService/v1?OPERATION-NAME=findItemsAdvanced&SERVICE-VERSION=1.0.0&SECURITY-APPNAME=TomasSad-betterse-PRD-980426f0d-6a936209&RESPONSE-DATA-FORMAT=JSON&REST-PAYLOAD"
    url = f"{base_url}&keywords={keyword}&paginationInput.entriesPerPage=10&sortOrder={sort_by}"

    try:
        # Fetch and parse JSON data
        response = urllib.request.urlopen(url)
        data = json.load(response)

        # Extract search results
        search_response = data.get("findItemsAdvancedResponse", [{}])[0]
        search_result = search_response.get("searchResult", [{}])[0]

        if search_result.get("@count", "0") == "0":
            return render_template("home.html", items=[])

        items = search_result.get("item", [])
        response_items = []

        # Prepare response items
        for item in items:
            response_items.append({
                "galleryURL": item["galleryURL"][0],
                "title": item["title"][0],
                "viewItemURL": item["viewItemURL"][0],
                "price": item["sellingStatus"][0]["convertedCurrentPrice"][0]["__value__"],
                "location": item["location"][0],
            })

        return render_template("home.html", items=response_items)

    except Exception as e:
        print(f"Error: {e}")
        return render_template("home.html", items=[], error=str(e))



if __name__ == "__main__":
    app.run(debug=True)