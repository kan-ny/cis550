from flask import Flask, make_response, request
import io
import csv
import itertools
import time

app = Flask(__name__)
debug = True

MIN_SUPOORT = 0
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
                        action="/apriori_algo"
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

    
def find_frequency(*args):
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
        if v >= MIN_SUPOORT:
            t = args[0][i][:]
            t.sort()
            if t not in ret:
                ret.append(t)
                val.append( args[1][i] )
    if len(ret) == 0:
        return {"itemset": ret, "to_continue": False}
    if max(val) >= MIN_SUPOORT:
        to_continue = True
    total_sets.extend(ret)
    return {"itemset": ret, "to_continue": to_continue}

def apiori_gen(*args):
    s = set()
    l = []
    min_support_list = args[0]
    for x in range(0, len(min_support_list)-1 ):
        for y in range(x+1, len(min_support_list) ):
            temp = min_support_list[x][:]
            temp.extend( min_support_list[y] )
            l.insert( len(l) ,list(set(temp)) )
    l.sort()
    return list(l for l,_ in itertools.groupby(l))

@app.route('/apriori_algo', methods=["POST"])
def transform_view():
    try:
        f = request.files['data_file']
        if not f:
            return "Provide Data file"

        global MIN_SUPOORT
        global transactions
        global apriori_flag
        global total_sets
        global transactions_subset

        # MIN_SUPOORT = 20
        transactions = {}
        apriori_flag = True
        total_sets = []
        transactions_subset=[]

        MIN_SUPOORT = int(request.form.get('mim_sup'))
        print( 'File Name: ',f.filename, 'minimum support', MIN_SUPOORT)
        if not MIN_SUPOORT:
            return "Provide Minimun Support Value"

        filename = f.filename
        stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)

        start_time = time.time()
        for i,v in enumerate(csv_input):
            transactions[i] = list(map(int, v[1:] ))
            transactions_subset.append( set( list(map(int, v[1:] ))) ) 
        print('********* APRIORI *********', MIN_SUPOORT, 'Total Transactions:',len(transactions_subset) )
        s = set()
        for x in transactions.values():
            s.update(x)
        itemset = [[x] for x in s]
        sup_count = [0 for x in itemset]
        itemset.sort()
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
            "total_sets": final_set }
        print(ret)
        # return str("Mimimum Support: {}\n\nTotal Sets: {}\n\n{}".format(MIN_SUPOORT, len(final_set), final_set))
        return '''
                <html>
                    <head> <title>Apriori Result</title> </head>
                    <body>
                    <br>
                    <br>
                        <h2>File Name: {filename}</h2>
                        <h3>Minimum Support: {mim_s}</h3>
                        <h3>Total number of sets: {length}</h3>
                        <h4>
                            {sets}
                        </h4>
                        <h4>Time taken: {time} Seconds </h4>
                    </body>
                </html>
        '''.format(filename = filename, mim_s=MIN_SUPOORT, length= len(final_set), sets = final_set, time = round( (time.time() - start_time), 4 ) )
    except Exception as e:
        print(e)
        return "*Must provide CSV file and Minimum support value, "+ str(e) 