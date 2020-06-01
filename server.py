import sqlite3

from flask import Flask, render_template, request, redirect, abort

app = Flask(__name__)

db = "ristorante.db"


@app.route('/')
def root():
    return render_template('index.html')


# menu per cameriere con quantità piatti e bevande
# differenza ricavi costi


@app.route('/gestore_login', methods=['GET', 'POST'])
def gestore_login():
    file = open('pwdGest.txt', 'r')

    pwdGiusta = file.read()
    file.close()
    pwdTemp = request.form.get('pwd')
    if pwdTemp == pwdGiusta:
        return redirect('/gestore', code=302)

    return render_template('gestore_login.html', pwd=pwdTemp)


@app.route('/gestoreDir/ordinabili', methods=['GET', 'POST'])
def ordinabili():
    operation = request.form.get('op', '')
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    if operation == 'ins_piatto':
        nomepiatto = request.form.get('nome_piatto')
        sezione = request.form.get('sezione')
        tempoprep = request.form.get('tempo_prep')
        prezzopiatto = request.form.get('prezzo_piatto')
        cursor.execute("INSERT INTO piatto VALUES (?,?,?,?)", [nomepiatto, sezione, tempoprep, prezzopiatto])
        connection.commit()
    elif operation == 'del_piatto':
        nomepiatto = request.form.get('piatto')
        cursor.execute("DELETE FROM piatto WHERE nome = ?", [nomepiatto])
        connection.commit()
    elif operation == 'ins_bibita':
        nomebibita = request.form.get('nome_bibita')
        categoria = request.form.get('categoria')
        prezzobibita = request.form.get('prezzo_bibita')
        cursor.execute("INSERT INTO bevanda VALUES (?,?,?)", [nomebibita, categoria, prezzobibita])
        connection.commit()
    elif operation == 'del_bibita':
        nomebibita = request.form.get('bibita')
        cursor.execute("DELETE FROM bevanda WHERE nome = ?", [nomebibita])
        connection.commit()

    cursor.execute("SELECT * FROM piatto")
    piatti = cursor.fetchall()
    cursor.execute("SELECT * FROM bevanda")
    bevande = cursor.fetchall()
    connection.close()
    return render_template('gestoreDir/ordinabili.html', piatti=piatti, bevande=bevande)


@app.route('/gestoreDir/gestione_menu', methods=['GET', 'POST'])
def gestione_menu():
    # selezione giorno per il menu
    op = request.form.get('operation', 'del')
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("SELECT nome FROM piatto")
    piatti = cursor.fetchall()

    if op == 'ins':
        datamenu = request.form.get('data_menu', '')
        menudesc = request.form.get('menu_desc', '')
        cursor.execute("INSERT INTO menu_giornaliero VALUES (?,?)", [datamenu, menudesc])
        connection.commit()
    elif op == 'del':
        datadel = request.form.get('data_del')
        cursor.execute("DELETE FROM menu_giornaliero WHERE data = ?", [datadel])
        connection.commit()

    cursor.execute("SELECT * FROM menu_giornaliero")
    menu = cursor.fetchall()
    connection.close()
    return render_template('gestoreDir/gestione_menu.html', piatti=piatti, len=len(piatti), menu=menu)


@app.route('/menu')
def visione_menu():
    return render_template('/menu.html')


@app.route('/gestore')
def gestore():
    return render_template('gestore.html')


@app.route('/cameriere_login', methods=['GET', 'POST'])
def cameriere_login():
    user = request.form.get('user')
    pwd = request.form.get('pwd')

    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM cameriere WHERE userid=? AND password=?", [user, pwd])
    rows = cursor.fetchall()
    connection.close()
    if len(rows) == 1:
        return redirect('/cameriere', code=302)

    return render_template('cameriere_login.html', user=user, pwd=pwd)


@app.route('/reset')
def reset():
    connection = sqlite3.connect(db)

    connection.execute('DROP TABLE IF EXISTS cameriere;')
    connection.execute('DROP TABLE IF EXISTS piatto;')
    connection.execute('DROP TABLE IF EXISTS menu_giornaliero;')
    connection.execute('DROP TABLE IF EXISTS bevanda;')
    connection.execute('DROP TABLE IF EXISTS proposte;')
    connection.execute('DROP TABLE IF EXISTS tavolo;')
    connection.execute('DROP TABLE IF EXISTS prodotto')
    connection.execute('DROP TABLE IF EXISTS piatto_prodotto')
    # connection.execute('DROP TABLE IF EXISTS cameriere;')
    connection.execute('CREATE TABLE cameriere (userid VARCHAR NOT NULL PRIMARY KEY, password VARCHAR);')
    connection.execute(
        'CREATE TABLE piatto (nome VARCHAR NOT NULL PRIMARY KEY,  sezione VARCHAR, tempo_preparazione FLOAT, prezzo FLOAT);')
    connection.execute('CREATE TABLE menu_giornaliero (data DATE NOT NULL PRIMARY KEY, descrizione VARCHAR);')
    connection.execute('CREATE TABLE bevanda (nome VARCHAR NOT NULL PRIMARY KEY, categoria VARCHAR, prezzo FLOAT);')
    connection.execute(
        'CREATE TABLE proposte (dataMenu DATE NOT NULL REFERENCES menu_giornaliero(data), nomePiatto VARCHAR NOT NULL REFERENCES piatto(nome), PRIMARY KEY(dataMenu, nomePiatto));')
    # connection.execute('CREATE TABLE cameriere (userid VARCHAR PRIMARY KEY, password VARCHAR);')
    connection.execute('CREATE TABLE tavolo (numero INTEGER PRIMARY KEY, posti INTEGER NOT NULL, esterno BOOLEAN);')
    connection.execute('CREATE TABLE prodotto (id VARCHAR PRIMARY KEY, costo FLOAT, data_scad DATE, descr VARCHAR, qta_disp INTEGER, conserv VARCHAR);')
    connection.execute('CREATE TABLE piatto_prodotto (nomePiatto VARCHAR REFERENCES piatto(nome), idProdotto VARCHAR REFERENCES prodotto(id), qta INTEGER, PRIMARY KEY (nomePiatto, idProdotto));')

    connection.commit()
    connection.close()
    return "OK"


@app.route('/gestoreDir/personale', methods=['GET', 'POST'])
def personale():
    user = request.form.get('user')
    pwd = request.form.get('pwd')
    operation = request.form.get('operation', 'del')
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    if operation == "del":
        cursor.execute("DELETE FROM cameriere WHERE userid = ?", [user])
        connection.commit()

    else:
        cursor.execute("INSERT INTO cameriere VALUES (?,?)", [user, pwd])
        connection.commit()

    cursor.execute("SELECT * FROM cameriere ")
    rows = cursor.fetchall()
    connection.close()

    return render_template('gestoreDir/personale.html', camerieri=rows, user=user, pwd=pwd, operation=operation)


@app.route('/gestoreDir/gestione_tavoli', methods=['GET', 'POST'])
def gestione_tavoli():
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    operation = request.form.get('operation')


    if operation == 'ins':
        number = request.form.get('number')
        posti = request.form.get('posti')
        est = request.form.get('esterno', 'interno')=='esterno'
        connection.execute("INSERT INTO tavolo VALUES (?,?,?)", [number, posti, est])
        connection.commit()

    if operation == 'del':
        number = request.form.get('numberC')
        connection.execute("DELETE FROM tavolo WHERE numero = ?", [number])
        connection.commit()

    cursor.execute("SELECT * FROM tavolo")
    rows = cursor.fetchall()
    connection.close()

    return render_template('gestoreDir/gestione_tavoli.html', tavoli = rows)


@app.route('/gestoreDir/gestione_prodotti', methods=['GET', 'POST'])
def gestione_prodotti():
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    operation = request.form.get('operation')


    if operation == 'ins':
        id = request.form.get('id')
        costo = request.form.get('costo')
        data_scadenza = request.form.get('data_scadenza')
        descr = request.form.get('descr')
        qta = request.form.get('qta')
        conserv = request.form.get('conserv')

        connection.execute("INSERT INTO prodotto VALUES (?,?,?,?,?,?)", [id,costo,data_scadenza,descr,qta,conserv])
        connection.commit()

    if operation == 'del':
        id = request.form.get('IDC')
        connection.execute("DELETE FROM prodotto WHERE id = ?", [id])
        connection.commit()

    cursor.execute("SELECT * FROM prodotto")
    rows = cursor.fetchall()
    connection.close()

    return render_template('gestoreDir/gestione_prodotti.html', prodotti = rows)


@app.route('/gestoreDir/gestione_necessita', methods=['GET', 'POST'])
def gest_nec():
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    nomePiatto = request.form.get('nomePiatto')
    idProdotto = request.form.get('idProdotto')
    qta = request.form.get('qta')

    cursor.execute('SELECT nome FROM piatto WHERE nome =?', [nomePiatto])
    nomeEstr = cursor.fetchone()

    cursor.execute('SELECT id FROM prodotto WHERE id = ?', [idProdotto])
    idEstr = cursor.fetchone()

    cursor.execute('INSERT INTO piatto_prodotto VALUES (?,?,?)', [nomePiatto, idProdotto, qta])
    connection.commit()

    cursor.execute('SELECT * FROM piatto_prodotto')
    rows = cursor.fetchall()
    connection.close()

    return render_template('/gestoreDir/gest_necessita.html', rows=rows)


app.run(host="127.0.0.1", port=5000, debug=True)