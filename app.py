# from flask import Flask, request, render_template, send_from_directory
from flask import Flask, make_response, request
# from werkzeug.utils import secure_filename
from itertools import chain, combinations
import os
import argparse
import io
import csv

app = Flask(__name__)

output_result = {
    "error": None,
    "result": "",
    "file": None,
    "total": None
}



@app.route('/')
def form():
    return """
       <html>
        <head>
            <link
            rel="stylesheet"
            href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
            integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T"
            crossorigin="anonymous"
            />
            <link
            rel="stylesheet"
            href="https://use.fontawesome.com/releases/v5.6.3/css/all.css"
            integrity="sha384-UHRtZLI+pbxtHCWp1t77Bi1L4ZtiqrqD80Kn4Z8NTSRyMA2Fd33n5dQ8lWUE00s/"
            crossorigin="anonymous"
            />
            <link
            rel="stylesheet"
            href="https://unpkg.com/bootstrap-table@1.19.1/dist/bootstrap-table.min.css"
            />
        </head>
        <style type="text/css">
            body {
                 background-image: linear-gradient(to right top, #f8b368, #f7ac6c, #f5a670, #f3a074, #ef9b78, #ed9e72, #eaa26d, #e6a668, #d9b75f, #c3c962, #a3da73, #74e993);

            margin: 0;
            padding: 0;
            background-color: #fbfbfb;
            height: 100vh;
            }
            #login .container #login-row #login-column #login-box {
            
            
            margin-top: 120px;
            max-width: 600px;
            height: 320px;
            border: 1px solid #9c9c9c;
            background-color: #eaeaea;
            box-shadow: 5px 5px #888888;
            border-radius: 5px;
            }
            #login .container #login-row #login-column #login-box #login-form {
            padding: 20px;
            }
            #login
            .container
            #login-row
            #login-column
            #login-box
            #login-form
            #register-link {
            margin-top: -85px;
            }

        </style>
        <body>
            <div class="gradient" id="login">
            <h3 class="text-center text-dark pt-5">CIS550 Apriori Algorithm</h3>
            <div class="container">
                <div
                id="login-row"
                class="row justify-content-center align-items-center"
                >
                <div id="login-column" class="col-md-6">
                    <div id="login-box" class="col-md-12">
                    <form
                        method="post" enctype="multipart/form-data"
                        action="/apriori"
                        id="login-form"
                        class="form"
                    >
                        <h2>Upload dataset 📊</h2>
                        <input type="file" name="data_file" />

                        <input name="mim_sup" placeholder="Minimum Support"  type="text" oninput="this.value = this.value.replace(/[^0-9.]/g, '').replace(/(\..*?)\..*/g, '$1');" />
                        <input type="submit" />


                        <br><p>Pramod Kumar Bathulla</p>
                        <p>2836854 | prbathul</p>

                    </form>
                    
                    </div>
                </div>
                </div>
            </div>
            </div>
        </body>
        </html>
    """

    
def add_to_sets(items):
    add_to_set = set()
    for item in items:
        add_to_set.add(item)
    return add_to_set


def convert_to_array_int(items):
    arr = []
    for item in items:
        arr.append(int((item)))
    return arr


def candidate_item(frequent_item, iterator):
    data = []
    for i in frequent_item:
        for j in frequent_item:
            if len(i.union(j)) == iterator:
                data.append(i.union(j))
    return set(data)


def subset(candidate, iterator):
    return set([frozenset(list(z)) for z in
                list(chain.from_iterable(combinations(candidate, j) for j in range(iterator - 1, iterator)))])


def has_infrequent_subset(candidate, data_set, minimum_support):
    re_formatted_candidate = set()
    list_of_items = list(candidate)
    for item in range(len(list_of_items)):
        i = 0
        for data in data_set:
            if list_of_items[item].issubset(data):
                i += 1
        if i >= minimum_support:
            re_formatted_candidate.add(list_of_items[item])
    return re_formatted_candidate


def apriori_gen(read_lines, minimum_support):
    re_formatted_data = []
    item_sets = set()
    iterator = 2
    for row in read_lines:
        split_by_comma = str(row.strip()).split(", ")
        line_number = split_by_comma.pop(0)
        item_sets = item_sets.union(split_by_comma)
        data = set(convert_to_array_int(split_by_comma))
        data.add(line_number + 'key')
        # converting tuple to frozenset
        re_formatted_data.append(frozenset(data))

    re_formatted_item_set = set(frozenset([int(single_set)]) for single_set in item_sets)
    frequent_item = has_infrequent_subset(re_formatted_item_set, re_formatted_data, minimum_support)
    frequent_item_sets = add_to_sets(frequent_item)

    while True:
        candidate_items = candidate_item(frequent_item, iterator)
        temp_candidate_items = set()
        for candidate in candidate_items:
            subsets = subset(candidate, iterator)
            count = 0
            for item in subsets:
                if item in frequent_item:
                    count += 1
            if count == len(subsets):
                temp_candidate_items.add(candidate)

        candidate_items = temp_candidate_items
        frequent_item = has_infrequent_subset(candidate_items, re_formatted_data, minimum_support)

        if len(frequent_item) != 0:
            for candidate in frequent_item:
                subsets = subset(candidate, iterator)
                frequent_item_sets.add(candidate)
                frequent_item_sets = frequent_item_sets - subsets

            iterator += 1
        else:
            break
    output_result["total"] = len(frequent_item_sets)
    return [set(z) for z in frequent_item_sets]


def main(select_file_list, minimum_support):
    try:
        filename = str(select_file_list)
        file_read = open(filename, "r")
        read_lines = file_read.readlines()
        file_read.close()
        output_result["result"] = apriori_gen(read_lines, int(minimum_support))
    except:
        output_result["error"] = "Invalid File: Some thing is wrong with file upload "

    return output_result



@app.route('/apriori', methods=["POST"])
def transform_view():
    try:
        f = request.files['data_file']
        minimum_support = request.form.get('mim_sup')
        if not f:
            return "No file"
        stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        l = []
        for i,v in enumerate(csv_input):
            t = ""
            for x in v:
                t = t+x+","
            l.append(t[:-1])
        output_result["result"] = apriori_gen(l, int(minimum_support))
        print(output_result['result'])
        print("End - total items:", output_result['total'])
        return str( "Total sets: "+str(len(output_result['result'])) +" \n"+str(output_result['result']) )
    except Exception as e:
        return " *Must provide Minimum support value,  "+ str(e)