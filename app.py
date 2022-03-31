from flask import Flask, make_response, request
import io
import sys
import csv
import itertools

app = Flask(__name__)
debug = True

MIN_SUPOORT = 20
transactions = {}
apriori_flag = True
total_sets = []
transactions_subset=[]


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
            <div id="login">
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
                        action="/transform"
                        id="login-form"
                        class="form"
                    >
                        <h2>Upload dataset 📊</h2>
                        <p>Minimum support is 20%</p>
                        <input type="file" name="data_file" />
                        <input type="submit" />
                    </form>
                    </div>
                </div>
                </div>
            </div>
            </div>
        </body>
        </html>
    """

    
def find_frequency(*args):
    print('find..')
    l = 0
    new = []
    temp = [ sum( set(x).issubset(y) for y in transactions_subset  ) for x in args[0] ]
    return temp

def check_in_support(*args):
    # compare candidate support count with min support
    ret = []
    val = []
    to_continue = False
    for i,v in enumerate(args[1]):
        # if v < MIN_SUPOORT:
        #     args[0].pop(i)
        #     args[1].pop(i)
        #     print(v, i)
        if v >= MIN_SUPOORT:
            t = args[0][i][:]
            t.sort()
            # print('step 3', t )
            if t not in ret:
                ret.append(t)
                val.append( args[1][i] )
    if len(ret) == 0:
        return {"itemset": ret, "to_continue": False}
    if max(val) >= MIN_SUPOORT:
        to_continue = True
    # print("\nElements with min support count: ",len(ret))
    total_sets.extend(ret)
    return {"itemset": ret, "to_continue": to_continue}
    # s = set(ret)
    # print("#", s)
    
    # return ret



def apiori_gen(*args):
    s = set()
    l = []
    min_support_list = args[0]
    for x in range(0, len(min_support_list)-1 ):
        for y in range(x+1, len(min_support_list) ):
            # print(x, y, min_support_list[x], min_support_list[y])
            temp = min_support_list[x][:]
            temp.extend( min_support_list[y] )
            l.insert( len(l) ,list(set(temp)) )
    l.sort()
    # print('\n\nGenerating Candidate list: \n',l )
    return list(l for l,_ in itertools.groupby(l))

@app.route('/transform', methods=["POST"])
def transform_view():
    f = request.files['data_file']
    if not f:
        return "No file"
    stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.reader(stream)
    #print("file contents: ", file_contents)
    #print(type(file_contents))
    for i,v in enumerate(csv_input):
        transactions[i] = list(map(int, v[1:] ))
        transactions_subset.append( set( list(map(int, v[1:] ))) ) 

    MIN_SUPOORT = int(len(transactions.keys()) * 0.02)

    print('********* APRIORI *********')
    # step 1: create unique set
    s = set()
    for x in transactions.values():
        s.update(x)
    # s= sorted(s)
    # print('------',s)
    itemset = [[x] for x in s]
    sup_count = [0 for x in itemset]
    # print("\nMinimum Supprot: ", MIN_SUPOORT)
    itemset.sort()
    # print('step 1', itemset)
    try:
        while(apriori_flag):
            sup_count = find_frequency(itemset)
            obj = check_in_support(itemset, sup_count)
            if obj['to_continue'] == False:
                break
            itemset = apiori_gen(obj['itemset'])
        temp = []
        for i,v in enumerate(total_sets):
            f = True
            for j,b in enumerate(total_sets):
                if set(v) != set(b) and (set(v) & set(b) == set(v)):
                    f = False
            if f == True:
                temp.append(v)
        final_set = [list(y) for y in set([tuple(x) for x in temp])]
        ret = {
            "len": len(final_set),
            "Minimum": MIN_SUPOORT,
            "total_sets": final_set
        }
        return str("Mimimum Support: {}\n\nTotal Sets: {}\n\n{}".format(MIN_SUPOORT, len(final_set), final_set))
    except Exception as e:
        print(e)
        return str(e)