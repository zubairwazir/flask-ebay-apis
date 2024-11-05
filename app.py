from flask import Flask, request, render_template, jsonify
import json, urllib.request

app = Flask(__name__, static_folder="static")
app.debug = True


@app.route("/", methods=['GET'])
def index():
    return (app.send_static_file('ebay.html'))


@app.route("/search-ebay", methods=['GET'])
def processForm():
    check = "false"
    freeshipcheck = "false"
    expshipcheck = "false"
    #mykey=MrunalDe-MrunalAp-PRD-d2eb4905c-3e24c023
    keyword = request.args.get("Keyword")
    priceFrom = request.args.get("from")
    priceTo = request.args.get("to")

    condition = request.args.getlist("cond")
    seller = request.args.get("ra")
    if (seller == "Return Accepted"):
        check = "true"

    shipping = request.args.getlist("ship")
    if (len(shipping) != 0):
        if (shipping[0] == "free"):
            freeshipcheck = "true"
        if (shipping[0] == "expedited" or len(shipping) == 2):
            expshipcheck = "true"

    sortby = request.args.get("sort_by")

    # print(keyword)
    # print(priceTo)
    print(priceFrom)
    print(len(priceFrom))
    #print(condition)
    #print(seller)
    print(shipping)
    #print(sortby)
    # print(check)
    constr = ""
    str0 = ""
    str2 = ""
    str3 = ""
    str4 = ""
    newflag = False

    if (len(priceTo) == 0 and len(priceFrom) == 0):
        str0 = ""
    elif (len(priceTo) > 0 and len(priceFrom) == 0):
        str0 += "&itemFilter(0).name=MaxPrice&itemFilter(0).value=" + priceTo + "&itemFilter(0).paramName=Currency&itemFilter(0).paramValue=USD"
    elif (len(priceTo) == 0 and len(priceFrom) > 0):
        str0 += "&itemFilter(0).name=MinPrice&itemFilter(0).value=" + priceFrom + "&itemFilter(0).paramName=Currency&itemFilter(0).paramValue=USD"
    else:
        str0 += "&itemFilter(0).name=MaxPrice&itemFilter(0).value=" + priceTo + "&itemFilter(0).paramName=Currency&itemFilter(0).paramValue=USD&itemFilter(1).name=MinPrice&itemFilter(1).value=" + priceFrom + "&itemFilter(1).paramName=Currency&itemFilter(1).paramValue=USD"
        newflag = True

    print(len(str0))

    if (len(str0) == 0 and len(condition) > 0):  #if no price range
        constr += "&itemFilter(0).name=Condition"
        for i in range(len(condition)):
            constr += "&itemFilter(0).value(" + str(i) + ")=" + condition[i]

    elif (len(condition) > 0 and len(str0) > 0
          and newflag == False):  #if any of 1 price range
        constr += "&itemFilter(1).name=Condition"
        for i in range(len(condition)):
            constr += "&itemFilter(1).value(" + str(i) + ")=" + condition[i]

    elif (len(condition) > 0 and newflag == True):  #both price range
        constr += "&itemFilter(2).name=Condition"
        for i in range(len(condition)):
            constr += "&itemFilter(2).value(" + str(i) + ")=" + condition[i]
    else:
        constr = ""

    # if(seller==None)://compulsory
    if (len(condition) == 0 and len(priceFrom) == 0 and len(priceTo) == 0):
        str2 += "&itemFilter(0).name=ReturnsAcceptedOnly&itemFilter(0).value(0)=" + check
    elif (len(condition) > 0 and len(priceFrom) == 0 and len(priceTo) == 0):
        str2 += "&itemFilter(1).name=ReturnsAcceptedOnly&itemFilter(1).value(0)=" + check
    elif (len(condition) == 0 and len(str0) > 0 and newflag == False):
        str2 += "&itemFilter(1).name=ReturnsAcceptedOnly&itemFilter(1).value(0)=" + check
    elif (len(str0) > 0 and newflag == False and len(condition) > 0):
        str2 += "&itemFilter(2).name=ReturnsAcceptedOnly&itemFilter(2).value(0)=" + check
    elif (len(condition) == 0 and newflag == True):
        str2 += "&itemFilter(2).name=ReturnsAcceptedOnly&itemFilter(2).value(0)=" + check
    else:
        str2 += "&itemFilter(3).name=ReturnsAcceptedOnly&itemFilter(3).value(0)=" + check

    #compulsory
    if (len(condition) == 0 and len(priceFrom) == 0 and len(priceTo) == 0):
        str3 += "&itemFilter(1).name=FreeShippingOnly&itemFilter(1).value(0)=" + freeshipcheck
    elif (len(condition) > 0 and len(priceFrom) == 0 and len(priceTo) == 0):
        str3 += "&itemFilter(2).name=FreeShippingOnly&itemFilter(2).value(0)=" + freeshipcheck
    elif (len(condition) == 0 and len(str0) > 0 and newflag == False):
        str3 += "&itemFilter(2).name=FreeShippingOnly&itemFilter(2).value(0)=" + freeshipcheck
    elif (len(str0) > 0 and newflag == False and len(condition) > 0):
        str3 += "&itemFilter(3).name=FreeShippingOnly&itemFilter(3).value(0)=" + freeshipcheck
    elif (len(condition) == 0 and newflag == True):
        str3 += "&itemFilter(3).name=FreeShippingOnly&itemFilter(3).value(0)=" + freeshipcheck
    else:
        str3 += "&itemFilter(4).name=FreeShippingOnly&itemFilter(4).value(0)=" + freeshipcheck

    if (len(condition) == 0 and len(priceFrom) == 0 and len(priceTo) == 0):
        if (expshipcheck == "true"):
            str4 += "&itemFilter(2).name=ExpeditedShippingType&itemFilter(2).value(0)=Expedited"
    elif (len(condition) > 0 and len(priceFrom) == 0 and len(priceTo) == 0):
        if (expshipcheck == "true"):
            str4 += "&itemFilter(3).name=ExpeditedShippingType&itemFilter(3).value(0)=Expedited"
    elif (len(condition) == 0 and len(str0) > 0 and newflag == False):
        if (expshipcheck == "true"):
            str4 += "&itemFilter(3).name=ExpeditedShippingType&itemFilter(3).value(0)=Expedited"
    elif (len(str0) > 0 and newflag == False and len(condition) > 0):
        if (expshipcheck == "true"):
            str4 += "&itemFilter(4).name=ExpeditedShippingType&itemFilter(4).value(0)=Expedited"
    elif (len(condition) == 0 and newflag == True):
        if (expshipcheck == "true"):
            str4 += "&itemFilter(4).name=ExpeditedShippingType&itemFilter(4).value(0)=Expedited"
    else:
        if (expshipcheck == "true"):
            str4 += "&itemFilter(5).name=ExpeditedShippingType&itemFilter(5).value(0)=Expedited"


    #url="https://svcs.ebay.com/services/search/FindingService/v1?OPERATIONNAME=findItemsAdvanced&SERVICE-VERSION=1.0.0&SECURITY-APPNAME=MrunalDe-MrunalAp-PRD-d2eb4905c-3e24c023&RESPONSEDATA-FORMAT=JSON&RESTPAYLOAD&keywords=iphone&paginationInput.entriesPerPage=25&sortOrder=BestMatch&itemFilter(0).name=MaxPrice&itemFilter(0).value=25&itemFilter(0).paramName=Currency&itemFilter(0).paramValue=USD&itemFilter(1).name=MinPrice&itemFilter(1).value=10&itemFilter(1).paramName=Currency&itemFilter(1).paramValue=USD&itemFilter(2).name=ReturnsAcceptedOnly&itemFilter(2).value=false&itemFilter(3).name=Condition&itemFilter(3).value(0)=2000&itemFilter(3).value(1)=3000"
    #url="https://svcs.ebay.com/services/search/FindingService/v1?OPERATION-NAME=findItemsAdvanced&SERVICE-VERSION=1.0.0&SECURITY-APPNAME=MrunalDe-MrunalAp-PRD-d2eb4905c-3e24c023&RESPONSE-DATA-FORMAT=JSON&REST-PAYLOAD&keywords=iphone&paginationInput.entriesPerPage=25&sortOrder=BestMatch&itemFilter(0).name"
    #url = "https://svcs.ebay.com/services/search/FindingService/v1?OPERATION-NAME=findItemsAdvanced&SERVICE-VERSION=1.0.0&SECURITY-APPNAME=MrunalDe-MrunalAp-PRD-d2eb4905c-3e24c023&RESPONSE-DATA-FORMAT=JSON&REST-PAYLOAD&keywords="+keyword+"&paginationInput.entriesPerPage=25&sortOrder=bestmatch&itemFilter(0).name=MaxPrice&itemFilter(0).value="+priceTo+"&itemFilter(0).paramName=Currency&itemFilter(0).paramValue=USD&itemFilter(1).name=MinPrice&itemFilter(1).value="+priceFrom+"&itemFilter(1).paramName=Currency&itemFilter(1).paramValue=USD&itemFilter(2).name=Condition&itemFilter(2).value(0)=1000&itemFilter(2).value(1)=3000"

    url = "https://svcs.ebay.com/services/search/FindingService/v1?OPERATION-NAME=findItemsAdvanced&SERVICE-VERSION=1.0.0&SECURITY-APPNAME=MrunalDe-MrunalAp-PRD-d2eb4905c-3e24c023&RESPONSE-DATA-FORMAT=JSON&REST-PAYLOAD&keywords=" + keyword + "&paginationInput.entriesPerPage=25&sortOrder=" + sortby + str0 + constr + str2 + str3 + str4
    print(url)
    url_req = urllib.request.urlopen(url)
    json_obj = json.load(url_req)

    rf = json_obj.get("findItemsAdvancedResponse")
    # top_image = ""
    # imageURL=[]
    # item_title = []
    # link = []
    # category_name = []
    # condition_item=[]
    # top_image = []
    # current_price =[]
    # ship_cost = []
    # ret_acc = []
    # locations = []
    #print(len(rf))
    for i in range(len(rf)):
        x = rf[i]
    l = x["paginationOutput"]
    #print("l:"+l)
    searchResult = x["searchResult"]
    #print(len(searchResult))

    # return if count is 0
    if searchResult[0]["@count"] == "0":
        return jsonify(data={"count": "0"})

    item = (searchResult[0]["item"])
    #print(len(item))

    keysToCheck = set([
        "galleryURL", "title", "viewItemURL", "returnsAccepted",
        "primaryCategory", "condition", "topRatedListing", "sellingStatus",
        "shippingInfo", "location"
    ])

    responseItems = []

    for i in range(len(item)):
        if len(responseItems) == 10:
            break

        item1 = item[i]

        # if item doesn't have all required keys then skip it
        if not keysToCheck.issubset(item1.keys()):
            continue

        itemToAdd = {}

        itemToAdd["galleryURL"] = item1["galleryURL"][0]
        # iURL = item1["galleryURL"][0]
        # imageURL.append(iURL)

        itemToAdd["title"] = item1["title"][0]
        # item_var = item1["title"][0]
        # item_title.append(item_var)

        itemToAdd["viewItemURL"] = item1["viewItemURL"][0]
        # link_var = item1["viewItemURL"][0]
        # link.append(link_var)

        itemToAdd["returnsAccepted"] = item1["returnsAccepted"][0]
        # ret_acc.append(item1["returnsAccepted"][0] if item1.__contains__("returnsAccepted") else "false")

        itemToAdd["categoryName"] = item1["primaryCategory"][0]["categoryName"][0]
        # item2 = item1["primaryCategory"][0]
        # category_name_var  = item2["categoryName"][0]
        # category_name.append(category_name_var)

        itemToAdd["condition"] = item1["condition"][0]["conditionDisplayName"][0]
        # item3 = item1["condition"][0]
        # condition_item_var = item3["conditionDisplayName"][0]
        # condition_item.append(condition_item_var)

        itemToAdd["topRatedListing"] = item1["topRatedListing"][0]
        # top_rated_var = item1["topRatedListing"][0]
        # if (top_rated_var == "true"):
        #     top_image.append("true")
        # else:
        #     top_image.append("false")

        itemToAdd["currentPrice"] = item1["sellingStatus"][0]["convertedCurrentPrice"][0]["__value__"]
        # item4 =  item1["sellingStatus"][0]
        # curr_price = item4["convertedCurrentPrice"][0]
        # current_price_var = float(curr_price["__value__"])
        # current_price.append(current_price_var)
        if ("shippingServiceCost" in item1["shippingInfo"][0].keys()):
            itemToAdd["shippingServiceCost"] = item1["shippingInfo"][0]["shippingServiceCost"][0]["__value__"]
        else:
            itemToAdd["shippingServiceCost"] = 0.0
        # print(item1["shippingInfo"][0].keys())
        itemToAdd["expeditedShipping"] = item1["shippingInfo"][0]["expeditedShipping"][0]
        
        # item5 = item1["shippingInfo"][0]
        # ship_cost.append(item5)

        itemToAdd["location"] = item1["location"][0]
        # locations.append(item1["location"][0])

        responseItems.append(itemToAdd)

    a = l[0]
    entries = int(a['totalEntries'][0])

    # data = {
    #     "keyword":keyword,
    #     "entries":entries,
    #     "shipping": shipping,
    #     "ret_acc": ret_acc,
    #     "imageURL": imageURL,
    #     "item_title":item_title,
    #     "link":link,
    #     "category_name":category_name,
    #     "condition_item":condition_item,
    #     "top_image":top_image,
    #     "current_price":current_price,
    #     "ship_cost": ship_cost,
    #     "locations": locations
    # }
    return jsonify(data={
        "keyword": keyword,
        "entries": entries,
        "items": responseItems
    })


if __name__ == "__main__":
    app.run()