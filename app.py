#------------------------------------------
#funzioni flask
from flask import Flask, render_template,request,redirect,url_for
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user,
    current_user)
#------------------------------------------


#------------------------------------------
from werkzeug.utils import secure_filename
import os,uuid


from werkzeug.security import generate_password_hash, check_password_hash
#------------------------------------------


#------------------------------------------
#funzioni ausiliarie per database
from aux_functions import(

    get_generi,

    check_subscribe_form,
    nuovo_utente,

    info_giorni,
    get_biglietti,
    get_biglietto_by_id_biglietto,
    
    
    get_acquisto_by_id_utente,
    get__info_giorno_by_id_giorno,
    get_utente_by_id,
    get_utente_by_mail,
    info_incassi_vendite,
    info_bozza,
    db_conferma_modifica,
    

    get_palchi,

    get_artisti,
    check_esistenza_artista_by_nome,
    insert_artista,
    set_artista_as_inattivo,
    
    dati_per_insert_esibizione,
    dati_per_form_filtri,
    db_programmazione,
    get_esibizioni,
    info_esibizioni, 

    non_piu_di_1,
    update_crediti,
    check_capienza,
    transazione_by_user_id,

    User)
#------------------------------------------


#------------------------------------------
#sqlite
import sqlite3
#------------------------------------------



app = Flask(__name__)

app.config['SECRET_KEY'] = "312450IAco"
UPLOAD_FOLDER = 'static/images/artisti'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_utente = get_utente_by_id(user_id)
    if db_utente is not None:
        user = User(id = db_utente[0],
                    nome = db_utente[1],
                    cognome =  db_utente[2],
                    email =db_utente[3],
                    password = db_utente[4],
                    ruolo = db_utente[5],
                    crediti = db_utente[6])
    else:
        user = None

    return user



#------------------------------------------
@app.route("/")
def home():
    db_info_giorni = info_giorni()
    return render_template('index.html',p_giorni = db_info_giorni)
#------------------------------------------


#------------------------------------------
@app.route("/subscribe",methods=["GET"])
def subscribe():
    # se l'utente è gia registrato non può accedere al form
    # per registrarsi
    if current_user.is_authenticated == True:
        return redirect(url_for('home'))
    
    return render_template('subscribe.html')
#------------------------------------------


#------------------------------------------
@app.route("/register",methods=["POST"])
def register():

    nome = request.form.get("nome")
    cognome = request.form.get("cognome")

    email = request.form.get("email")
    re_email= request.form.get("re_email")

    password = request.form.get("password")
    re_password = request.form.get("re_password")

    if check_subscribe_form(email,re_email,password,re_password) == True:

        ruolo = request.form.get("ruolo")

        if ruolo == "client":
            ruolo = 0
        else:
            ruolo = 1   # 1 == ruolo di organizer (ruolo specificato
                        # nel form in "index.html") 

        crediti = 500

        form = request.form.to_dict()
        if form is not None:
            #il valore dei crediti per l'acquisto è un valore arbitrario dato che
            # non è presente un metodo di pagamento
            nuovo_utente(nome,cognome,email,password,ruolo,crediti)

            return redirect(url_for('home'))
        else:
            return redirect(url_for('errore'))
            
    else:
        return redirect(url_for('errore'))
#------------------------------------------


#------------------------------------------
@app.route("/login",methods=["GET"])
def login():
    return render_template("login.html")
#------------------------------------------


#------------------------------------------
@app.route("/autenticazione",methods=["POST"])
def autenticazione():
    
    email = request.form.get('email')
    password = request.form.get('password')

    db_utente = get_utente_by_mail(email)   

    # controllo se esiste quell'utente con quella mail nel db
    if db_utente == None:
        print("ERRORE INDIRIZZO MAIL ERRATO")
        messaggio = "INDIRIZZO MAIL O PASSWORD ERRATI"
        return redirect(url_for('errore',p_messaggio = messaggio))
    else:
        if check_password_hash(db_utente[4],password) == True:
            user = User(
                id = db_utente[0],
                nome = db_utente[1],
                cognome = db_utente[2],
                email =db_utente[3],
                password = db_utente[4],
                ruolo = db_utente[5],
                crediti = db_utente[6])
            login_user(user)
            return redirect(url_for('home'))
        else:
            print("ERRORE:PASSWORD ERRATA")
            messaggio = "INDIRIZZO MAIL O PASSWORD ERRATI"
            return redirect(url_for('errore', p_messaggio = messaggio))  
#------------------------------------------


#------------------------------------------
@app.route("/errore")
def errore():
    messaggio = request.args.get('p_messaggio')
    return render_template("errore.html",messaggio = messaggio)
#------------------------------------------

#------------------------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
#------------------------------------------


#------------------------------------------
@app.route("/utente",methods = ["POST","GET"])
@login_required
def utente():
    id_utente = current_user.id

    # prende le info del biglietto:

    db_info_acquisto = get_acquisto_by_id_utente(id_utente)
    if db_info_acquisto == "ERRORE":
    
        # route per organizzatore
        generi = get_generi()
        # info vendite es incassi
        (db_incassi,db_vendite) = info_incassi_vendite()

        # dati per il form rogrammazione
        (db_nomi_artisti,db_nomi_giorni,db_nomi_palchi) = dati_per_insert_esibizione()

        # dati per la scelta dei filtri
        (db_generi,db_nomi_giorni,db_nomi_palchi) = dati_per_form_filtri()

        #FILTRI SCELTI 
        filtro_genere = request.form.get("genere")
        filtro_giorno = request.form.get("giorno")
        filtro_palco = request.form.get("palco")

        #ESIBIZIONI
        #prende gli id di artisti giorni ecc
        db_esibizioni = get_esibizioni()
        
        esib = info_esibizioni(db_esibizioni,filtro_genere = filtro_genere,
                            filtro_giorno = filtro_giorno,
                            filtro_palco = filtro_palco)
        
        # (organizzatori,artisti,palchi,giorni,ore,generi,status,attive) 
        # elementi iesimi sono della stessa esibizione
        # gli elementi dentro la tupla sono liste 
        # utilizzo poi sul file html la funzione zip per
        # prendere i valori iesimi di ogni tupla

        zip_esib = list(zip(*esib))

        campi = [filtro_genere,filtro_giorno,filtro_palco]
        
        campi = [filtro_genere,filtro_giorno,filtro_palco]
        if all(item is not None and item.strip() != "" for item in campi):
            return render_template("utente.html",p_incassi = db_incassi,p_vendite = db_vendite,
                                p_nomi_artisti = db_nomi_artisti,p_nomi_giorni  = db_nomi_giorni,
                                p_nomi_palchi = db_nomi_palchi,p_generi = generi,
                                p_esib= zip_esib)
        else:
            return render_template("utente.html",p_incassi = db_incassi,p_vendite = db_vendite,
                                p_nomi_artisti = db_nomi_artisti,p_nomi_giorni  = db_nomi_giorni,
                                p_nomi_palchi = db_nomi_palchi,p_generi = db_generi,
                                p_esib= zip_esib)
    else:
        #route utente 
        id_biglietto = db_info_acquisto[0]
        id_giorno = int(db_info_acquisto[1])

        # prende le info del giorno 
        db_info_giorno = get__info_giorno_by_id_giorno(id_giorno)
        db_nome_giorno = db_info_giorno[0]
        # prende le info del biglietto:

        db_biglietto = get_biglietto_by_id_biglietto(id_biglietto)

        return render_template("utente.html",p_errore = "NO",p_biglietto = db_biglietto, p_nome_giorno = db_nome_giorno)
    #------------------------------------------



#------------------------------------------
@app.route("/artisti")
def artisti():
    db_artisti = get_artisti()
    return render_template("artisti.html",p_artisti = db_artisti)
#------------------------------------------



#------------------------------------------
@app.route("/inserisci_artisti",methods=["POST"])
@login_required
def inserisci_artisti():
    if current_user.ruolo == 1:
        if request.form.to_dict() is not None:

            nome = request.form.get("nome")
            if check_esistenza_artista_by_nome(nome) == False:
                # se l'artista non esiste allora si puo procedere
                #all'inserimento

                foto  = request.files["foto"]
                descrizione = request.form.get("descrizione")
                embed = request.form.get("embed")
                genere = request.form.get("genere")

                # Estensione e nome sicuro
                estensione = os.path.splitext(foto.filename)[1]
                nuovo_nome = f"artista_{uuid.uuid4().hex}{estensione}"
                path_locale = os.path.join(app.config['UPLOAD_FOLDER'], nuovo_nome)
                percorso_db = f"images/artisti/{nuovo_nome}"  # relativo alla cartella static

                # Salva il file
                foto.save(path_locale)

                insert_artista(nome,percorso_db,descrizione,embed,genere)
                return redirect(url_for('utente'))

            else:
                return redirect(url_for('errore'))
#------------------------------------------


#------------------------------------------
@app.route("/programmazione",methods=["POST"])
@login_required
def programmamzione():
    if current_user.ruolo == 1:

        user_id  = current_user.id
        nome_artista = request.form.get("nome")
        palco = request.form.get("palco")
        giorno = request.form.get("giorno")
        ora_inizio = request.form.get("ora_inizio")

        if ora_inizio is not None and ora_inizio.strip("") != (""):
            ora_inizio  = int(ora_inizio)

        status = request.form.get("status")

        campi  = [nome_artista,palco,giorno,status]
        if all(item is not None and item.strip() != "" for item in campi):
            if db_programmazione(user_id,nome_artista,palco,giorno,ora_inizio,status) == "ERRORE":
                messaggio = "SLOT OCCUPATO"
                return redirect(url_for('errore',p_messaggio = messaggio))
            else:
                return redirect(url_for('utente'))
        
#------------------------------------------


#------------------------------------------
@app.route("/esibizioni",methods = ["POST","GET"])
def esibizioni():
    (db_generi,db_nomi_giorni,db_nomi_palchi) = dati_per_form_filtri()
    generi = get_generi()
    #FILTRI SCELTI
    filtro_genere = request.form.get("genere")
    filtro_giorno = request.form.get("giorno")
    filtro_palco = request.form.get("palco")
    
 
    #ESIBIZIONI
    #prende gli id di artisti giorni ecc
    db_esibizioni = get_esibizioni()
    
    esib = info_esibizioni(db_esibizioni,filtro_genere = filtro_genere,
                           filtro_giorno = filtro_giorno,
                           filtro_palco = filtro_palco)
    
    # (organizzatori,artisti,palchi,giorni,ore,generi,status,attive) 
    # elementi iesimi sono della stessa esibizione
    # gli elementi dentro la tupla sono liste 
    # utilizzo poi sul file html la funzione zip per
    # prendere i valori iesimi di ogni tupla

    zip_esib = list(zip(*esib))

    campi = [filtro_genere,filtro_giorno,filtro_palco]
    if all(item is not None and item.strip() != "" for item in campi):
        return render_template("esibizioni.html",
                               p_generi = generi,p_nomi_giorni = db_nomi_giorni,p_nomi_palchi = db_nomi_palchi,
                               p_esib= zip_esib)
    else:
        return render_template("esibizioni.html",
                               p_generi = db_generi,p_nomi_giorni  = db_nomi_giorni,p_nomi_palchi = db_nomi_palchi,
                               p_esib = zip_esib)
    
#------------------------------------------

#------------------------------------------
@app.route("/modifica_bozza/<int:id_bozza>",methods = ["POST","GET"])
@login_required
def modifica_bozza(id_bozza):

    if current_user.ruolo == 1:
        generi = get_generi()
        user_id = current_user.id
        bozza_selezionata = info_bozza(id_bozza,user_id)

        # dati per il form rogrammazione
        (db_nomi_artisti,db_nomi_giorni,db_nomi_palchi) = dati_per_insert_esibizione()
        print(dati_per_insert_esibizione())
        return render_template("modifica_bozza.html",
                                p_id_bozza = id_bozza,
                                p_artisti = db_nomi_artisti,p_giorni = db_nomi_giorni,
                                p_palchi = db_nomi_palchi,p_generi = generi,
                                p_bozza = bozza_selezionata)
    else:
        print("NON AUTORIZZATO")
        return render_template("utente.html")
#------------------------------------------

#------------------------------------------
@app.route("/conferma_modifica",methods=["POST"])
@login_required
def conferma_modifica():
    if current_user.ruolo == 1:

        id_bozza = request.form.get("id-bozza")
        nome = request.form.get("nome")
        giorno = request.form.get("giorno")
        palco = request.form.get("palco")
        ora_inizio = request.form.get("ora_inizio")
        genere = request.form.get("genere")
        status = request.form.get("status")

        db_conferma_modifica(id_bozza,nome,palco,giorno,ora_inizio,status,genere)

        return redirect(url_for('utente'))
    else:
        print("NON AUTORIZZATO")
        return redirect(url_for('utente'))
#------------------------------------------


#------------------------------------------
@app.route("/delete_artista/<int:id_artista>")
@login_required
def delete_artista(id_artista):
    set_artista_as_inattivo(id_artista)
    return redirect(url_for('artisti'))
    

#------------------------------------------
@app.route("/palchi")
def palchi():
    db_palchi = get_palchi()
    return render_template('palchi.html',p_palchi = db_palchi)
#------------------------------------------


#------------------------------------------
@app.route("/biglietti")
def biglietti():
    db_biglietti = get_biglietti()
    return render_template("biglietti.html",p_biglietti = db_biglietti)
#------------------------------------------


#------------------------------------------
@app.route("/acquista_biglietto/<int:id>")
def acquista_biglietto(id):
    if current_user.is_authenticated == False:
        print("ERRORE:PASSWORD ERRATA")
        messaggio = "DEVI PRIMA EFFETTUARE IL LOGIN"
        return redirect(url_for('errore', p_messaggio = messaggio))  
    else:
        if current_user.ruolo == 0:

            db_biglietto = get_biglietto_by_id_biglietto(id)

            return render_template("biglietto.html",p_biglietto = db_biglietto)
        else:
            messaggio = "Gli organizzatori non possono comprare biglietti"
            return redirect(url_for('errore',p_messaggio = messaggio))
#------------------------------------------

#------------------------------------------
@app.route("/transazione",methods=["POST"])
@login_required
def transazione():
    user_id = current_user.id
    prezzo  = request.form.get("prezzo")
    id_biglietto = request.form.get("id_biglietto")
    id_giorno = request.form.get("giorno")
    
    #controllo errori
    if update_crediti(user_id,prezzo) == "ERRORE":
        messaggio = "Credito esaurito"
        return redirect(url_for('errore',p_messaggio = messaggio))
    
    if non_piu_di_1(current_user.id) == False:
        messaggio = "Non si può acquistare più di 1 biglietto"
        return redirect(url_for('errore',p_messaggio = messaggio))
    
    if check_capienza() == "Errore":
        messaggio = "Non ci sono più posti"
        return redirect(url_for('errore',p_messaggio = messaggio))
    #controllo errori

    id_biglietto = int(id_biglietto)
    id_giorno = int(id_giorno)

    transazione_by_user_id(user_id,id_biglietto,prezzo,id_giorno)
    return redirect(url_for('palchi'))
#------------------------------------------