import sqlite3
from flask import redirect,url_for
from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash
#---------------------------------------------------------------------------------------
#--------------------
# BLOCCO FUNZINONI PER 'subscribe.html'

def check_subscribe_form(email,re_email,password,re_password):
    if (email == re_email and password == re_password 
        and email != "" and password != ""):
        return True
    else:
        return False

def nuovo_utente(nome,cognome,email,password,ruolo,crediti):
    hashed_password = generate_password_hash(password)
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""INSERT INTO utenti (nome,cognome,email,password,ruolo,crediti) 
              VALUES (?,?,?,?,?,?)""",
              (nome,cognome,email,hashed_password,ruolo,crediti))

    conn.commit()
    conn.close()

    print("""
          ***
          Iscrizione effettuata con successo
          ***
          """)
    return

#--------------------
#---------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------
#--------------------
# BLOCCO FUNZINONI PER 'palchi.html'

def get_palchi():
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM palchi")
    
    palchi = c.fetchall()

    conn.commit()
    conn.close()

    print("""COMANDO ESEGUITO CON SUCCESSO""")


    return palchi

#--------------------
#---------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------
#--------------------
# BLOCCO FUNZINONI PER 'biglietti.html'

def info_giorni():
    conn = sqlite3.connect("database.db")
    c  = conn.cursor()

    c.execute("SELECT nome,capienza FROM giorni")

    info_giorno = c.fetchall()

    conn.commit()
    conn.close()

    return info_giorno

def get_biglietti():

    conn = sqlite3.connect('database.db')
    c =conn.cursor()

    c.execute("SELECT * FROM biglietti")

    biglietti = c.fetchall()

    conn.commit()
    conn.close()

    print("""COMANDO ESEGUITO CON SUCCESSO""")

    return biglietti

def get_biglietto_by_id_biglietto(id):
    # l'id è del biglietto
    conn = sqlite3.connect('database.db')
    c =conn.cursor()

    c.execute("SELECT * FROM biglietti WHERE id=?",(id,))

    biglietti = c.fetchone()

    conn.commit()
    conn.close()

    print("""COMANDO ESEGUITO CON SUCCESSO""")

    return biglietti

#--------------------
#---------------------------------------------------------------------------------------



#---------------------------------------------------------------------------------------
#--------------------
# BLOCCO FUNZINONI PER L'ACQUISTO DEI BIGLIETTI

def non_piu_di_1(user_id):

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT 1 FROM biglietti_acquistati WHERE id_utente = ?",(user_id,))

    result = c.fetchone()

    conn.commit()
    conn.close()

    if result is None:
        return True
    else:
        return False

def update_crediti(id,prezzo):
     #-----------------------------------------------
    # Prende i crediti dell'untente loggato
    prezzo = int(prezzo)
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT crediti FROM utenti WHERE id=?",(id,))

    credito_precedente = c.fetchone()[0]

    nuovo_credito = credito_precedente-prezzo

    if nuovo_credito > 0:
        conn.commit()
        conn.close()
    else:
        messaggio = "povero"
        return "ERRORE"
 
    # update dei crediti dell'utente a seconda del prezzo del biglietto
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE utenti SET crediti=? WHERE id=?",(nuovo_credito,id))

    conn.commit()
    conn.close()
    #-----------------------------------------------
    return

def insert_biglietto(id,id_biglietto,id_giorno):

    id_biglietto = int(id_biglietto)
    id_giorno = int(id_giorno)

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("""INSERT  INTO biglietti_acquistati 
              (id_utente,id_biglietto,id_giorno) 
              VALUES(?,?,?)""",(id,id_biglietto,id_giorno))
    
    conn.commit()
    conn.close()

    return

def check_capienza():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT capienza FROM giorni")

    capienze = c.fetchall()
    for capienza in capienze:
        if capienza[0] < 1:
            return "Errore"

def transazione_by_user_id(id,id_biglietto,prezzo,id_giorno):
    #-----------------------------------------------
    # insert del biglietto acquistato nella tabella biglietti_acquistati
    insert_biglietto(id,id_biglietto,id_giorno)
    #----------------------------------------------

    #caso biglietto oro
    unit = 1
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    if id_biglietto == 1:

        c.execute("UPDATE biglietti SET venduti = venduti + 1 WHERE id = ? ",(id_biglietto,))

        for giorno in range(1, 4):

            c.execute("SELECT capienza FROM giorni WHERE id=?",(giorno,))
            conn.commit()

            result = c.fetchone()[0]
        
            if result > 0:

                c = conn.cursor()
                c.execute("UPDATE giorni SET capienza= capienza - ? WHERE id=?",(unit,giorno))
                conn.commit()

    #caso biglietto oro

    #caso biglietto argento
    if id_biglietto == 2:
        c.execute("UPDATE biglietti SET venduti = venduti + 1 WHERE id = ? ",(id_biglietto,))
        count = 0
        for i in range(0, 2):
            giorno = id_giorno + count

            c.execute("SELECT capienza FROM giorni WHERE id=?",(giorno,))
            conn.commit()

            result = c.fetchone()[0]

            if result > 0:
             
                c.execute("UPDATE giorni SET capienza=capienza - ? WHERE id=?",(unit,giorno))
                conn.commit()
                count = count + 1

        
    #caso biglietto argento

    #caso biglietto bronzo
    if id_biglietto == 3:

        c.execute("UPDATE biglietti SET venduti = venduti + 1 WHERE id = ? ",(id_biglietto,))

        c.execute("SELECT capienza FROM giorni WHERE id=?",(id_giorno,))
        conn.commit()
        result = c.fetchone()[0]

        if result > 0:
            c.execute("UPDATE giorni SET capienza=capienza - ? WHERE id=?",(unit,id_giorno))
            conn.commit()

    conn.commit()
    conn.close()


    #caso biglietto bronzo

    #----------------------------------------------
    
    print("""COMANDO ESEGUITO CON SUCCESSO""")
    return

#--------------------
#---------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------
#--------------------
# BLOCCO FUNZINONI PER PROFILO UTENTE ('utente.html')

def get_acquisto_by_id_utente(id_utente):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()


    c.execute("SELECT id_biglietto,id_giorno FROM biglietti_acquistati WHERE id_utente=?",(id_utente,))
    info_biglietto = c.fetchone()
    if info_biglietto is None:
        return "ERRORE"
    else:
        conn.commit()
        conn.close() 
        return info_biglietto

def get__info_giorno_by_id_giorno(id_giorno):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT nome,capienza FROM giorni WHERE id = ?",(id_giorno,))
    info_giorno =c.fetchone()
    conn.commit()
    conn.close()

    return info_giorno

def get_utente_by_id(id):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM utenti WHERE id = ?",(id,))

    utente = c.fetchone()

    conn.commit()
    conn.close()

    return utente

def get_utente_by_mail(email):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM utenti WHERE email= ?", (email,) )

    utente = c.fetchone()

    conn.commit()
    conn.close()

    return utente

# FUNZIONI PER ORGANIZZATORE
def info_incassi_vendite():
    conn = sqlite3.connect("database.db")    
    c = conn.cursor()

    c.execute("SELECT id_biglietto FROM biglietti_acquistati")

    biglietti_acquistati = c.fetchall()
    incassi = 0

    for biglietto_acquistato in biglietti_acquistati:
         
         id_biglietto_acquistato = biglietto_acquistato[0]

         c.execute("SELECT prezzo FROM biglietti WHERE id = ?",(id_biglietto_acquistato,))
         prezzo = c.fetchone()[0]

         incassi = incassi + prezzo

    c.execute("SELECT nome,venduti FROM biglietti")
    vendite = c.fetchall()

    conn.commit()
    conn.close()
    return (incassi,vendite)

def info_bozza(id_bozza,user_id):
    #prende tutte le caratteristiche della bozza da modificare

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    info_bozza_selezionata = []
    #c.execute("SELECT nome FROM palchi")
    #nomi_palchi = c.fetchall()

    c.execute("SELECT * FROM programmazione where id_organizzatore = ? AND id = ?",(user_id,id_bozza))
    bozza = c.fetchone()


    c.execute("SELECT nome FROM artisti where id = ?",(bozza[2],))
    artista = c.fetchone()
    info_bozza_selezionata.append(artista[0])

    c.execute("SELECT nome FROM palchi WHERE id = ?",(bozza[3],))
    palco = c.fetchone()
    info_bozza_selezionata.append(palco[0])

    c.execute("SELECT nome FROM giorni WHERE id = ?",(bozza[4],))
    giorno = c.fetchone()
    info_bozza_selezionata.append(giorno[0])

    ora_inizio = bozza[5]
    ora_fine = bozza[6]
    genere = bozza[8]

    info_bozza_selezionata.append(ora_inizio)
    info_bozza_selezionata.append(ora_fine)
    info_bozza_selezionata.append(genere)

    conn.commit()
    conn.close()

    return info_bozza_selezionata

def db_conferma_modifica(id_bozza,nome,palco,giorno,ora_inizio,status,genere):
    
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    ora_inizio = int(ora_inizio)
    status = int(status)
    id_bozza = int(id_bozza)

    c.execute("SELECT status FROM programmazione WHERE id = ?",(id_bozza,))
    risultato = c.fetchone()[0]
    if risultato == 0:

        c.execute("SELECT id FROM artisti WHERE nome = ?",(nome,))
        id_artista = c.fetchone()[0]

        c.execute("SELECT id FROM palchi WHERE nome = ?",(palco,))
        id_palco = c.fetchone()[0]

        c.execute("SELECT id FROM giorni WHERE nome = ?",(giorno,))
        id_giorno = c.fetchone()[0]


        c.execute("""UPDATE programmazione SET id_artista = ?, id_palco = ?, id_giorno = ?,
                orario_inizio = ?, orario_fine = ?, status = ?, 
                genere = ? WHERE id = ?""",(id_artista,id_palco,id_giorno,ora_inizio,ora_inizio + 1,status,genere,id_bozza))
        conn.commit()
        conn.close()
        return
    else:
        return
#--------------------
#---------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------
#--------------------
# BLOCCO FUNZINONI PER 'artisti.html' e per L'INSERIMENTO DEGLI ARTISTI 

def get_artisti():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM artisti")

    artisti =  c.fetchall()

    conn.commit()
    conn.close()

    return artisti

def check_esistenza_artista_by_nome(nome):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    #controllo se l'artista gia esiste
    c.execute("SELECT nome FROM artisti WHERE nome = ?",(nome,))

    if c.fetchone() is not None :   
        return True
    else:
        return False
    
def insert_artista(nome,percorso,descrizione,embed,genere):

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("INSERT INTO artisti (nome,foto,descrizione,embed,attivo,genere) VALUES(?,?,?,?,?,?)",(nome,percorso,descrizione,embed,1,genere))

    conn.commit()
    conn.close()

    print("sucesso")
    return

def set_artista_as_inattivo(id_artista):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("UPDATE artisti SET attivo = ? WHERE id=?",(0,id_artista,))
    print("wow")

    conn.commit()
    conn.close()

    return

#--------------------
#---------------------------------------------------------------------------------------



#---------------------------------------------------------------------------------------
#--------------------
# BLOCCO FUNZINONI PER 'esibizioni.html'

def dati_per_insert_esibizione():

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT nome FROM artisti")
    nomi_artisti = c.fetchall()

    c.execute("SELECT nome FROM giorni")
    nomi_giorni = c.fetchall()

    c.execute("SELECT nome FROM palchi")
    nomi_palchi = c.fetchall()

    return(nomi_artisti,nomi_giorni,nomi_palchi)

def dati_per_form_filtri():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT nome FROM generi")
    generi = []

    risultati = c.fetchall()
    for risultato in risultati:
        generi.append(risultato[0])

    c.execute("SELECT nome FROM giorni")

    nome_giorni = c.fetchall()

    c.execute("SELECT nome FROM palchi")
    nome_palchi = c.fetchall()

    conn.commit()
    conn.close() 
    return (generi,nome_giorni,nome_palchi)

def db_programmazione(user_id,nome_artista,nome_palco,giorno,ora_inizio,status):
    ora_fine = ora_inizio + 1

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT id,genere FROM artisti WHERE nome =?",(nome_artista,))
    riga = c.fetchone()
    (id_artista,genere) = (riga[0],riga[1])

    c.execute("SELECT id FROM palchi WHERE nome =?",(nome_palco,))
    id_palco  = c.fetchone()[0]

    c.execute("SELECT id FROM giorni WHERE nome =?",(giorno,))
    id_giorno = c.fetchone()[0]

    c.execute("""
    SELECT * FROM programmazione 
    WHERE id_palco = ? AND id_giorno = ? AND orario_inizio = ? AND orario_fine = ?
    """, (id_palco, id_giorno, ora_inizio, ora_fine))
    
    esibizioni = c.fetchall()
    if not esibizioni:

        c.execute("""INSERT INTO programmazione 
                (id_organizzatore,id_artista,id_palco,id_giorno,orario_inizio,orario_fine,status,genere)
                VALUES(?,?,?,?,?,?,?,?)""",
                (user_id,id_artista,id_palco,id_giorno,ora_inizio,ora_fine,status,genere))
        
        conn.commit()
        conn.close()
        return
    else:
        conn.commit()
        conn.close()
        return "ERRORE"

def get_esibizioni():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    
    c.execute("SELECT * FROM programmazione ORDER BY id")
    esibizioni = c.fetchall()
    conn.close()

    return esibizioni

def info_esibizioni(esibizioni,**kwargs):
    filtro_genere = kwargs.get("filtro_genere", "tutti")
    filtro_giorno = kwargs.get("filtro_giorno", "tutti")
    filtro_palco = kwargs.get("filtro_palco", "tutti")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    organizzatori = []
    artisti = []
    foto = []
    palchi = []
    giorni = []
    ore = []
    generi = []
    attive = []
    id_esibizioni = []

    for esibizione in esibizioni:
        c.execute("SELECT id FROM utenti WHERE id = ?", (esibizione[1],))
        organizzatore = c.fetchone()[0]

        c.execute("SELECT nome, foto FROM artisti WHERE id = ?", (esibizione[2],))
        nome_foto = c.fetchone()
        artista = nome_foto[0]
        foto_artista = nome_foto[1]

        c.execute("SELECT nome FROM palchi WHERE id = ?", (esibizione[3],))
        palco = c.fetchone()[0]

        c.execute("SELECT nome FROM giorni WHERE id = ?", (esibizione[4],))
        giorno = c.fetchone()[0]

        c.execute("SELECT orario_inizio FROM programmazione WHERE orario_inizio = ?", (esibizione[5],))
        ora = c.fetchone()[0]

        c.execute("SELECT genere FROM programmazione WHERE genere = ?", (esibizione[8],))
        genere_ = c.fetchone()
        genere = genere_[0]

        c.execute("SELECT id,status FROM programmazione WHERE id = ?", (esibizione[0],))
        risultati = c.fetchone()
        id_esibizione = risultati[0]
        status = risultati[1]

        # Applica i filtri qui, se tutti o corrispondono
        if (filtro_genere == "tutti" or genere == filtro_genere) and \
           (filtro_giorno == "tutti" or giorno == filtro_giorno) and \
           (filtro_palco == "tutti" or palco == filtro_palco):
            
            organizzatori.append(organizzatore)
            artisti.append(artista)
            foto.append(foto_artista)
            palchi.append(palco)
            giorni.append(giorno)
            ore.append(ora)
            generi.append(genere)
            attive.append(status)
            id_esibizioni.append(id_esibizione)

    return (organizzatori, artisti, foto, palchi, giorni, ore, generi,attive,id_esibizioni)

#--------------------
#---------------------------------------------------------------------------------------


def get_generi():
    conn = sqlite3.connect("database.db")
    c =conn.cursor()

    c.execute("SELECT nome FROM generi")
    generi = []

    risultati = c.fetchall()
    for risultato in risultati:
        generi.append(risultato[0])

    conn.close()

    return generi

class User(UserMixin):
    def __init__(self,id,nome,cognome,email,password,ruolo,crediti):
        self.id = id
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.password = password
        self.ruolo = ruolo
        self.crediti = crediti

