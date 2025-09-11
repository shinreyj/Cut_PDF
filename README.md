# Cut PDF

Un'applicazione Python per tagliare e manipolare file PDF in modo semplice ed efficiente.

## 🚀 Funzionalità

- Estrazione di pagine specifiche da PDF
- Divisione di PDF in più file
- Unione di più PDF in un unico file
- Rotazione di pagine
- Estrazione di testo da PDF

## 📋 Prerequisiti

Prima di iniziare, assicurati di avere installato:

- Python 3.7 o superiore
- pip (gestore di pacchetti Python)

## 🔧 Installazione

1. Clona il repository:
```bash
git clone https://github.com/TUO_USERNAME/Cut_PDF.git
cd Cut_PDF
```

2. Crea un ambiente virtuale (consigliato):
```bash
python -m venv venv
```

3. Attiva l'ambiente virtuale:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

## 💻 Utilizzo

### Esempio base:

```python
from cut_pdf import PDFCutter

# Crea un'istanza del cutter
cutter = PDFCutter("documento.pdf")

# Estrai pagine specifiche
cutter.extract_pages([1, 3, 5], "output.pdf")

# Dividi il PDF in file separati
cutter.split_pdf()
```

### Eseguire l'applicazione:

```bash
python main.py
```

## 🛠️ Configurazione

È possibile configurare l'applicazione modificando il file `config.py` (se presente) o utilizzando variabili d'ambiente.

## 📁 Struttura del Progetto

```
Cut_PDF/
│
├── main.py           # Entry point dell'applicazione
├── requirements.txt  # Dipendenze Python
├── README.md        # Questo file
├── .gitignore       # File e cartelle da ignorare in Git
│
├── src/             # Codice sorgente
│   ├── __init__.py
│   └── pdf_cutter.py
│
└── tests/           # Test unitari
    └── test_pdf_cutter.py
```

## 🤝 Contribuire

Le pull request sono benvenute! Per modifiche importanti:

1. Fork del progetto
2. Crea il tuo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📝 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per maggiori informazioni.

## ✍️ Autore

- **Il tuo nome** - [TUO_USERNAME](https://github.com/TUO_USERNAME)

## 🙏 Riconoscimenti

- PyPDF2 per la manipolazione dei PDF
- Altri contributori e librerie utilizzate

---

**Nota**: Questo progetto è in fase di sviluppo attivo. Per segnalare bug o richiedere nuove funzionalità, apri una issue su GitHub.