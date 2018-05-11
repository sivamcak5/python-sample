from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import csv
import json

app = Flask(__name__)
app.secret_key = 'SuperSecretKey'
mysql = MySQLConnector(app, 'd21a9hpbni3n5r')


@app.route('/')
def root():
    return render_template('index.html', all_levels=getLevels())


@app.route('/levels')
def index():
    return render_template('index.html', all_levels=getLevels())


def getLevels():
    query = "SELECT id, level1 , ne_list, "
    query += "  nat_list, "
    query += "  dep_list, dep_ex_list,lob "
    query += "FROM pbcs_pl"
    return mysql.query_db(query)


@app.route('/levels/new')
def new():
    return render_template('level_new.html' , level={})


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
    errors = validate(request)
    rdata = {
        'level1': request.form['level1'],
        'ne_list': request.form['ne_list'],
        'nat_list': request.form['nat_list'],
        'dep_list': request.form['dep_list'],
        'dep_ex_list': request.form['dep_ex_list'],
        'lob': request.form['lob'],
    }
    
    if len(errors) > 0:
        return render_template('level_new.html', errors=errors, level=rdata)
    query = "SELECT id "
    query += "FROM pbcs_pl WHERE level1 = '{}' ".format(request.form['level1'])
    query += "and ne_list= '{}' ".format(request.form['ne_list'])
    query += "and nat_list= '{}' ".format(request.form['nat_list'])
    query += "and dep_list='{}' ".format(request.form['dep_list'])
    query += "and dep_ex_list='{}' ".format(request.form['dep_ex_list'])
    query += "and lob='{}' ".format(request.form['lob'])
    data = mysql.query_db(query)
    
    if len(data) > 0:
        errors = {'duplicate': 
                  {'msg':'Similar Level found. Do you want to Edit ?',
                   'id':str(data[0]['id']),
                   'level1': request.form['level1'] } }
        return render_template('level_new.html', errors=errors , level=rdata)
    query = "INSERT INTO pbcs_pl (level1, ne_list, nat_list, dep_list, dep_ex_list, lob ) "
    query += "VALUES (:level1, :ne_list, :nat_list, :dep_list, :dep_ex_list, :lob) "
    
    id = mysql.query_db(query, rdata)
    return redirect('/levels')


@app.route('/levels/<id>/destroy')
def destory(id):
    query = "DELETE FROM pbcs_pl WHERE id = {}".format(id)
    mysql.query_db(query)
    return redirect('/levels')


@app.route('/levels/<id>', methods=['POST'])
def update(id):
    
    data = {
    'level1': request.form['level1'],
    'ne_list': request.form['ne_list'],
    'nat_list': request.form['nat_list'],
    'dep_list': request.form['dep_list'],
    'dep_ex_list': request.form['dep_ex_list'],
    'lob': request.form['lob'],
    'id': id,
    }
    errors = validate(request)
    if len(errors) > 0:
        return render_template('level_edit.html', errors=errors , level=data)
    query = "SELECT id "
    query += "FROM pbcs_pl WHERE level1 = '{}' ".format(request.form['level1'])
    query += "and ne_list= '{}' ".format(request.form['ne_list'])
    query += "and nat_list= '{}' ".format(request.form['nat_list'])
    query += "and dep_list='{}' ".format(request.form['dep_list'])
    query += "and dep_ex_list='{}' ".format(request.form['dep_ex_list'])
    query += "and lob='{}' ".format(request.form['lob'])
    query += "and id !={} ".format(id)
    edata = mysql.query_db(query)
    
    if len(edata) > 0:
        errors = {'duplicate': 
                  {'msg':'Similar Level found. Do you want to Edit ?',
                   'id':str(edata[0]['id']),
                   'level1': request.form['level1'] } }
        return render_template('level_edit.html', errors=errors , level=data)
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
    list = [];
    statusMsg = {"status":"", "message":""}
    if len(searchQuery) == 13 :
       pattern = re.compile("\d{3}-\d{4}-\d{4}")
       if pattern.match(searchQuery):
           list = doQueryCheck(searchQuery)
           statusMsg["message"] = "Search completed successfully."
           statusMsg["status"] = "success"
       else:
           statusMsg["message"] = "Please check the search string pattern."
           statusMsg["status"] = "error"
    else:
        statusMsg["message"] = "Please provide 13 character length string. Example: 999-9999-9999"
        statusMsg["status"] = "error"
    
    return render_template('index.html', all_levels=list, searchQuery=searchQuery , statusMsg=statusMsg)


def doQueryCheck(searchQuery):
    return doCodeCheck(searchQuery, getLevels())
    

def doCodeCheck(searchQuery, data):
    searchParts = searchQuery.split("-")
    list = [];
    for level in data: 
        if (isExistedInLevel(level, searchParts)):
            list.append(level)
    return list


def isExistedInLevel(level, searchParts):
#     print("################## next level ##########")
#     print(level)
    _le = searchParts[0]
    _nat = searchParts[1]
    _dep = searchParts[2][:2]
    _lob = searchParts[2][2:]
    
    le = level['ne_list'].split(",")
    nat = level['nat_list'].split(",")
    dep = level['dep_list'].split(",")
    depe = level['dep_ex_list'].split(",")
    lob = level['lob'].split(",")
    isFound = False;
    isFound = isPartExisted(le, _le)
#     print("is Legal entity found ? " + giveString(isFound))
    if isFound:
        isFound = isPartExisted(nat, _nat)
#     print("is Natural Account found ?" + giveString(isFound))
    if isFound:
        isFound = isPartExisted(dep, _dep)
#         print("is Department found ?" + giveString(isFound))  
        if isPartExisted(depe, _dep) :
            isFound = False 
        else:
            isFound = True
#         print("is Department Excluded ?" + giveString(isFound))  
        
    if isFound:
        isFound = isPartExisted(lob, _lob) 
#         print("is Lob found ?" + giveString(isFound))         
#     print(giveString(isFound))
    return isFound


def isPartExisted(list, s):
#     print(":part check:")
#     print(list)
#     print(s)
    for e in list:
        if e.lower() == "all":
            return True
        elif e == s:
            return True
        elif e.find(":") != -1:
#             print("it has : data")
#             print("we need to process")
            rangs = e.split(":")
            if((int(rangs[0]) <= int(s)) & (int(rangs[1]) >= int(s))):
                return True
    return False


def giveString(isFound):
    if isFound:
        return "True"
    else:
        return "False"


@app.route('/batch-finder')
def batchFinder():
    return render_template('batch-finder.html') 


def decode_utf8(input_iterator):
    for l in input_iterator:
        yield l.decode('utf-8')


@app.route('/batch-finder/upload' , methods=['POST'])
def upload():
    reader = csv.DictReader(decode_utf8(request.files['file']))
    jsonArray = []
    data = getLevels()
    
    for row in reader:
#         json.dump(row, jsonfile)
#         jsonfile.write('\n')
        rowJsonStr = json.dumps(row)
        rowJson = json.loads(rowJsonStr)
        print(rowJson['Code Combo'])
        levels = doCodeCheck(rowJson['Code Combo'], data)
        print(levels)
        if  len(levels) > 0:
            level = "";
            for l in levels:
                level = level + l['level1'] + ","
            if level != "":
                level = level[:-1]
            rowJson['Levels'] = level
            print(rowJson)
        else:
            rowJson['Levels'] = "NA"
        jsonArray.append(rowJson)
#         print(json.dumps(row, indent=4))
    print(jsonArray)

    return render_template('batch-finder.html', all_levels=jsonArray) 


def validate(request):
    level1 = request.form['level1']
    ne_list = request.form['ne_list'] 
    nat_list = request.form['nat_list']
    dep_list = request.form['dep_list']
    dep_ex_list = request.form['dep_ex_list']
    lob = request.form['lob']
    errors = {};
    if level1 != '':
        print(len(level1))
        if len(level1) < 2 or len(level1) > 150:
            errors['level1'] = 'Level1 length should be greater than 2 and less than 150.'
    else:
        errors['level1'] = 'Level1 is required'
    
    if ne_list != '':
        if len(ne_list) < 2 or len(ne_list) > 500:
            errors['ne_list'] = 'LE list length should be greater than 2 and less than 500.'
        else:
            fv = validateList(ne_list, 3)
            if fv != 'ok' :
                errors['ne_list'] = 'LE List : ' + fv;
    else:
        errors['ne_list'] = 'LE list is required'
        
    if nat_list != '':
        if len(nat_list) < 2 or len(nat_list) > 500:
            errors['nat_list'] = 'NAT List length should be greater than 2 and less than 500.'
        else:
            fv = validateList(nat_list, 4)
            if fv != 'ok' :
                errors['nat_list'] = 'NAT List : ' + fv;
    else:
        errors['nat_list'] = 'NAT List is required'
        
    if dep_list != '':
        if len(dep_list) < 1 or len(dep_list) > 500:
            errors['dep_list'] = 'DEP List length should be greater than 1 and less than 500.'
        else:
            fv = validateList(dep_list, 2)
            if fv != 'ok' :
                errors['dep_list'] = 'DEP List : ' + fv;
    else:
        errors['dep_list'] = 'DEP List is required'
    
    if lob != '':
        if len(lob) < 1 or len(lob) > 500:
            errors['lob'] = 'LOB length should be greater than 1 and less than 500.'
        else:
            fv = validateList(lob, 2)
            if fv != 'ok' :
                errors['lob'] = 'LOB : ' + fv;
    else:
        errors['lob'] = 'LOB is required'
        
    if dep_ex_list != '':
        if len(dep_ex_list) < 1 or len(dep_ex_list) > 500:
            errors['dep_ex_list'] = 'DEPT Ex List length should be greater than 1 and less than 500.'
        else:
            fv = validateList(dep_ex_list, 2)
            if fv != 'ok' :
                errors['dep_ex_list'] = 'DEP Ex List : ' + fv;
    
    return errors


def validateList(lstField, fl):
    
    if lstField.lower() != "all":
        if lstField.lower().find("all") != -1:
            return "ALL is not allowed with other tokens. "
        lstParts = lstField.split(",")
        for lp in lstParts:
            if lp.find(":") != -1:
                # do something
                rangs = lp.split(":")
                if len(rangs[0]) != fl or len(rangs[1]) != fl:
                    return "Length of the token (" + lp + ") is wrong."
                elif (int(rangs[0]) > int(rangs[1])):
                    return "Range of the token (" + lp + ") is wrong. lower boundary should be less than upper boundary."
                    
            elif len(lp) != fl:
                return "Length of the token (" + lp + ") is wrong."
                
    return 'ok'   
            
        
# app.run(debug=True)
