from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
app = Flask(__name__)
app.secret_key = 'SuperSecretKey'
mysql = MySQLConnector(app,'python')


@app.route('/')
def root():
#     query = "SELECT id, level1 , ne_list, "
#     query += "  nat_list, "
#     query += "  dep_list, dep_ex_list,lob "
#     query += "FROM pbcs_pl"
#     data = mysql.query_db(query)
    return render_template('index.html', all_levels=[])


@app.route('/levels')
def index():
    query = "SELECT id, level1 , ne_list, "
    query += "  nat_list, "
    query += "  dep_list, dep_ex_list,lob "
    query += "FROM pbcs_pl"
    data = mysql.query_db(query)
    return render_template('index.html', all_levels=data)


@app.route('/levels/new')
def new():
    return render_template('level_new.html')



@app.route('/levels/<id>')
def show(id):
    query = "SELECT id, level1 , ne_list, "
    query += "  nat_list, "
    query += "  dep_list, dep_ex_list,lob "
    query += "FROM pbcs_pl WHERE id = {}".format(id)
    data = mysql.query_db(query)
    return render_template('level_edit.html', level=data[0])


@app.route('/levels/create', methods=['POST'])
def create():
    query = "INSERT INTO pbcs_pl (level1, ne_list, nat_list, dep_list, dep_ex_list, lob ) "
    query += "VALUES (:level1, :ne_list, :nat_list, :dep_list, :dep_ex_list, :lob) "
    data = {
        'level1': request.form['level1'],
        'ne_list': request.form['ne_list'],
        'nat_list': request.form['nat_list'],
        'dep_list': request.form['dep_list'],
        'dep_ex_list': request.form['dep_ex_list'],
        'lob': request.form['lob'],
    }
    id = mysql.query_db(query, data)
    return redirect('/levels')


@app.route('/levels/<id>/destroy')
def destory(id):
    query = "DELETE FROM pbcs_pl WHERE id = {}".format(id)
    mysql.query_db(query)
    return redirect('/levels')


@app.route('/levels/<id>', methods=['POST'])
def update(id):
    query = "UPDATE pbcs_pl SET "
    query += "level1 = '{}', ".format(request.form['level1'])
    query += "ne_list = '{}', ".format(request.form['ne_list'])
    query += "nat_list = '{}', ".format(request.form['nat_list'])
    query += "dep_list = '{}', ".format(request.form['dep_list'])
    query += "dep_ex_list = '{}', ".format(request.form['dep_ex_list'])
    query += "lob = '{}' ".format(request.form['lob'])
    query += "WHERE id = {}".format(id)

    mysql.query_db(query)
    return redirect('/levels')

@app.route('/levels/search/<searchQuery>')
def searchLevels(searchQuery):
    print(searchQuery)
    list= [];
    statusMsg = {"status":"", "message":""}
    if len(searchQuery) == 13 :
       pattern = re.compile("\d{3}-\d{4}-\d{4}")
       if pattern.match(searchQuery):
           list = doQueryCheck(searchQuery)
           statusMsg["message"] =  "Search completed successfully."
           statusMsg["status"] = "success"
       else:
           statusMsg["message"] =  "Please check the search string pattern."
           statusMsg["status"] = "error"
    else:
        statusMsg["message"] =  "Please provide 13 character length string. Example: 999-9999-9999"
        statusMsg["status"] = "error"
    
    return render_template('index.html', all_levels=list, searchQuery = searchQuery , statusMsg = statusMsg)

def doQueryCheck(searchQuery):
    list = [];
    query = "SELECT id, level1 , ne_list, "
    query += "  nat_list, "
    query += "  dep_list, dep_ex_list, lob "
    query += "FROM pbcs_pl " 
    data = mysql.query_db(query)
    searchParts = searchQuery.split("-")
    
    
    for level in data: 
        if (isExistedInLevel(level,searchParts)):
            list.append(level)
    return list

def isExistedInLevel(level,searchParts):
    print("################## next level ##########")
    print(level)
    _le = searchParts[0]
    _nat = searchParts[1]
    _dep = searchParts[2][:2]
    _lob = searchParts[2][2:]
    
    le = level['ne_list'].split(",")
    nat = level['nat_list'].split(",")
    dep= level['dep_list'].split(",")
    depe = level['dep_ex_list'].split(",")
    lob= level['lob'].split(",")
    isFound = False;
    isFound = isPartExisted(le,_le)
    print("is Legal entity found ? " + giveString(isFound))
    if isFound:
        isFound = isPartExisted(nat,_nat)
    print("is Natural Account found ?" + giveString(isFound))
    if isFound:
        isFound = isPartExisted(dep,_dep)
        print("is Department found ?" + giveString(isFound))  
        if isPartExisted(depe,_dep) :
            isFound = False 
        else:
            isFound = True
        print("is Department Excluded ?" + giveString(isFound))  
        
    if isFound:
        isFound = isPartExisted(lob,_lob) 
        print("is Lob found ?" + giveString(isFound))         
    print(giveString(isFound))
    return isFound

def isPartExisted(list, s):
    print(":part check:")
    print(list)
    print(s)
    for e in list:
        if e.lower() == "all":
            return True
        elif e == s:
            return True
        elif e.find(":") != -1:
            print("it has : data")
            print("we need to process")
            rangs = e.split(":")
            if((int(rangs[0]) <= int(s)) & (int(rangs[1]) >= int(s))):
                return True
    return False

def giveString(isFound):
    if isFound:
        return "True"
    else:
        return "False"



