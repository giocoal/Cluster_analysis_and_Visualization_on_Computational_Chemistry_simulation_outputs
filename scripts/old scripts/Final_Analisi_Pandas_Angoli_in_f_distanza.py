import numpy as np
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import pdist, squareform
import csv
import os
import pandas as pd
import timeit
import math
import matplotlib.pyplot as plt

start = timeit.default_timer()
# COSTANTI FONDAMENTALI
cartella_e_nome_output = "Replica1"
path_cartella = 'C:\\Users\\Giorgio\\Desktop\\Tirocinio\\Dati\\Solo_H2O\\' + cartella_e_nome_output #cartella contenente i files.pdb
path_output_clusterizzazione = "C:\\Users\\Giorgio\\Desktop\\Tirocinio\\Risultati\\Clusterizzazione_Angoli_H2O_in_funzione_della_distanza\\" + cartella_e_nome_output + ".txt"
path_output_angoli = "C:\\Users\\Giorgio\\Desktop\\Tirocinio\\Risultati\\Clusterizzazione_Angoli_H2O_in_funzione_della_distanza\\" + cartella_e_nome_output + "_angoli_distanza" + ".txt"
numero_di_frame = 3000 #numero di frame da analizzare per ogni file

# *** FUNZIONI ***
def nuovi_indici(vecchi_indici):
    indici_o_nuovi = np.array(vecchi_indici + (vecchi_indici*2))
    indici_h1_nuovi = np.array(indici_o_nuovi + 1)
    indici_h2_nuovi = np.array(indici_o_nuovi + 2)
    return indici_o_nuovi, indici_h1_nuovi, indici_h2_nuovi

def periodicita(L = 39.606): #L larghezza della scatola
    total = 0
    for d in range(data_solo_ossigeno.shape[1]):
        pd = pdist(data_solo_ossigeno[:, d].reshape(-1, 1))
        if (d != 2):
            pd[pd > (0.5 * L)] -= L
        total += pd ** 2

    total = np.sqrt(total)
    square = squareform(total)
    return square

def outofbox():
    # TEST PER VALORI DI |X,Y| MAGGIORI DI 19.803 - OVVERO L/2
    data_solo_ossigeno[:, :2] = np.where((data_solo_ossigeno[:, :2] > 19.803) & (((data_solo_ossigeno[:, :2] // 19.803) % 2) == 1), (-(19.803) + (data_solo_ossigeno[:, :2] % 19.803)), data_solo_ossigeno[:, :2])
    data_solo_ossigeno[:, :2] = np.where((data_solo_ossigeno[:, :2] > 19.803) & (((data_solo_ossigeno[:, :2] // 19.803) % 2) == 0), data_solo_ossigeno[:, :2] % 19.803, data_solo_ossigeno[:, :2])
    # test per valori di x,y minori di -20
    data_solo_ossigeno[:, :2] = np.where((data_solo_ossigeno[:, :2] < (-19.803)) & (((data_solo_ossigeno[:, :2] // (-19.803)) % 2) == 1),
                                         [+19.803 + (data_solo_ossigeno[:, :2] % (-19.803))], data_solo_ossigeno[:, :2])
    data_solo_ossigeno[:, :2] = np.where((data_solo_ossigeno[:, :2] < (-19.803)) & (((data_solo_ossigeno[:, :2] // (-19.803)) % 2) == 0), data_solo_ossigeno[:, :2] % (-19.803),
                                         data_solo_ossigeno[:, :2])
    return data_solo_ossigeno

def clusterizzazione(eps=4, min_samples=3):

    db = DBSCAN(eps,min_samples,metric='precomputed')
    db.fit_predict(periodicita())
    db_labels = db.labels_

    """fig = plt.figure()
    ax = Axes3D(fig)
    ax.set_xlim3d(-19.803, 19.803)
    ax.set_ylim3d(-19.803, 19.803)
    ax.set_zlim3d(-25, +25)
    ax.scatter(data[:, 0], data[:, 1], data[:, 2], c=db.labels_, s=150)
    ax.view_init(azim=200)
    plt.show()
    plt.close()"""

    #n_clusters_ = len(set(db_labels)) - (1 if -1 in db_labels else 0)
    #n_noise_ = list(db_labels).count(-1) NON SERVE
    n_elements_clusters = np.bincount(db_labels[db_labels >= 0])

    return n_elements_clusters, db_labels

def calcolo_angoli(dataset,indici_O,indici_H1,indici_H2):
    """Creo una lista vuota che ospiterà gli angoli dei clusters(indipendentemente da che siano isole o altro
    questa distinzione viene fatta prima di richiamare la funzione"""
    lista_liste_angoli = []
    """#Ottengo dalla lista una LISTA DI LISTE, ogni lista conterrà gli angoli per le molecole d'acqua a diverse distanze dalla
    #superficie, a step di 0.5 (ipotizzando che la superficie sia a 6.0 A),l'algoritmo riconosce il numero di settori
    da creare sulla base dell'inizio e la fine dell'area da suddividere e della lunghezza dello step"""
    # Praticamente poi si suddivide z in tanti "settori" lunghi 0.5 A, gli angoli delle molecole d'acqua appartenenti ad un
    # Determinato settore saranno assegnate ad un valore di distanza corrispondente al limite massimo del settore
    # questo significa che tutto ciò che si trova tra
    # ad esempio, 6.5 e 7, sarà assegnato alla posizione 7, ma indicherà che si trova tra la posizione 7 e quella precedente
    for i in np.arange(6.5, 25.5, 0.5):
        lista_liste_angoli.append([])
    "Segue il calcolo vero e proprio, che si concentrerà su una molecola d'acqua alla volta"
    for count_angoli in range(0,len(indici_O)):
        # Coordinate 3D acqua
        O = dataset[(indici_O[count_angoli]),:]
        H1 = dataset[(indici_H1[count_angoli]),:]
        H2 = dataset[(indici_H2[count_angoli]),:]
        # Array legami
        d_OH1 = H1 - O
        d_OH2 = H2 - O
        # Vettore totale acqua
        v_H2O = d_OH1 + d_OH2
        # Normalizzazione vettore acqua
        norma_v_H2O = math.sqrt(v_H2O[0] ** 2 + v_H2O[1] ** 2 + v_H2O[2] ** 2)
        v_H2O_normalized = [v_H2O[0] / norma_v_H2O, v_H2O[1] / norma_v_H2O, v_H2O[2] / norma_v_H2O]
        # Dichiarazione Normale a superficie
        if O[2] > 0:
            normale = [0, 0, 1]
        elif O[2] < 0:
            normale = [0, 0, -1]
        # coseno angolo tra i due vettori
        prodotto_scalare_vettori = (v_H2O_normalized[0] * normale[0]) + (v_H2O_normalized[1] * normale[1]) + (
                    v_H2O_normalized[2] * normale[2])
        norma_v_H2O_normalized = math.sqrt(
            v_H2O_normalized[0] ** 2 + v_H2O_normalized[1] ** 2 + v_H2O_normalized[2] ** 2)
        norma_normale = math.sqrt(normale[0] ** 2 + normale[1] ** 2 + normale[2] ** 2)
        prodotto_norme = norma_v_H2O_normalized * norma_normale
        coseno_angolo = prodotto_scalare_vettori / prodotto_norme
        # Ottengo angolo in radianti
        angolo = math.acos(coseno_angolo)
        # Converto in gradi
        angolo_gradi = math.degrees(angolo)
        """Aggiungo le molecole al database
        Creo il ciclo for che, dato un angolo per un'acqua specifica, determinerà a quale "settore di distanza" appartiene,
        Sulla base della posizione di O, andando quindi ad aggiungere il valore dell'angolo alla lista corrispondente"""
        contatore_settore = 0
        for distanza_max in np.arange(6.5, 25.5, 0.5):
            #print(distanza_max)
            # Viene utilizzato il valore assoluto abs() perchè abbiamo una funzione della distanza assoluta
            if (abs(O[2]) < distanza_max) & (abs(O[2]) > (distanza_max - 0.5)):
                lista_liste_angoli[contatore_settore].append(angolo_gradi)
                break
            contatore_settore += 1
    """Terminato il processo di calcolo e smistamento degli angoli per le acque dei vari settori ottengo una lista
    di liste disomogenea, ogni settore (ogni lista) avrà una lunghezza diversa dovuta al diverso numero di acque 
    presenti.
    Si genera ora un numpy array di array rendendolo omogeneo, vengono riempite le colonne vuote dei vari array
    dei vari settori con Nan, il quale poi non verrà calcolato nella media, ma l'omogeneità garantirà il corretto
    funzionamento dell'array di array(numpy lavora bene solo con matrici omogenee come colonne)"""
    pad = len(max(lista_liste_angoli, key=len))
    array_arrays_angoli = np.array([i + [float('nan')] * (pad - len(i)) for i in lista_liste_angoli])
    """L'array di array ottenuto, omogeneo, verrà concatenato(append su ogni riga) a quello database"""
    return array_arrays_angoli


def trova_linea(frase, filename):
    with open(filename, 'r') as f:
        for (i, line) in enumerate(f):
            if frase in line:
                return i
    return -1

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def splitta(database_originale):
    isole = database_originale[database_originale < 70]
    monolayers = database_originale[database_originale >= 70]
    return isole,monolayers



# *** INIZIO CODICE ***
# dichiarazione delle variabili necessarie nel ciclo for:
count = 0
# Definisco le colonne che caratterizzerano i dataframe successivi
colonne_nomi=np.array(["0","1","2","3","4","x","y","z"]) #colonne del dataframe .pdb
colonne_elemento_e_coordinate = ["2","x","y","z"]
n_isole_database = np.array([])
n_elements_isole_database = np.array([])
n_monolayers_database = np.array([])
n_elements_monolayers_database = np.array([])
# APRE FILE DA SCRIVERE
with open(path_output_clusterizzazione, 'w') as csvfile, open(path_output_angoli, 'w') as csv_angoli:
    fieldnames = ['nome_file', 'n_isole_medio', 'n_isole_medio_std_della_media', 'n_elements_isole_medio',
                  'n_elements_isole_medio_std_della_media','n_monolayers_medio', 'n_monolayers_medio_std_della_media',
                  'n_elements_monolayers_medio', 'n_elements_monolayers_medio_std_della_media']
    fieldnames_angoli = ['titolo']
    #Modalità di scrittura per il file dei cluster
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #Modalità di scrittura per il file degli angoli
    wr = csv.writer(csv_angoli)
    titoli = csv.DictWriter(csv_angoli,fieldnames=fieldnames_angoli)
    writer.writeheader()
# CARICAMENTO FILES
    files_pdb = os.listdir(path_cartella)  #crea una lista contenente tutti i nomi dei file
    for x in range(len(files_pdb)):
        path = path_cartella + "\\" + files_pdb[x]
        print(path)
        # L'intero file .pdb viene estratto e inserito in un dataframe, come delimiter gli spazi, come colonne i nomi
        # Scritti precedentemente, nessuna compressione dei dati
        dataframe = pd.read_csv(path, delim_whitespace=True, names=colonne_nomi, low_memory=False)
        # to_numeric() rende float i numeri della colonna "1", .apply() applica la modifica al dataframe copia su cui sto
        # agendo, devo eguagliare infine il database originale al database copia
        dataframe.loc[1:, "1"] = dataframe.loc[1:, "1"].apply(pd.to_numeric, errors='coerce')
        # trovo TUTTE le posizioni dei model successivi a 1 e le unisco alla posizione di model 1 specificata a mano
        posizione_model = np.append([0], np.where(dataframe.loc[1:, "1"] > 1))
        # correggo la posizione essendo che parte da 1 nel data.loc(), ottengo la posizione dei model nel dataframe
        posizione_model += 1
        # lunghezza (numero di linee) del file nel path
        numero_di_linee_totali = file_len(path)
        # AZZERO VARIABILI
        n_isole_database = np.array([])
        n_elements_isole_database = np.array([])
        n_monolayers_database = np.array([])
        n_elements_monolayers_database = np.array([])
        """Sempre parte di AZZERO VARIABILI, vado a creare degli array di arrays database che conterranno gli angoli
        Delle molecole d'acqau, ogni riga farà riferimento ad un determinato settore di distanza dalla superficie"""
        lista_liste_angoli = []
        for i in np.arange(6.5, 25.5, 0.5):
            lista_liste_angoli.append([])

        angoli_isole_distanza_database = np.array(lista_liste_angoli)
        angoli_layers_distanza_database = np.array(lista_liste_angoli)
        angoli_rumore_distanza_database = np.array(lista_liste_angoli)

        for count in range(0, numero_di_frame):
            print("Elaborando il frame:", count + 1)
            if count != 2999:
                # counter per il fine frame
                count1 = count + 1
                # Seleziono dati, saranno selezionati i dati dalla posizione del model del frame + 1(non si seleziona "model" nei dati)
                # alla posizione del model successivo - 2 (non si seleziona "model" e "endmodel"
                # le colonne sono quelle delle coordinate ma anche quella dell'elemento
                data = dataframe.loc[(posizione_model[count] + 1):(posizione_model[count1] - 2),colonne_elemento_e_coordinate].copy(deep=True)
            else:
                # nel caso siamo all'ultimo frame, non si può usare come delimitatore il model del frame successivo
                # quindi semplicemente gli dico di saltare le ultime due righe(uso iloc per questo, .loc non può farlo)
                # non serve neanche il count per trovare il model 3000(so che sarà l'ultimo quindi -1)
                # le colonne vanno indicate con numeri essendo iloc
                data = dataframe.iloc[(posizione_model[-1] + 1):-2, [2, 5, 6, 7]].copy(deep=True)

            data.reset_index(drop=True, inplace=True)
            # ESTRAGGO I DATASET soloossigeno e ossigeno&idrogeno
            data_solo_ossigeno = data.loc[::3, ["x", "y", "z"]].to_numpy()
            data_ossigeno_e_idrogeno = data.loc[:, ["x", "y", "z"]].to_numpy()

            if data_solo_ossigeno.size != 3:
                outofbox()
                n_elements_clusters_temp,labels = clusterizzazione()  # variabi temporanee da mergiare agli array totali
                """SPLITTA I DATI IN ISOLE E CLUSTERS"""
                n_elements_isole_temp, n_elements_monolayers_temp = splitta(n_elements_clusters_temp)
                n_monolayers_temp = len(n_elements_monolayers_temp)
                n_isole_temp = len(n_elements_isole_temp)
            else:
                n_monolayers_temp = np.array([0])
                n_isole_temp = np.array([0])
                n_elements_isole_temp = np.array([])
                n_elements_monolayers_temp = np.array([])
                # Se ho una sola molecola, il vettore dei labels è un solo valore, di rumore
                labels = np.array([-1])


            """UNISCE I TEMP AI DATABASE (numero di clusters)"""
            n_isole_database = np.append(n_isole_database, n_isole_temp)  # .append permette di unire array con diverso numero di colonne (diverso numero di clusters in diversi frame) in un unico array 1-D
            n_monolayers_database = np.append(n_monolayers_database, n_monolayers_temp)
            """UNISCE I TEMP AI DATABASE (numero di elementi)"""
            n_elements_isole_database = np.append(n_elements_isole_database, n_elements_isole_temp)
            n_elements_monolayers_database = np.append(n_elements_monolayers_database, n_elements_monolayers_temp)
            #print(n_clusters_database)            # COSA BUONA: se ci sono 0 cluster viene registrato 0 (deve fare media)
            #print(n_elements_clusters_database)   # se non ci sono cluster non viene registrato un valore di numero di elementi(GIUSTO: non deve fare media)

            if data_solo_ossigeno.size != 3:
                """STUDIO ANGOLI VETTORE H2O/NORMALE ALLA SUPERFICIE DI NaCl"""
                # Definisco quali labels sono associati alle isole,layers e rumore
                labels_delle_isole = np.where(n_elements_clusters_temp < 70)
                labels_dei_layer = np.where(n_elements_clusters_temp >= 70)
                label_rumore = -1
                # Trovo le righe delle coordinate degli ossigeni appartenenti ad isole, layers e rumore nel
                # dataset con solo ossigeni
                indici_ossigeno_isole_in_solo_ox = np.where(np.in1d(labels, labels_delle_isole))
                indici_ossigeno_layers_in_solo_ox = np.where(np.in1d(labels, labels_dei_layer))
                indici_ossigeno_rumore_in_solo_ox = np.where(labels == -1)
                #print(indici_ossigeno_isole_in_solo_ox)

                # Trovo le righe delle coordinate degli ossigeni appartenenti ad isole, layers e rumore nel
                # dataset con ossigeni ed idrogeni, ricavo da questi indici i medesimi indici per H1 ed H2
                # ISOLE
                indici_ossigeno_isole, indici_idrogeno1_isole, indici_idrogeno2_isole = nuovi_indici(
                    indici_ossigeno_isole_in_solo_ox[0])
                # LAYERS
                indici_ossigeno_layers, indici_idrogeno1_layers, indici_idrogeno2_layers = nuovi_indici(
                    indici_ossigeno_layers_in_solo_ox[0])
                # RUMORE
                indici_ossigeno_rumore, indici_idrogeno1_rumore, indici_idrogeno2_rumore = nuovi_indici(
                    indici_ossigeno_rumore_in_solo_ox[0])
                #print(n_elements_isole_temp)
                #print(indici_ossigeno_isole, indici_idrogeno1_isole, indici_idrogeno2_isole)

                # TROVO GLI ANGOLI, PER TUTTE LE MOLECOLE D'ACQUA DI OGNI GRUPPO(tramite la funzione) e LI UNISCO AL DATABASE DEL FILE(che si azzera dopo l'apertura di ogni file)
                angoli_isole_distanza_database = np.concatenate((angoli_isole_distanza_database, calcolo_angoli(data_ossigeno_e_idrogeno, indici_ossigeno_isole, indici_idrogeno1_isole, indici_idrogeno2_isole)),axis=1)
                angoli_layers_distanza_database = np.concatenate((angoli_layers_distanza_database, calcolo_angoli(data_ossigeno_e_idrogeno, indici_ossigeno_layers, indici_idrogeno1_layers, indici_idrogeno2_layers)),axis=1)
                angoli_rumore_distanza_database = np.concatenate((angoli_rumore_distanza_database, calcolo_angoli(data_ossigeno_e_idrogeno, indici_ossigeno_rumore, indici_idrogeno1_rumore, indici_idrogeno2_rumore)),axis=1)
                #print(angoli_isole_distanza_database, angoli_layers_distanza_database, angoli_rumore_distanza_database)
            # nel caso in cui ci sia solo una molecola, il sistema con il clustering non funziona, quindi devo ovviare fornendo io l'indice dell'ossigeno e degli idrogeni
            # considero l'acqua alone come rumore
            else:
                indici_ossigeno_alone = np.array([0])
                indici_idrogeno1_alone = np.array([1])
                indici_idrogeno2_alone = np.array([2])
                angoli_rumore_distanza_database = np.concatenate((angoli_rumore_distanza_database, calcolo_angoli(data_ossigeno_e_idrogeno, indici_ossigeno_alone, indici_idrogeno1_alone, indici_idrogeno2_alone)),axis=1)


        """ TROVA VALORI MEDI -> OUTPUT  CLUSTERS """
        n_isole_medio = np.mean(n_isole_database)
        n_isole_medio_std_della_media = np.std(n_isole_database) / ((len(n_isole_database)) ** (0.5))
        #n_isole_medio_std = np.std(n_isole_database)
        if n_elements_isole_database.size != 0:
            n_elements_isole_medio = (np.mean(n_elements_isole_database))
        #n_elements_clusters_medio_std = np.std(n_elements_isole_database)
            n_elements_isole_medio_std_della_media = np.std(n_elements_isole_database) / ((len(n_elements_isole_database)) ** (0.5))
        else:
            n_elements_isole_medio = 0.00
            n_elements_isole_medio_std_della_media = 0.00
        """TROVA VALORI MEDI -> OUTPUT  MONOLAYERS """
        n_monolayers_medio = np.mean(n_monolayers_database)
        #n_clusters_medio_std = np.std(n_isole_database)
        n_monolayers_medio_std_della_media = np.std(n_monolayers_database) / ((len(n_monolayers_database)) ** (0.5))
        if n_elements_monolayers_database.size != 0:
            n_elements_monolayers_medio = (np.mean(n_elements_monolayers_database))
        #n_elements_monolayers_medio_std = np.std(n_elements_isole_database)
            n_elements_monolayers_medio_std_della_media = np.std(n_elements_monolayers_database) / ((len(n_elements_monolayers_database)) ** (0.5))
        else:
            n_elements_monolayers_medio = 0.00
            n_elements_monolayers_medio_std_della_media = 0.00
        """TROVA VALORI MEDI -> ANGOLI """
        # Se non ho molecole in uno de tre database, devo settare la media su "Nan", se mettessi 0 sarebbe equivocabile, mentre una string adarebbe errore
        """Come il database degli angoli passa da vettore mono-dimensionale a matrice bidimensionale(in questo caso
        specifico in cui ho funzione della distanza),il contenitore delle medie degli angoli non sarà una variabile
        ma un vettore monodimensionale, ogni posizione indica la media degli angoli in certo settore di distanza."""
        #Inizializzo per prima cosa i vettori degli angoli medi come array mono-d vuoti
        angoli_isole_medio_distanza = np.array([])
        angoli_layers_medio_distanza = np.array([])
        angoli_rumore_medio_distanza = np.array([])
        angoli_isole_medio_std_della_media = np.array([])
        angoli_layers_medio_std_della_media = np.array([])
        angoli_rumore_medio_std_della_media = np.array([])
        #Inizializzo il counter che permetterà di studiare i diversi vettori (dell'array di array) contenenti
        #Gli angoli delle molecole nei diversi settori
        counter_media_angoli = 0
        for distanza_max in np.arange(6.5, 25.5, 0.5):
            #Ora ottengo le medie, andando a verificare che non ci siano settori senza molecole d'acqua(restituirebbe
            #Errore per media di soli nan
            """.isnan ottiene un vettore identico dove i nan sono sostituiti da true ed i valori da false, all() verifica
            se tutti i valori sono uguali(ad esempio tutti True perchè tutti nan) e restituisce True nel caso io abbia solo nan"""

            """Sia per il calcolo delle medie che degli std si usano le specifiche nanmean e nanstd, che ignorano i NaNs"""
            if np.isnan(angoli_isole_distanza_database[counter_media_angoli]).all() != True:
                angoli_isole_medio_distanza = np.append(angoli_isole_medio_distanza,np.nanmean(angoli_isole_distanza_database[counter_media_angoli]))
                angoli_isole_medio_std_della_media = np.append(angoli_isole_medio_std_della_media,np.nanstd(angoli_isole_distanza_database[counter_media_angoli]) / ((np.size(angoli_isole_distanza_database[counter_media_angoli]) - np.count_nonzero(np.isnan(angoli_isole_distanza_database[counter_media_angoli]))) ** (0.5)))
            else:
                angoli_isole_medio_distanza = np.append(angoli_isole_medio_distanza,float("nan"))
                angoli_isole_medio_std_della_media = np.append(angoli_isole_medio_std_della_media,float("nan"))

            if np.isnan(angoli_layers_distanza_database[counter_media_angoli]).all() != True:
                angoli_layers_medio_distanza = np.append(angoli_layers_medio_distanza, np.nanmean(angoli_layers_distanza_database[counter_media_angoli]))
                angoli_layers_medio_std_della_media = np.append(angoli_layers_medio_std_della_media,np.nanstd(angoli_layers_distanza_database[counter_media_angoli]) / ((np.size(angoli_layers_distanza_database[counter_media_angoli]) - np.count_nonzero(np.isnan(angoli_layers_distanza_database[counter_media_angoli]))) ** (0.5)))
            else:
                angoli_layers_medio_distanza = np.append(angoli_layers_medio_distanza, float("nan"))
                angoli_layers_medio_std_della_media = np.append(angoli_layers_medio_std_della_media, float("nan"))

            if np.isnan(angoli_rumore_distanza_database[counter_media_angoli]).all() != True:
                angoli_rumore_medio_distanza = np.append(angoli_rumore_medio_distanza,np.nanmean(angoli_rumore_distanza_database[counter_media_angoli]))
                angoli_rumore_medio_std_della_media = np.append(angoli_rumore_medio_std_della_media,np.nanstd(angoli_rumore_distanza_database[counter_media_angoli]) / ((np.size(angoli_rumore_distanza_database[counter_media_angoli]) - np.count_nonzero(np.isnan(angoli_rumore_distanza_database[counter_media_angoli]))) ** (0.5)))
            else:
                angoli_rumore_medio_distanza = np.append(angoli_rumore_medio_distanza,float("nan"))
                angoli_rumore_medio_std_della_media = np.append(angoli_rumore_medio_std_della_media,float("nan"))
                print(angoli_rumore_medio_std_della_media)
            #Aggiorno il counter, al prossimo loop verrà analizzato il settore successivo
            counter_media_angoli += 1
        # STAMPA UNA RIGA DI OUTPUT
        writer.writerow({'nome_file': files_pdb[x], 'n_isole_medio': "%.2f" %n_isole_medio, 'n_isole_medio_std_della_media': "%.2f" %n_isole_medio_std_della_media,
                        'n_elements_isole_medio': "%.2f" %n_elements_isole_medio, 'n_elements_isole_medio_std_della_media': "%.2f" %n_elements_isole_medio_std_della_media
                        ,'n_monolayers_medio':"%.2f" %n_monolayers_medio, 'n_monolayers_medio_std_della_media':"%.2f" %n_monolayers_medio_std_della_media,
                        'n_elements_monolayers_medio':"%.2f" %n_elements_monolayers_medio, 'n_elements_monolayers_medio_std_della_media':"%.2f" %n_elements_monolayers_medio_std_della_media})
        csvfile.flush()
        #STAMPA FILE ANGOLI DI OUTPUT, UNA RIGA PER INDICARE IL NOM DEL FILE,UNA RIGA PER IL TIPO DI CLUSTER, UNA RIGA L?ARRAY DELLA MEDIA,UNA PER GLI ERRORI
        titoli.writerow({'titolo':files_pdb[x]})
        titoli.writerow({'titolo': "Angoli_isole"})
        wr.writerow(angoli_isole_medio_distanza)
        titoli.writerow({'titolo':"Errori_Isole"})
        wr.writerow(angoli_isole_medio_std_della_media)

        titoli.writerow({'titolo':"Angoli_layers"})
        wr.writerow(angoli_layers_medio_distanza)
        titoli.writerow({'titolo':"Errori_layers"})
        wr.writerow(angoli_layers_medio_std_della_media)

        titoli.writerow({'titolo':"Angoli_rumore"})
        wr.writerow(angoli_rumore_medio_distanza)
        titoli.writerow({'titolo':"Errori_rumore"})
        wr.writerow(angoli_rumore_medio_std_della_media)
        csv_angoli.flush()
        #va a scrivere il txt che altrimenti sarebbe scritto totalmente alla fine

stop = timeit.default_timer()
print('Tempo totale di esecuzione: ', (stop - start)/60)