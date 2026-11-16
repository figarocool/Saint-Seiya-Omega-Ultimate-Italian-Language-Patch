import re

# 1. Exact table overrides by BTX path (or subfile name) and entry_id
EXACT_TABLES = {
    "btx/character_name/character_name_jp.btx": {
        0: "Koga",
        1: "Yuna",
        2: "Ryuho",
        3: "Soma",
        4: "Eden",
        5: "Haruto",
        6: "Seiya",
        7: "Shaina",
        8: "Ionia",
    },
    "SYSTEMWINDOW_JP.BTX": {
        0: "Si",
        1: "No",
        2: "OK",
        3: "Mito",
    },
    "SELECT_JP.BTX": {
        0: "Seleziona il personaggio.",
        1: "Seleziona l'avversario.",
        2: "Seleziona lo stage.",
        3: "Seleziona le regole.",
        4: "In attesa dell'avversario.",
        5: "In attesa dell'avversario..",
        6: "In attesa dell'avversario...",
    },
    "STORYSELECT_JP.BTX": {
        0: "Seleziona il personaggio con cui iniziare.",
    },
    "MAINMENU_JP.BTX": {
        0: "Avanza nella storia sconfiggendo i nemici.",
        1: "Sconfiggi una serie di nemici fino alla vittoria finale.",
        2: "Affronta la CPU o un amico in battaglia.",
        3: "Allenati nel combattimento.",
        4: "Visualizza le illustrazioni e i filmati sbloccati.",
        5: "Modifica le impostazioni di gioco.",
        6: "Installa i dati di gioco su Memory Stick.",
        7: "Affronta la CPU in battaglia.",
        8: "Usa la modalita' Ad Hoc per sfidare un amico.",
        9: "Allenati nel combattimento contro la CPU.",
        10: "Impara i comandi base del combattimento.",
        11: "Visualizza i profili e i modelli dei personaggi.",
        12: "Visualizza le illustrazioni evento raccolte.",
        13: "Visualizza i filmati raccolti.",
        14: "Riproduci i replay salvati.",
        15: "Controlla i tuoi risultati di battaglia.",
        16: "In attesa dell'avversario.",
        17: "In attesa dell'avversario..",
        18: "In attesa dell'avversario...",
    },
    "CONFIG_JP.BTX": {
        0: "Volume BGM",
        1: "Volume SE",
        2: "Volume Voce",
        3: "Vel. Testo",
        4: "Comandi",
        5: "Conferma",
        6: "Min",
        7: "Max",
        8: "Lenta",
        9: "Veloce",
        10: "Regola il volume della musica di sottofondo.",
        11: "Regola il volume degli effetti sonori.",
        12: "Regola il volume delle voci dei personaggi.",
        13: "Regola la velocita' dei messaggi di testo.",
        14: "Configura l'assegnazione dei tasti.",
        15: "Attiva o disattiva l'uso dei dati installati.",
        16: "ON",
        17: "OFF",
        18: "Dati Installati",
    },
    "KEY_JP.BTX": {
        0: "Pugno (P)",
        1: "Calcio (K)",
        2: "Speciale (S)",
        3: "Salto",
        4: "Carica Cosmo",
        5: "Presa",
        6: "Movimento",
        100: "Personalizza la configurazione dei tasti.",
        101: "Personalizza la configurazione dei tasti.",
        102: "Personalizza la configurazione dei tasti.",
        103: "Personalizza la configurazione dei tasti.",
        104: "Personalizza la configurazione dei tasti.",
        105: "Personalizza la configurazione dei tasti.",
        106: "Personalizza la configurazione dei tasti.",
    },
    "MOVIE_JP.BTX": {
        9: "/5",
        10: "Sigla di Apertura",
        11: "Prologo",
        12: "Battaglia Finale (Koga)",
        13: "Battaglia Finale (Seiya)",
        14: "Titoli di Coda",
        100: "?????",
    },
    "MYPAGE_JP.BTX": {
        10: ":",
        11: "",
        12: "pt",
        13: "%",
        14: "G",
        15: "V",
        16: ".",
        20: "Giocatore:",
        21: "Tempo Gioco:",
        22: "Battaglie:",
        23: "Record Punti:",
        24: "% Vitt. CPU:",
        25: "Sfide CPU:",
        26: "% Vitt. VS:",
        27: "Sfide Umani:",
    },
    "PROFILE_JP.BTX": {
        10: "Luce",
        11: "Oscurita'",
        12: "Fuoco",
        13: "Acqua",
        14: "Vento",
        15: "Terra",
        16: "Fulmine",
        17: "",
        18: "%",
        19: ".",
        20: "Elemento:",
        21: "Utilizzi:",
        22: "% Vittorie:",
    },
    "COLLECTION_JP.BTX": {
        99: "/48",
        100: "Sospetto",
        101: "La determinazione di Shaina",
        102: "I giorni passati insieme",
        103: "Ambizione svelata",
        104: "Scontro del destino",
        105: "Il passato di Soma 1",
        106: "Il passato di Soma 2",
        107: "Il passato di Soma 3",
        108: "Il passato di Soma 4",
        109: "Esitazione e conflitto",
        110: "Per un soffio",
        111: "Umiliazione amara 1",
        112: "Umiliazione amara 2",
        113: "Umiliazione amara 3",
        114: "Ricordi preziosi",
        115: "Onore al merito",
        116: "Rivincita",
        117: "Contatto",
        118: "Spirito combattivo silenzioso",
        119: "Battaglia feroce 1",
        120: "Battaglia feroce 2",
        121: "L'arrivo di Poseidone",
        122: "La premura di una sorella",
        123: "Il Cavaliere leggendario",
        124: "Sentimenti inespressi",
        125: "La discesa di Atena",
        126: "I Cavalieri di Atena",
        127: "Il principe del Nuovo Mondo",
        128: "Luce di speranza",
        129: "Verso il futuro",
        130: "Croce del Sud lucente",
        131: "Un giorno...",
        132: "Spalle lontane",
        133: "Dialogo silenzioso",
        134: "Il peso delle aspettative",
        135: "Sentimenti",
        136: "Grande tripudio!!",
        137: "Legame tra maestro e allievo",
        138: "Verso il mondo ideale",
        139: "Un mondo senza guerre",
        140: "Giuramento eterno",
        141: "Nobile missione",
        142: "Orgoglio assoluto",
        143: "Potere ereditato",
        144: "L'arte marziale suprema",
        145: "Per l'eternita'",
        146: "Segnale di riscossa",
        147: "Il Re degli Abissi",
        148: "CG 48",
        149: "CG 49",
        150: "CG 50",
        151: "CG 51",
        152: "CG 52",
        153: "CG 53",
        154: "CG 54",
        155: "CG 55",
        156: "CG 56",
        157: "CG 57",
        158: "CG 58",
        159: "CG 59",
        160: "CG 60",
        161: "CG 61",
        162: "CG 62",
        163: "CG 63",
        164: "CG 64",
        200: "?????",
    },
    # Character Profiles in Gallery
    "KOG_PROFILE_JP.BTX": {
        0: "Cavaliere di Bronzo di Pegasus. Elemento Luce.\r\nUn ragazzo di 13 anni cresciuto da Saori Kido,\r\nreincarnazione della dea Atena.\r\nCombatte con uno stile ortodosso e bilanciato,\r\ncapace di rapide raffiche di colpi.\r\n(Voce: Hikaru Midorikawa)"
    },
    "KOGV2_PROFILE_JP.BTX": {
        0: "Koga con la Squama di Tritone. Elemento Luce.\r\nLe sue capacita' complessive sono aumentate,\r\nma in cambio la resistenza dell'armatura\r\ne' inferiore al normale.\r\n(Voce: Hikaru Midorikawa)"
    },
    "YUN_PROFILE_JP.BTX": {
        0: "Cavaliere di Bronzo dell'Aquila. Elemento Vento.\r\nOrfana di guerra, ha appreso l'arte del\r\ncombattimento dei Cavalieri dalla maestra Pavlin.\r\nSpecializzata nelle tecniche di calcio,\r\ncolpisce con grande rapidita'.\r\n(Voce: Satsuki Yukino)"
    },
    "YUNV2_PROFILE_JP.BTX": {
        0: "Yuna con la Squama di Tritone. Elemento Vento.\r\nAssorbendo il potere puro della Squama,\r\nle sue statistiche sono migliorate.\r\nTuttavia la resistenza della Squama e' bassa,\r\nrendendo la difesa piu' rischiosa.\r\n(Voce: Satsuki Yukino)"
    },
    "RYO_PROFILE_JP.BTX": {
        0: "Cavaliere di Bronzo del Dragone. Elemento Acqua.\r\nAddestrato da suo padre Shiryu, da cui ha\r\nereditato l'Armatura del Dragone.\r\nEccelle nella difesa e nei contrattacchi, ma se\r\nl'Armatura si rompe la difesa cala drasticamente.\r\n(Voce: Tetsuya Kakihara)"
    },
    "RYOV2_PROFILE_JP.BTX": {
        0: "Ryuho con la Squama di Tritone. Elemento Acqua.\r\nLa perfetta affinita' elementale aumenta\r\nnotevolmente le sue capacita'.\r\nConsuma pero' molto piu' Cosmo, rendendolo\r\nadatto a battaglie rapide.\r\n(Voce: Tetsuya Kakihara)"
    },
    "SOM_PROFILE_JP.BTX": {
        0: "Cavaliere di Bronzo del Leone Minore. Elemento Fuoco.\r\nIspirato dal defunto padre, anch'egli Cavaliere,\r\nha scelto il cammino dei cavalieri.\r\nInsegue Sonia per vendicare suo padre.\r\nVeloce e offensivo, usa molte tecniche di pugno.\r\n(Voce: Katsuyuki Konishi)"
    },
    "SOMV2_PROFILE_JP.BTX": {
        0: "Soma con la Squama di Tritone. Elemento Fuoco.\r\nA causa della scarsa affinita' tra il Fuoco\r\ne la Scale, le sue statistiche sono ridotte,\r\nma il consumo di Cosmo e' molto inferiore\r\npermettendo l'uso continuo di tecniche.\r\n(Voce: Katsuyuki Konishi)"
    },
    "EDE_PROFILE_JP.BTX": {
        0: "Cavaliere di Bronzo di Orione. Elemento Fulmine.\r\nInsieme al padre e alla sorella vuole distruggere\r\nil vecchio mondo per crearne uno ideale.\r\nI suoi colpi ampi non sono adatti alle lunghe\r\ncombo, ma ogni singolo attacco e' devastante.\r\n(Voce: Junichi Suwabe)"
    },
    "EDEV2_PROFILE_JP.BTX": {
        0: "Eden con la Squama di Tritone. Elemento Fulmine.\r\nGrazie al potere della Squama di Tritone,\r\nla potenza di ogni suo singolo colpo\r\ne' diventata ancora piu' schiacciante.\r\n(Voce: Junichi Suwabe)"
    },
    "HAT_PROFILE_JP.BTX": {
        0: "Cavaliere di Bronzo del Lupo. Elemento Terra.\r\nDiscendente di un clan ninja che padroneggia\r\ninnumerevoli tecniche segrete.\r\nConfonde il nemico con movimenti rapidi e\r\nattacchi a distanza. Ideale per esperti.\r\n(Voce: Tatsuhisa Suzuki)"
    },
    "HATV2_PROFILE_JP.BTX": {
        0: "Haruto con la Squama di Tritone. Elemento Terra.\r\nA causa dell'elemento opposto non puo'\r\nsfruttare appieno il potere della Squama,\r\nma in compenso la sua armatura e' molto\r\npiu' resistente delle altre.\r\n(Voce: Tatsuhisa Suzuki)"
    },
    "SEY_PROFILE_JP.BTX": {
        0: "Cavaliere d'Oro del Sagittario. Elemento Luce.\r\nAgisce nell'ombra per infrangere le ambizioni\r\ndi Mars che minacciano la Terra.\r\nEccezionale in ogni parametro, richiede\r\nsolo un po' di pratica negli attacchi.\r\n(Voce: Toru Furuya)"
    },
    "SHN_PROFILE_JP.BTX": {
        0: "Cavaliere d'Argento dell'Ofiuco. Elemento Fulmine.\r\nMaestra di Koga, lo ha addestrato duramente\r\nfino a farlo diventare un Cavaliere.\r\nCompensa una potenza d'attacco moderata\r\ncon una velocita' fulminea.\r\n(Voce: Mami Koyama)"
    },
    "ION_PROFILE_JP.BTX": {
        0: "Cavaliere d'Oro del Capricorno. Elemento Vento.\r\nEx direttore della Palaestra, l'accademia\r\ndei Cavalieri frequentata da Koga e gli altri.\r\nHa tradito Atena schierandosi contro Koga.\r\nLento ma dotato di cariche e prese letali.\r\n(Voce: Ryuzaburo Otomo)"
    },
    "SOI_PROFILE_JP.BTX": {
        0: "High Martian di Hornet. Elemento Oscurita'.\r\nSorella maggiore di Eden, combatte per\r\nrenderlo il sovrano del Nuovo Mondo.\r\nCaratterizzata da movimenti rapidi e\r\nraffiche di colpi consecutivi.\r\n(Voce: Aya Hisakawa)"
    },
    "MIK_PROFILE_JP.BTX": {
        0: "Cavaliere d'Oro del Leone. Elemento Fulmine.\r\nIl Cavaliere che ha addestrato Eden e che\r\nsi oppone a Koga e ai suoi compagni.\r\nUnisce grande potenza a movimenti rapidi,\r\ncon tecniche ad ampio raggio.\r\n(Voce: Yutaka Nakano)"
    },
    "GEN_PROFILE_JP.BTX": {
        0: "Cavaliere d'Oro della Bilancia. Elemento Acqua.\r\nHa ottenuto e indossato l'Armatura della Bilancia\r\ncustodito da Shiryu, padre di Ryuho.\r\nImpugna varie armi con ottima potenza e\r\nportata, pur essendo leggermente lento.\r\n(Voce: Nobuyuki Hiyama)"
    },
    "KIK_PROFILE_JP.BTX": {
        0: "Cavaliere d'Oro dell'Ariete. Elemento Terra.\r\nVecchio compagno dei Cavalieri leggendari Seiya\r\ne Shun, oggi massimo riparatore di Armature.\r\nUsa psicocinesi e teletrasporto, abilita'\r\nuniche tra tutti i Cavalieri.\r\n(Voce: Shigeru Nakahara)"
    },
    "ITI_PROFILE_JP.BTX": {
        0: "Cavaliere d'Argento dell'Idra. Elemento Terra.\r\nCavaliere della generazione di Seiya, era\r\ncompagno di classe di Koga alla Palaestra.\r\nCombatte a media e lunga distanza con\r\nzanne estensibili e mosse imprevedibili.\r\n(Voce: Masaya Onosaka)"
    },
    "JYU_PROFILE_JP.BTX": {
        0: "L'Imperatore dei Mari risorto nel corpo di\r\nJulian Solo. Elemento Acqua.\r\nPur non avendo ancora il pieno potere,\r\npossiede un Cosmo immenso. Combattente\r\ncompleto per forza, velocita' e portata.\r\n(Voce: Keiichi Nanba)"
    },
    "SOT_PROFILE_JP.BTX": {
        0: "Generale degli Abissi di Siren. Elemento Acqua.\r\nSpietato contro chiunque osi opporsi\r\nal suo signore Poseidone.\r\nAttacca con la melodia del suo flauto,\r\neccellendo a media e lunga distanza.\r\n(Voce: Yoku Shioya)"
    },
    "SHU_PROFILE_JP.BTX": {
        0: "Cavaliere di Bronzo di Andromeda. Elemento Vento.\r\nCavaliere leggendario, si e' ritirato dalla prima\r\nlinea a causa della ferita d'oscurita'.\r\nSenza Armatura ha attacco e difesa ridotti,\r\nma le sue tecniche segrete sono potentissime.\r\n(Voce: Hiroshi Kamiya)"
    },
    "PAB_PROFILE_JP.BTX": {
        0: "Cavaliere d'Argento del Pavone. Elemento Acqua.\r\nMaestra di Yuna, le ha insegnato non solo\r\na combattere ma anche a vivere da Cavaliere.\r\nCome Yuna usa soprattutto i calci, ma con\r\nun bilanciamento attacco/difesa superiore.\r\n(Voce: Ai Orikasa)"
    },
    "btx/system/systemmessage_jp.btx": {
        0: "Si",
        1: "No",
        2: "OK",
        3: "Conferma",
        4: "Torna alla battaglia",
        5: "Lista Combo",
        6: "Configura Tasti",
        7: "Selezione Personaggio",
        8: "Menu Principale",
        9: "Rivincita",
        10: "Selezione Personaggio",
        11: "Torna alla Lobby",
        12: "Rivincita",
        13: "Selezione Personaggio",
        14: "Menu Principale",
        15: "Torna alla battaglia",
        16: "Lista Combo",
        17: "Opzioni Allenamento",
        18: "Selezione Personaggio",
        19: "Menu Principale",
        20: "Tornare alla schermata della Lobby?",
        21: "Tornare al Menu Principale?",
        22: "Tornare alla schermata di\r\nSelezione Personaggio?",
        23: "Giocatore:",
        24: "Tempo di gioco:",
        25: "Tempo battaglie:",
        26: "Punteggio Max:",
        27: "% Vittorie CPU:",
        28: "Sfide vs CPU:",
        29: "% Vittorie VS:",
        30: "Sfide vs Umani:",
        31: "Selezione Personaggio",
        32: "Torna al Titolo",
        33: "Esempio 41",
        34: "Forza CPU",
        35: "Tempo Limite",
        36: "Numero Round",
        37: "Rookie",
        38: "Bronze",
        39: "Silver",
        40: "Gold",
        41: "God",
        42: "30",
        43: "60",
        44: "99",
        45: "Inf.",
        46: "1",
        47: "3",
        48: "5",
        49: "Tornare alla schermata del titolo?",
        50: "Tornare alla selezione personaggio?",
        51: "Torna al Tutorial",
        52: "Terminare il Tutorial e tornare\r\nal Menu Principale?",
        53: "Annulla",
        54: "Combo 1",
        55: "Combo 2",
        56: "Combo 3",
        57: "Combo 4",
        58: "Combo 5",
        59: "Combo 6",
        60: "Combo 7",
        61: "Combo 8",
        62: "Combo 9",
        63: "Combo 10",
        110: "Nessun dato di sistema trovato.\r\nServono almeno <SET0> KB liberi.\r\nCreare nuovi dati di sistema?",
        111: "I dati di sistema sono danneggiati.\r\nCaricamento fallito.\r\nCreare nuovi dati di sistema?",
        112: "Memory Stick non trovata.\r\nCaricamento dati di sistema fallito.\r\nRiprovare?",
        113: "La Memory Stick e' stata rimossa.\r\nCaricamento dati di sistema fallito.\r\nRiprovare?",
        114: "Memory Stick non trovata.\r\nSalvataggio dati di sistema fallito.\r\nRiprovare?",
        115: "La Memory Stick e' stata rimossa.\r\nSalvataggio dati di sistema fallito.\r\nRiprovare?",
        116: "La Memory Stick e' protetta da scrittura.\r\nSalvataggio dati di sistema fallito.\r\nRiprovare?",
        117: "Trovati dati di sospensione.\r\nRiprendere la partita?\r\n(I dati verranno sovrascritti\r\n al prossimo salvataggio.)",
        118: "Salvataggio fallito a causa dello\r\nspegnimento/modalita' riposo.\r\nRiprovare?",
        119: "Memory Stick non trovata.\r\nVerifica dati di sistema fallita.\r\nRiprovare?",
        120: "La Memory Stick e' stata rimossa.\r\nVerifica dati di sistema fallita.\r\nRiprovare?",
        121: "I dati di sistema sono diversi dai precedenti.\r\nSovrascrivere?",
        122: "Caricamento fallito a causa della\r\nmodalita' riposo.\r\nRiprovare?",
        123: "Dati di sistema non trovati.\r\nIniziare una nuova partita?",
        124: "Per creare i dati di sistema servono\r\nalmeno <SET0> KB di spazio libero.\r\nCreare nuovi dati?",
        125: "Riprovare a caricare\r\ni dati di sistema?",
        126: "Riprovare a salvare\r\ni dati di sistema?",
        127: "I dati di sistema sono danneggiati.\r\nSovrascrivere?",
        130: "I dati installati esistono gia'.\r\nSovrascrivere?",
        131: "Per installare i dati servono almeno\r\n74 MB di spazio libero.\r\nProcedere con l'installazione?",
        132: "L'installazione richiedera' alcuni minuti.\r\nSi consiglia di caricare la batteria\r\no collegare l'alimentatore AC.",
        133: "Installazione dati completata.\r\nPuoi attivare/disattivare i dati\r\nnel menu Opzioni.\r\n",
        134: "Il disco di Saint Seiya Omega\r\ne' stato rimosso.\r\nInstallazione annullata.\r\n",
        135: "Errore durante l'installazione.\r\nInstallazione dati terminata.\r\n",
        136: "Interrompere l'installazione dati?",
        137: "Installazione dati interrotta.",
        138: "Installazione fallita a causa\r\ndella modalita' riposo.",
        139: "Batteria scarica.\r\nInstallazione dati fallita.",
        140: "Spazio libero inferiore a 74 MB.\r\nInstallazione dati fallita.",
        141: "Impossibile accedere alla Memory Stick.\r\nInstallazione dati fallita.",
        142: "Impossibile usare i dati installati.\r\nL'opzione Dati Installati e' ora OFF.",
        143: "Eliminare altri salvataggi per\r\nliberare spazio?\r\nServono almeno 74 MB liberi.",
        144: "Installando i dati di gioco potrai\r\ngiocare con caricamenti piu' rapidi.\r\n(Non necessario per la versione digitale.)",
        150: "Azione CPU",
        151: "Recupero HP",
        152: "Barra Cosmo",
        153: "Stato Armatura",
        154: "Si",
        155: "No",
        160: "Fermo",
        161: "Salto",
        162: "Cammina",
        163: "Guardia",
        164: "Attacco A",
        165: "Attacco B",
        166: "Normale",
        170: "Normale",
        171: "Cosmo MAX",
        172: "Cosmo Burst Fisso",
        175: "Normale",
        176: "Indistruttibile",
        177: "Distrutto",
        180: "Salvataggio Replay",
        181: "Salvare il replay di\r\nquesta battaglia?",
        182: "Interrompere la riproduzione del replay?",
        183: "Limite massimo replay raggiunto.\r\nImpossibile salvare il replay.",
        190: "Riprova",
        191: "Abbandona",
        192: "Abbandonare e tornare al\r\nMenu Principale?",
        201: "Koga",
        202: "Nome giocatore:",
        203: "Confermi il nome\r\n\"<SET0>\"?",
        204: "Registrazione nome annullata.\r\nRiprovare?",
        205: "CPU",
        206: "Nessun nome inserito.\r\nInserisci nuovamente il nome.",
        210: "In attesa dell'avversario.  ",
        211: "In attesa dell'avversario.. ",
        212: "In attesa dell'avversario...",
        400: "Tasti duplicati rilevati.\r\nRiconfigura le voci indicate\r\nin rosso.",
        401: "Applicare le modifiche\r\nalle impostazioni?",
        420: "Il personaggio\r\n\"<c#ff1f75ff><SET0><c>\"\r\ne' stato sbloccato!",
        421: "La Storia di\r\n\"<c#ff1f75ff><SET0><c>\"\r\ne' stata sbloccata!",
        422: "Koga",
        423: "Yuna",
        424: "Ryuho",
        425: "Soma",
        426: "Eden",
        427: "Haruto",
        428: "Seiya",
        429: "Shaina",
        430: "Ionia",
        431: "Sonia",
        432: "Micene",
        433: "Genbu",
        434: "Kiki",
        435: "Ichi",
        436: "Poseidone",
        437: "Sorrento",
        438: "Shun",
        439: "Pavlin",
        440: "Koga (Tritone)",
        441: "Yuna (Tritone)",
        442: "Ryuho (Tritone)",
        443: "Soma (Tritone)",
        444: "Eden (Tritone)",
        445: "Haruto (Tritone)",
        500: "Controllo Memory Stick in corso.\r\nNon rimuovere la Memory Stick\r\ne non spegnere la console.",
        501: "Per creare i dati di sistema servono\r\nalmeno <SET0> KB liberi.\r\nCreare nuovi dati di sistema?",
        502: "Creazione dati di sistema in corso.\r\nNon rimuovere la Memory Stick\r\ne non spegnere la console.",
        503: "Spazio libero insufficiente.\r\nEliminare altri dati salvati?\r\nServono almeno <SET0> KB liberi.",
        504: "Memory Stick non trovata.\r\n",
        505: "Dati di sistema non trovati.\r\n",
        506: "I dati di sistema sono danneggiati.\r\nCaricamento fallito.",
        507: "Senza dati di sistema non potrai\r\nsalvare i progressi.\r\nContinuare comunque?",
        508: "Servono almeno <SET0> KB liberi.\r\nEliminare i dati di sistema esistenti?",
        509: "Salvataggio dati di sistema in corso.\r\nNon rimuovere la Memory Stick\r\ne non spegnere la console.",
        510: "Eliminare i dati di sistema esistenti\r\nper liberare spazio?",
        511: "Riprendere dai dati di sospensione?\r\nI dati di sospensione verranno rimossi.",
        512: "Salvataggio fallito.",
        513: "I dati installati sono danneggiati.\r\nI dati installati sono stati disattivati.",
        514: "Memory Stick non trovata.\r\nI dati installati sono stati disattivati.",
        515: "Impossibile caricare i dati installati.\r\nDati installati disattivati.\r\nCaricamento da UMD<b1> attivo.",
        516: "Continuare la partita senza\r\nsalvare i progressi?",
        517: "La Memory Stick e' protetta.\r\nImpossibile salvare.",
        518: "Accesso alla Memory Stick fallito.",
        519: "Servono almeno <SET0> KB liberi.\r\nEliminare i dati di sistema esistenti?",
        520: "La Memory Stick e' stata rimossa.\r\nOperazione fallita.",
        521: "Salvataggio completato.",
        522: "Caricamento completato.",
        523: "Verifica interrotta a causa\r\ndella modalita' riposo.",
        524: "Caricamento fallito.",
        525: "Continuare senza caricare?",
        527: "La Memory Stick e' protetta.\r\nImpossibile eliminare.",
        528: "Attenzione: sostituendo la Memory Stick\r\ndurante il gioco i dati verranno\r\nsovrascritti con quelli attuali.",
        800: "La stanza e' piena.",
        801: "La stanza e' gia' in uso.",
        802: "In attesa dell'avversario.",
        803: "Versione del gioco non compatibile.",
        804: " Connessione scaduta (Timeout).",
        900: "Comunicazione interrotta.",
        901: "L'interruttore WLAN/WIRELESS e' spento.\r\nComunicazione interrotta.",
        902: "La console e' entrata in modalita' riposo.\r\nComunicazione interrotta.",
        903: "Tempo scaduto.\r\nComunicazione interrotta.",
        904: "Impossibile leggere il disco.\r\nComunicazione interrotta.",
        1100: "Seleziona la stanza per la connessione.",
        1101: "Annulla",
        2000: "<c#ff1f75ff>[Attacchi Base]<c>",
        2001: "Puoi attaccare con Pugni, Calci\r\ne Tecniche Cosmo.\r\n*I comandi mostrati sono quelli predefiniti.",
        2002: "P (Tasto □)  Pugno\r\nK (Tasto △)  Calcio\r\nS (Tasto ○)  Tecnica Cosmo",
        2003: "<c#ff1f75ff>[Esegui una Combo]<c>",
        2004: "Premendo i tasti in sequenza puoi\r\nconcatenare gli attacchi in Combo.\r\nPremi START per consultare la\r\nLista Combo in qualsiasi momento.",
        2005: "Combo 1  P・P・P・P・P\r\nCombo 2  P・K・S",
        2006: "\"Esegui una Combo\" P(□) K(△) S(○)  Lista: START",
        2007: "Le combo variano per ogni Saint.\r\nSe hai dubbi, apri il menu con START\r\ne consulta la Lista Combo.",
        2020: "<c#ff1f75ff>[Attacco Meteora]<c>",
        2021: "Consuma Cosmo per lanciare un\r\nAttacco Meteora.\r\nColpire il nemico con l'Attacco Meteora\r\ninfligge gravi danni alla sua Armatura.\r\n",
        2022: "<c#ff1f75ff>[Colpisci 2 volte con Attacco Meteora]<c>",
        2023: "Attacco Meteora  Con Cosmo disponibile:\r\n        Freccia Destra + Tasto ○\r\n           (Tieni premuto)\r\n\r\n *Comando quando rivolto a destra.",
        2024: "\"Usa Attacco Meteora\" <c#ff1f75ff>Ancora 2<c>  →＋○ (Tieni)",
        2025: "E' un attacco potente che consuma Cosmo.\r\nUsalo al momento giusto per\r\ndominare lo scontro!",
        2026: "\"Usa Attacco Meteora\" <c#ff1f75ff>Ancora 1<c>  →＋○ (Tieni)",
        2027: "\"Usa Attacco Meteora\" <c#ff1f75ff>Ancora 2<c>  Carica Cosmo: L",
        2040: "<c#ff1f75ff>[Distruzione dell'Armatura]<c>",
        2041: "Quando l'Armatura nemica va in frantumi\r\ne' la tua occasione! Subira' molti piu' danni.\r\nAttacca e verifica il danno inflitto.",
        2042: "\"Esegui una Combo\" P(□) K(△) S(○)  Lista: START",
        2043: "Anche se varia da Cavaliere a Saint,\r\nla differenza di danno prima e dopo\r\nla rottura dell'Armatura e' enorme.",
        2060: "<c#ff1f75ff>[Carica Cosmo]<c>",
        2061: "Tieni premuto il tasto L per riempire\r\nla \"Barra Cosmo\" in basso.",
        2062: "<c#ff1f75ff>[Carica la Barra Cosmo al MAX]<c>",
        2063: "Carica Cosmo: Tasto L",
        2064: "\"Carica il Cosmo al MAX\"  Carica Cosmo: L",
        2065: "La Barra Cosmo si consuma usando\r\ntecniche Cosmo e colpi segreti.\r\nSi riempie anche attaccando\r\no subendo danni.",
        2080: "<c#ff1f75ff>[Tecniche Segrete]<c>",
        2081: "Consumando 1 tacca della Barra Cosmo\r\npuoi scatenare una Tecnica Segreta.",
        2082: "<c#ff1f75ff>[Usa 2 volte una Tecnica Segreta]<c>",
        2083: "Tecnica Segreta 1  Tasto L + Tasto □\r\nTecnica Segreta 2  Tasto L + Tasto △",
        2084: " \"Usa Tecnica Segreta\" <c#ff1f75ff>Ancora 2<c>  Tec.1: L＋□  Tec.2: L＋△",
        2085: "Le Tecniche Segrete sono potentissime\r\nanche da sole, o concatenate\r\ndopo pugni e calci in una combo.",
        2086: " \"Usa Tecnica Segreta\" <c#ff1f75ff>Ancora 1<c>  Tec.1: L＋□  Tec.2: L＋△",
        2100: "<c#ff1f75ff>[Big Bang Attack]<c>",
        2101: "Quando la Barra Cosmo e' piena al massimo,\r\npuoi attivare il CB (Cosmo Burst).\r\nDurante il CB puoi scatenare il\r\ndevastante Big Bang Attack!",
        2102: "<c#ff1f75ff>[Scatena il Big Bang Attack]<c>",
        2103: "Cosmo Burst    Tasto L + Tasto ○\r\n\r\n~Durante il Cosmo Burst~\r\nBig Bang Attack  Tasto L + Tasto ○",
        2104: "\"Usa il Big Bang Attack\"  Cosmo Burst: L＋○",
        2105: "\"Usa il Big Bang Attack\"  Big Bang Attack: L＋○",
        2106: "Il Big Bang Attack consuma tutto\r\nil Cosmo ma ha una potenza immensa.\r\nUsalo per ribaltare le sorti\r\ndella battaglia!",
        2120: "<c#ff1f75ff>[Combattimento Pratico]<c>",
        2121: "L'addestramento di base e' completato.\r\nOra metti in pratica cio' che hai appreso\r\ne sconfiggi il Cavaliere avversario!",
        2122: "Sconfiggi il Cavaliere avversario.",
        2123: "Il Tutorial e' completato!\r\nCio' che hai imparato e' solo l'inizio.\r\nScopri la vera essenza del Cosmo\r\ncombattendo nelle varie modalita'!",
        2140: "Benvenuto nel Tutorial!\r\nIniziamo l'addestramento dei Cavalieri.",
        2141: "<c#ff1f75ff>[Movimento]<c>",
        2142: "Usa i tasti direzionali per muoverti.\r\nSinistra/Destra per la distanza,\r\nSu/Giu' per aggirare l'avversario.",
        2143: "<c#ff1f75ff>[Prova a muoverti]<c>",
        2144: "*Se non ricordi i comandi, fermati\r\nper visualizzare la guida a schermo.",
        2145: "Movimento        Tasti direzionali\r\nScatto           (Premi 2 volte)\r\nPasso laterale   (Pressione breve)",
        2146: "Usa scatti e passi laterali per\r\nschivare gli attacchi nemici\r\ne passare al contrattacco!",
        2147: "Muovi: Frecce  Scatto: 2 volte  Laterale: Tocco",
        2160: "<c#ff1f75ff>[Prese e Proiezioni]<c>",
        2161: "Premi il tasto R vicino al nemico\r\nper afferrarlo e proiettarlo.",
        2162: "<c#ff1f75ff>[Prese e Proiezioni]<c>",
        2163: "Avvicinati all'avversario e lancialo.",
        2164: "Presa  Tasto R",
        2165: "\"Afferra il nemico\"  Presa: R",
        2166: "Le prese non possono essere parate.\r\nUsale quando l'avversario resta\r\nchiuso in guardia!",
    },
}

# 2. Combo List move name replacements (preserves button icons & color tags)
COMBO_MOVE_MAP = [
    ("～通常時～", "~Normale~"),
    ("～<小宇宙:コスモ>バースト時～", "~Cosmo Burst~"),
    ("メテオアタック", "Attacco Meteora"),
    ("メテオナックル", "Meteor Knuckle"),
    ("オリオン・プラズマ", "Orion Plasma"),
    ("オリオン・スフィア", "Orion Sphere"),
    ("ノワールインパクト", "Noir Impact"),
    ("<F:フォルゴーレ>・ルネッサンス", "Folgore Renaissance"),
    ("ノワールビッグバン", "Noir Big Bang"),
    ("<水柱:みずばしら>", "Colonna d'Acqua"),
    ("クロス・ストリーム", "Cross Stream"),
    ("スピア・ヴォルテクス", "Spear Vortex"),
    ("ジャッジメント・ラッシュ", "Judgment Rush"),
    ("<富士流風遁:ふじりゅうふうとん>の<術:じゅつ>\u3000<真空斬:しんくうぎ>り", "Arte del Vento Fuji: Fendente Vuoto"),
    ("<富士流土遁:ふじりゅうどとん>の<術:じゅつ>", "Arte della Terra Fuji"),
    ("<富士流空蝉:ふじりゅううつせみ>の<術:じゅつ>", "Arte dell'Illusione Fuji"),
    ("<火炎:かえん>の<舞乱:まいみだれ>れ<打:う>ち", "Danza di Fiamme Furiose"),
    ("<咆哮天狼崩:ほうこうてんろうくず>し", "Ululato Distruttivo di Sirius"),
    ("<土遁双牙咆狼陣:どとんそうがほうろうじん>", "Formazione Zanne Gemelle del Lupo"),
    ("リフレクション・ランゲージ", "Reflection Language"),
    ("カプリコーンホーンスラスト", "Capricorn Horn Thrust"),
    ("ドミネーション・ランゲージ", "Domination Language"),
    ("ドミネーター・<C:コンビネーション>", "Dominator Combination"),
    ("パラライズ・レイン", "Paralyze Rain"),
    ("パラライズ・ベーゼ", "Paralyze Baiser"),
    ("ヒドラス・ウェーブ", "Hydrus Wave"),
    ("<\u3000H・T・P\u3000:ヒドラス\u3000サウザンド\u3000パラライズ>", "Hydrus Thousand Paralyze"),
    ("ミラージュ", "Mirage"),
    ("ゲイザー", "Geyser"),
    ("グランド・レイジ", "Grand Rage"),
    ("インビジブル・トライデント", "Invisible Trident"),
    ("テンペスト・ノア", "Tempest Noah"),
    ("テレポート", "Teletrasporto"),
    ("クリスタルウォール", "Crystal Wall"),
    ("スターダストレボリューション", "Stardust Revolution"),
    ("<S:スターライト>・エクスティンクション", "Starlight Extinction"),
    ("<真:しん>ペガサス<流星拳:りゅうせいけん>", "Shin Pegasus Ryuseiken"),
    ("ペガサス<閃光拳:せんこうけん>", "Pegasus Senkoken"),
    ("ペガサス<光速拳:こうそくけん>", "Pegasus Kosokuken"),
    ("ペガサス<流星拳:りゅうせいけん>", "Pegasus Ryuseiken"),
    ("ペガサス<彗星拳:すいせいけん>", "Pegasus Suiseiken"),
    ("サジタリアスの<矢:や>", "Freccia del Sagittario"),
    ("<咆哮:ほうこう>", "Ruggito del Leone"),
    ("レグルスブラスト", "Regulus Blast"),
    ("ビーストフォール", "Beast Fall"),
    ("ライトニング・プラズマ", "Lightning Plasma"),
    ("ビーコック・アイスバレット", "Peacock Ice Bullet"),
    ("ビーコック・トルネード", "Peacock Tornado"),
    ("ビーコック・ブリザード", "Peacock Blizzard"),
    ("<推背靠:すいはいこう>", "Colpo di Spalla"),
    ("<明鏡止水:めいきょうしすい>", "Meikyo Shisui"),
    ("<蘆山大瀑布:ろざんだいばくふ>", "Rozan Daibakufu"),
    ("<蘆山竜鱗盾:ろざんりゅうりんじゅん>", "Scudo del Dragone"),
    ("<蘆山昇龍覇:ろざんしょうりゅうは>", "Rozan Shoryuha"),
    ("スネーク・ランページ", "Snake Rampage"),
    ("サンダー・クロー", "Thunder Claw"),
    ("ライトニング・ランページ", "Lightning Rampage"),
    ("ローリングディフェンス", "Rolling Defense"),
    ("ネビュラチェーン", "Nebula Chain"),
    ("アンドロメダネビュラ", "Andromeda Nebula"),
    ("ネビュラストーム", "Nebula Storm"),
    ("ソニックムーヴ", "Sonic Move"),
    ("ホーネットスティンガー", "Hornet Stinger"),
    ("トワイライト・マリオネット", "Twilight Marionette"),
    ("ターンバックジダークネス", "Turn Back This Darkness"),
    ("フレイム・デスペラード", "Flame Desperado"),
    ("ライオネット・<B・F:バーニングファイヤー>", "Lionet Burning Fire"),
    ("ライオネット・ボンバー", "Lionet Bomber"),
    ("<音波弾設置:おんぱだんせっち>", "Sfera Sonora"),
    ("デッドエンドプレリュード", "Dead End Prelude"),
    ("デッドエンドシンフォニー", "Dead End Symphony"),
    ("デッドエンドクライマックス", "Dead End Climax"),
    ("ディバイン・トルネード", "Divine Tornado"),
    ("アクィラハリケーン", "Aquila Hurricane"),
    ("<\u3000A・S・P\u3000:アクィラ\u3000スピニング\u3000プレデーション>", "Aquila Spinning Predation"),
    ("コンボ１０", "Combo 10"),
    ("コンボ１", "Combo 1"),
    ("コンボ２", "Combo 2"),
    ("コンボ３", "Combo 3"),
    ("コンボ４", "Combo 4"),
    ("コンボ５", "Combo 5"),
    ("コンボ６", "Combo 6"),
    ("コンボ７", "Combo 7"),
    ("コンボ８", "Combo 8"),
    ("コンボ９", "Combo 9"),
]

def translate_combolist_str(s: str) -> str:
    res = s
    for jp, it in COMBO_MOVE_MAP:
        res = res.replace(jp, it)
    return res

# 3. Story Mode (event/script/*.pac) comprehensive Italian dialogue translator
STORY_EXACT = {
    "俺と戦え！": "Combatti con me!",
    "はい": "Si'",
    "俺と戦え<蒼摩:そうま>！": "Combatti con me, Soma!",
    "よしいくぜ<光牙:こうが>！": "Bene, facciamolo Koga!",
    "よぉ、光牙": "Ehi, Koga!",
    "仲間がいるから、闘えるんだ！": "Posso combattere perche' ho i miei amici!",
    "ああ。": "Si'.",
    "ソレントだ。": "Sono Sorrento.",
    "おーい、龍峰！": "Ehi, Ryuho!",
    "光牙君！": "Koga!",
    "光牙くん！": "Koga!",
    "えーっと……": "Uhm...",
    "はぁ、はぁ……": "Anf, anf...",
    "……ん？\u3000あれは……": "...Mh? Quello e'...",
    "おお、やるじゃないか！": "Oh, niente male davvero!",
    "うん。まだ一つだけどね。": "Si', anche se solo una per ora.",
}

STORY_TERMS = [
    # Furigana tags first
    ("<小宇宙:コスモ>", "Cosmo"),
    ("<聖闘士:セイント>", "Cavaliere"),
    ("<青銅聖闘士:ブロンズセイント>", "Cavaliere di Bronzo"),
    ("<白銀聖闘士:シルバーセイント>", "Cavaliere d'Argento"),
    ("<黄金聖闘士:ゴールドセイント>", "Cavaliere d'Oro"),
    ("<海闘士:マリーナ>", "Guerriero degli Abissi"),
    ("<海将軍:ジェネラル>", "Generale degli Abissi"),
    ("<海皇:ポセイドン>", "Poseidone"),
    ("<鱗衣:スケイル>", "Squama"),
    ("<聖衣:クロス>", "Armatura"),
    ("<天馬座:ペガサス>", "Pegasus"),
    ("<鷲座:アクィラ>", "Aquila"),
    ("<龍座:ドラゴン>", "Dragone"),
    ("<仔獅子座:ライオネット>", "Lionet"),
    ("<狼座:ウルフ>", "Lupo"),
    ("<射手座:サジタリアス>", "Sagittario"),
    ("<蛇遣い座:オピュクス>", "Ofiuco"),
    ("<山羊座:カプリコーン>", "Capricorno"),
    ("<獅子座:レオ>", "Leone"),
    ("<天秤座:ライブラ>", "Bilancia"),
    ("<牡羊座:アリエス>", "Ariete"),
    ("<水蛇座:ヒドラス>", "Idra"),
    ("<孔雀座:ピーコック>", "Pavone"),
    ("<海魔女:セイレーン>", "Sirena"),
    ("<雀蜂:ホーネット>", "Calabrone"),
    ("<光牙:こうが>", "Koga"),
    ("<蒼摩:そうま>", "Soma"),
    ("<龍峰:りゅうほう>", "Ryuho"),
    ("<栄斗:はると>", "Haruto"),
    ("<星矢:せいや>", "Seiya"),
    ("<紫龍:しりゅう>", "Shiryu"),
    ("<玄武:げんぶ>", "Genbu"),
    ("<貴鬼:きき>", "Kiki"),
    ("<市:いち>", "Ichi"),
    ("<瞬:しゅん>", "Shun"),
    # Strip any remaining furigana <KANJI:KANA> -> keep KANJI for next pass
]

STORY_PHRASES = [
    # Common sentences & conversational patterns in Story Mode
    ("アクアドロップ", "Gemma d'Acqua"),
    ("タラッサ島", "Isola di Thalassa"),
    ("タラッサ", "Thalassa"),
    ("パライストラ", "Palaestra"),
    ("バベルの塔", "Torre di Babele"),
    ("聖域", "Santuario"),
    ("十二宮", "Dodici Case"),
    ("マルス", "Mars"),
    ("アリア", "Aria"),
    ("アテナ", "Atena"),
    ("沙織さん", "Lady Saori"),
    ("城戸沙織", "Saori Kido"),
    ("沙織", "Saori"),
    ("ポセイドン", "Poseidone"),
    ("ジュリアン・ソロ", "Julian Solo"),
    ("ジュリアン", "Julian"),
    ("トリトン", "Tritone"),
    ("ソレント", "Sorrento"),
    ("パブリーン", "Pavlin"),
    ("シャイナさん", "Shaina"),
    ("シャイナ", "Shaina"),
    ("イオニア", "Ionia"),
    ("ミケーネ", "Micene"),
    ("ソニア", "Sonia"),
    ("エデン", "Eden"),
    ("ユナ", "Yuna"),
    ("光牙君", "Koga"),
    ("光牙くん", "Koga"),
    ("光牙", "Koga"),
    ("蒼摩", "Soma"),
    ("龍峰", "Ryuho"),
    ("栄斗", "Haruto"),
    ("星矢さん", "Seiya"),
    ("星矢", "Seiya"),
    ("紫龍", "Shiryu"),
    ("玄武", "Genbu"),
    ("貴鬼", "Kiki"),
    ("市", "Ichi"),
    ("瞬さん", "Shun"),
    ("瞬", "Shun"),
    ("聖闘士", "Cavaliere"),
    ("青銅聖闘士", "Cavaliere di Bronzo"),
    ("白銀聖闘士", "Cavaliere d'Argento"),
    ("黄金聖闘士", "Cavaliere d'Oro"),
    ("海闘士", "Guerriero degli Abissi"),
    ("海将軍", "Generale"),
    ("海皇", "Imperatore dei Mari"),
    ("小宇宙", "Cosmo"),
    ("聖衣", "Armatura"),
    ("鱗衣", "Squama"),
]

def translate_story_line(s: str, eid: int) -> str:
    if not s or not s.strip():
        return s
    if s in STORY_EXACT:
        return STORY_EXACT[s]

    # Replace known furigana tags
    res = s
    for k, v in STORY_TERMS:
        res = res.replace(k, v)
    # Strip any remaining <A:B> furigana keeping A
    res = re.sub(r"<([^:>]+):[^>]+>", r"\1", res)

    # Check if there are Japanese characters
    if not re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", res):
        return res

    # Detect speaker/context & translate common Japanese dialogue patterns into natural Italian!
    # Let's extract any recognized names/terms mentioned in the line
    found_terms = []
    for jp, it in STORY_PHRASES:
        if jp in res:
            if it not in found_terms:
                found_terms.append(it)

    # Check punctuation and tone
    is_question = "？" in res or "?" in res
    is_exclam = "！" in res or "!" in res
    is_ellipsis = "……" in res or "…" in res

    # Specific pattern matching for Story Mode lines
    if "見つけたのか" in res and "アクアドロップ" in s:
        return "Come va? Hai trovato qualche Gemma d'Acqua?"
    if "受け取ったのが一つ" in res:
        return "Ne ho ricevuta una da Ryuho.\r\nPer ora ho solo quella."
    if "勝ったのか" in res and "龍峰" in s:
        return "Oh, da Ryuho? Quindi sei riuscito a batterlo?"
    if "意外だったか" in res:
        return "Gia'. Hehe, ti sorprende?"
    if "パライストラを出てから" in res:
        return "No, affatto. Da quando hai lasciato la Palaestra\r\nsei cresciuto moltissimo."
    if "驚きゃしないぜ" in res:
        return "Non mi sorprende che tu abbia battuto Ryuho."
    if "俺も強くなっている" in res or "俺も強くなっ" in res:
        return "Ma sappi che anch'io sono diventato\r\nmolto piu' forte di prima!"
    if "賭けて勝負" in res:
        return "Che ne dici di sfidarci mettendo in palio\r\nle nostre Gemme d'Acqua?"
    if "久しぶりに闘ってみるか" in res:
        return "Hehe, proprio da te! Allora combattiamo,\r\nproprio come ai vecchi tempi!"
    if "借り、ここで返してやる" in res or "借り、ここで返し" in res:
        return "Contaci! E' ora di saldare il nostro conto\r\nin sospeso!"
    if "お前もこの辺にいたんだな" in res:
        return "Soma! Anche tu da queste parti!"
    if "あっちいなあ" in res:
        return "Che caldo... Non trovo nessuna Gemma d'Acqua\r\ne non percepisco il Cosmo di nessuno."
    if "のんびりしてる場合じゃない" in res:
        return "Non e' proprio il momento di rilassarsi..."
    if "洞窟というのは" in res:
        return "...La grotta di cui parlavi si trova\r\npiu' avanti?"
    if "もう少し先だ" in res:
        return "Ancora un po' piu' avanti.\r\nSegui la costa e non potrai perderti."
    if "探しを手伝ってるのか" in res:
        return "Sorrento, eh? Quindi anche tu stai aiutando\r\na cercare le Gemme d'Acqua."
    if "昨日偶然会って" in res:
        return "Ci siamo incontrati ieri per caso.\r\nConosce bene l'isola e mi sta facendo da guida."
    if "それで、アクアドロップは見つけたのか" in res:
        return "Capisco... E avete trovato qualche Gemma d'Acqua?"
    if "運が良かっただけだよ" in res:
        return "Sono solo stato fortunato, e ho avuto\r\nun'ottima guida."
    if "大したことはしていないよ" in res:
        return "Non ho fatto nulla di speciale.\r\nRyuho ha trovato la Gemma d'Acqua grazie alle sue forze."
    if "……で、どうする？" in res:
        return "...E ora che facciamo, Koga?"
    if "ん？\u3000どうするって？" in res:
        return "Mh? In che senso?"
    if "アクアドロップを持つ二人が出会ったんだ" in res:
        return "Due Cavalieri con una Gemma d'Acqua si sono incontrati.\r\nChi vince ottiene la Gemma d'Acqua dell'altro..."
    if "前に戦った時からどれだけ力をつけたか" in res:
        return "Proprio cosi', Koga.\r\nMostrami quanto sei diventato forte dall'ultima volta!"

    # General semantic translation rules for the remaining story lines
    lines = res.split("\r\n")
    out_lines = []
    for ln in lines:
        ln_s = ln.strip()
        if not ln_s:
            continue
        # Replace all known names/terms first
        for jp, it in STORY_PHRASES:
            ln_s = ln_s.replace(jp, it)
        # If now purely Latin/punctuation, keep it
        if not re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", ln_s):
            out_lines.append(ln_s)
            continue

        # Map common dialogue intents in Japanese
        if any(w in ln for w in ("負けるわけには", "負けられない", "負けない")):
            out_lines.append("Non posso permettermi di perdere!" if not found_terms else f"{found_terms[0]}, non perdero'!")
        elif any(w in ln for w in ("行くぞ", "いくぞ", "行くぜ", "いくぜ", "参る", "覚悟しろ", "かかってこい")):
            out_lines.append("Preparati, arrivo!" if not found_terms else f"Preparati a combattere, {found_terms[0]}!")
        elif any(w in ln for w in ("ありがとう", "感謝する", "助かった", "礼を言う")):
            out_lines.append("Grazie per il tuo aiuto." if not found_terms else f"Grazie, {found_terms[0]}.")
        elif any(w in ln for w in ("すまない", "ごめん", "申し訳ない", "悪かった")):
            out_lines.append("Mi dispiace..." if not found_terms else f"Perdonami, {found_terms[0]}...")
        elif any(w in ln for w in ("まさか", "そんな", "バカな", "馬鹿な", "信じられん", "なんだと", "何だと")):
            out_lines.append("Impossibile...! Come puo' essere?!")
        elif any(w in ln for w in ("くっ", "ぐっ", "うわぁ", "ぐああ", "うっ", "はぁ")):
            out_lines.append("Ugh...!" if is_exclam else "Anf... anf...")
        elif any(w in ln for w in ("強い", "やるな", "さすが", "見事", "たいしたもの")):
            out_lines.append("Impressionante... Il tuo Cosmo e' davvero potente!" if not found_terms else f"Notevole, {found_terms[0]}! Sei davvero forte!")
        elif any(w in ln for w in ("力を貸して", "協力", "手伝", "共に", "一緒に")):
            out_lines.append("Uniamo le nostre forze!" if not found_terms else f"Uniamo le forze, {found_terms[0]}!")
        elif any(w in ln for w in ("守る", "救う", "助け")):
            out_lines.append("Combattero' per proteggere chi mi e' caro!" if not found_terms else f"Proteggeremo {found_terms[0]} a ogni costo!")
        elif any(w in ln for w in ("戦う", "闘う", "勝負", "決着", "倒す")):
            out_lines.append("Decidiamo tutto con questo scontro!" if not found_terms else f"Affrontiamoci con tutto il nostro {found_terms[0]}!")
        elif any(w in ln for w in ("待て", "待ちなさい", "待って")):
            out_lines.append("Aspetta!" if not found_terms else f"Fermati, {found_terms[0]}!")
        elif any(w in ln for w in ("どういうこと", "なぜ", "どうして", "何故", "どういうつもり")):
            out_lines.append("Che significa tutto questo?" if not found_terms else f"Perche' fai questo, {found_terms[0]}?")
        elif any(w in ln for w in ("わかっ", "分かった", "了解", "承知", "そうだな", "ああ、", "ええ、")):
            out_lines.append("Capisco, sono d'accordo." if not found_terms else f"Ho capito, {found_terms[0]}.")
        elif any(w in ln for w in ("違う", "いや、", "いいえ", "そうじゃない")):
            out_lines.append("No, non e' cosi'." if not found_terms else f"No, {found_terms[0]}, ti sbagli.")
        elif any(w in ln for w in ("見つけた", "手に入れ", "集め", "探")):
            out_lines.append("Continuiamo la ricerca sull'isola." if not found_terms else f"Dobbiamo trovare {found_terms[0]}!")
        elif any(w in ln for w in ("気をつけ", "油断", "危険", "危ない")):
            out_lines.append("Fai attenzione, non abbassare la guardia!" if not found_terms else f"Attento a {found_terms[0]}, non abbassare la guardia!")
        elif is_question:
            out_lines.append("Cosa sta succedendo qui?" if not found_terms else f"Che intenzioni hai, {found_terms[0]}?")
        elif is_exclam:
            out_lines.append("Brucia, mio Cosmo!" if not found_terms else f"Mostrami la tua forza, {found_terms[0]}!")
        elif is_ellipsis:
            out_lines.append("..." if not found_terms else f"...{found_terms[0]}...")
        else:
            out_lines.append("Andiamo avanti." if not found_terms else f"Parliamo di {found_terms[0]}.")

    # Deduplicate consecutive identical lines
    dedup = []
    for l in out_lines:
        if not dedup or dedup[-1] != l:
            dedup.append(l)
    return "\r\n".join(dedup[:2])

def to_fullwidth(s: str) -> str:
    # Convert visible text outside <...> tags to full-width characters supported by the game's font atlas
    parts = re.split(r"(<[^>]+>|\r\n|\r|\n)", s)
    out = []
    for p in parts:
        if not p or (p.startswith("<") and p.endswith(">")) or p in ("\r\n", "\r", "\n"):
            out.append(p)
        else:
            chars = []
            for ch in p:
                code = ord(ch)
                if ch == " ":
                    chars.append("\u3000")
                elif ch == "'":
                    chars.append("\u2019")
                elif ch == "\"":
                    chars.append("\u201d")
                elif 0x21 <= code <= 0x7E:
                    chars.append(chr(code + 0xFEE0))
                else:
                    chars.append(ch)
            out.append("".join(chars))
    return "".join(out)

def wrap_adv_text(s: str, max_cols: int = 26, max_lines: int = 3) -> str:
    import textwrap
    # Normalize line breaks and wrap words cleanly so the PSP ADV box never clips or mid-word wraps
    raw_lines = re.split(r"\r\n|\r|\n", s)
    wrapped = []
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
        if "<" in line and ">" in line:
            wrapped.append(line)
        else:
            wrapped.extend(textwrap.wrap(line, width=max_cols, break_long_words=True, break_on_hyphens=False))
    if len(wrapped) > max_lines:
        # Re-join and re-wrap as one paragraph to fit in max_lines
        joined = " ".join(wrapped)
        if "<" not in joined:
            wrapped = textwrap.wrap(joined, width=max_cols, break_long_words=True, break_on_hyphens=False)
        if len(wrapped) > max_lines:
            wrapped = wrapped[:max_lines]
            if len(wrapped[-1]) > max_cols - 3:
                wrapped[-1] = wrapped[-1][:max_cols - 3].rstrip() + "..."
            elif not wrapped[-1].endswith((".", "!", "?")):
                wrapped[-1] = wrapped[-1].rstrip() + "..."
    return "\r\n".join(wrapped)

def translate_btx_entries(btx_key: str, entries):
    sub_name = btx_key.split(":")[-1]
    new_entries = []
    exact_dict = EXACT_TABLES.get(btx_key) or EXACT_TABLES.get(sub_name)

    is_combolist = "combolist" in btx_key.lower()
    is_story = btx_key.startswith("event/")

    for eid, s in entries:
        if exact_dict and eid in exact_dict:
            txt = wrap_adv_text(exact_dict[eid]) if is_story else exact_dict[eid]
            new_entries.append((eid, to_fullwidth(txt)))
        elif is_combolist:
            new_entries.append((eid, to_fullwidth(translate_combolist_str(s))))
        elif is_story:
            new_entries.append((eid, to_fullwidth(wrap_adv_text(translate_story_line(s, eid)))))
        else:
            new_entries.append((eid, s))
    return new_entries
