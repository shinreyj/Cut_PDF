# Cut_PDF

Un'utility Python con interfaccia grafica (Tkinter) per dividere un PDF in singole pagine e salvarle rinominandole in base ai nomi trovati nel testo di ciascuna pagina.

## Funzionalità principali

- Apri un PDF e salva ogni pagina come file PDF separato.
- Rinomina ogni pagina in base a un elenco di nomi (file `dipendenti.txt`) se uno dei nomi è trovato nel testo della pagina.
- Interfaccia grafica semplice per scegliere file e cartella di output.
- Editor integrato per modificare il file `dipendenti.txt` dall'app.
- Evita sovrascritture aggiungendo un indice quando un file con lo stesso nome esiste già.

## Requisiti

- Python 3.7+
- Dipendenze (elencate in `requirements.txt`): PyPDF2, pdfplumber, pdfminer.six, Pillow

## Installazione

1. Clona o copia il progetto in una cartella, ad es. `c:\Programmazzione\Cut_PDF`.
2. Crea e attiva un virtualenv (consigliato):
   - Windows (cmd): `python -m venv venv` e poi `venv\Scripts\activate`
   - PowerShell: `.\venv\Scripts\Activate.ps1`
   - macOS/Linux: `python3 -m venv venv` e `source venv/bin/activate`
3. Installa le dipendenze:
   - `python -m pip install --upgrade pip`
   - `python -m pip install -r requirements.txt`

Nota: se incontri `ModuleNotFoundError: No module named 'PyPDF2'`, assicurati di aver attivato il venv corretto prima di installare le librerie ed eseguire `main.py`.

## Uso

1. Avvia l'applicazione:
   - `python main.py`
2. Nell'interfaccia:
   - Seleziona il file PDF da processare (pulsante "Sfoglia").
   - Seleziona la cartella di output (pulsante "Sfoglia").
   - Premi "Avvia" per eseguire la divisione e il salvataggio delle pagine.
   - Usa "Modifica Lista Dipendenti" per aprire l'editor del file `dipendenti.txt` (un nome per riga).

Alla fine verranno creati tanti file PDF quante sono le pagine analizzate; ogni file avrà come nome il nome trovato (o `Nome_Sconosciuto_<n>` se nessun nome è stato identificato).

## Formato di dipendenti.txt

- File di testo UTF-8 con un nome per riga.
- Linee vuote vengono ignorate.
- È possibile aggiungere commenti manualmente (es. righe che iniziano con `#`), ma verranno considerate come voci se non filtrate.

Esempio:
```
Mario Rossi
Anna Bianchi
Carla Verdi
```

## Comportamento, limitazioni e suggerimenti

- L'algoritmo di ricerca esegue una corrispondenza esatta e case-sensitive dei nomi nel testo estratto dalla pagina. Per migliorare il matching considerare di normalizzare (lowercase, rimuovere accenti) sia i nomi sia il testo estratto.
- L'estrazione del testo dipende da `pdfplumber`/`pdfminer.six`: PDF scansionati come immagini potrebbero non restituire testo. In tal caso è necessaria l'OCR esterna (non inclusa).
- Alcuni caratteri non validi nei nomi potrebbero causare errori nel filesystem; evita caratteri come `<>:"/\\|?*` nel file `dipendenti.txt`.
- Se il PDF è protetto con password, il programma potrebbe non essere in grado di leggere le pagine; gestioni aggiuntive per PDF cifrati non sono previste in questa versione.

## Risoluzione problemi

- Errore: `ModuleNotFoundError: No module named 'PyPDF2'`
  - Assicurati che il virtualenv sia attivato e che le librerie siano installate dentro il venv (`python -m pip install -r requirements.txt`).
- L'app trova sempre `Nome_Sconosciuto` per tutte le pagine:
  - Verifica che `dipendenti.txt` contenga i nomi corretti.
  - Controlla che `pdfplumber` estragga testo dalla pagina (aprire il PDF con `pdfplumber` in un REPL e chiamare `page.extract_text()` per verificare).

## Struttura del progetto

```
Cut_PDF/
├── main.py                  # Applicazione GUI principale
├── requirements.txt         # Dipendenze del progetto
├── README.md                # Questo file (aggiornato)
├── install_requirements.bat # Script Windows per creare venv e installare dipendenze
├── install_requirements.sh  # Script Unix per creare venv e installare dipendenze
└── dipendenti.txt           # File dati: lista nomi (creare se assente)
```

## Contribuire

Pull request e segnalazioni di bug sono benvenute. Per modifiche importanti apri prima un'issue per discussione.

## Licenza

Progetto rilasciato sotto licenza MIT.