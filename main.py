import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PyPDF2 import PdfReader, PdfWriter
import pdfplumber
import logging
import re
import difflib
import threading

# Configurazione logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Utility: rende sicuro un nome per il filesystem
def sanitize_filename(name, max_length=200):
	# semplice pulizia: rimuove caratteri non validi e tronca
	name = re.sub(r'[\\/*?:"<>|]', "_", name)
	name = name.strip()
	if not name:
		name = "Nome_Sconosciuto"
	return name[:max_length]

# Utility: normalizza testo (lowercase, collapse whitespace)
def normalize_text(s):
	if not s:
		return ""
	return re.sub(r'\s+', ' ', s).strip().lower()

# Carica la lista dei nomi e costruisce una lookup normalizzata -> originale
def load_employee_names(filename):
	"""Carica la lista dei nomi dipendenti da un file txt."""
	# ...existing code...
	try:
		with open(filename, 'r', encoding='utf-8') as file:
			names = [line.strip() for line in file if line.strip()]
		# costruisci mapping normalizzato -> originale (mantiene il primo occorso)
		lookup = {}
		for n in names:
			norm = normalize_text(n)
			if norm and norm not in lookup:
				lookup[norm] = n
		return lookup
	except Exception as e:
		# usa logging per debug e messagebox per l'utente
		logging.exception("Errore durante la lettura del file dei nomi")
		messagebox.showerror("Errore", f"Errore durante la lettura del file dei nomi: {e}")
		return {}

def extract_names_from_pdf(pdf_path, employee_lookup, use_fuzzy=True, fuzzy_cutoff=0.85):
	"""Estrae i nomi cercando corrispondenze con la lista dei dipendenti.
	employee_lookup: dict normalizzato -> originale
	"""
	names = []
	try:
		with pdfplumber.open(pdf_path) as pdf:
			for i, page in enumerate(pdf.pages):
				text = page.extract_text()
				ntext = normalize_text(text)
				if not ntext:
					names.append(f"Nome_Sconosciuto_{i+1}")
					continue

				found_name = False
				# Primo: ricerca esatta per substring su normalizzato
				for norm_name, original_name in employee_lookup.items():
					if norm_name and norm_name in ntext:
						names.append(original_name)
						found_name = True
						logging.info(f"Nome trovato (esatto): {original_name} pagina {i+1}")
						break

				# Secondo: fuzzy match sui token (opzionale)
				if not found_name and use_fuzzy and employee_lookup:
					# Lista di chiavi normalizzate
					candidates = difflib.get_close_matches(ntext, list(employee_lookup.keys()), n=1, cutoff=fuzzy_cutoff)
					if not candidates:
						# alternativa: prova matching su singole parole della pagina con le chiavi
						words = set(ntext.split())
						best = None
						best_ratio = 0.0
						for key in employee_lookup.keys():
							for w in words:
								r = difflib.SequenceMatcher(None, w, key).ratio()
								if r > best_ratio:
									best_ratio = r
									best = key
						if best and best_ratio >= fuzzy_cutoff:
							candidates = [best]
					if candidates:
						orig = employee_lookup[candidates[0]]
						names.append(orig + " (fuzzy)")
						found_name = True
						logging.info(f"Nome trovato (fuzzy): {orig} pagina {i+1}")

				if not found_name:
					logging.info(f"Nessun nome trovato nella pagina {i+1}")
					names.append(f"Nome_Sconosciuto_{i+1}")

	except Exception as e:
		logging.exception("Errore durante l'estrazione")
		messagebox.showerror("Errore", f"Errore durante l'estrazione dei nomi: {e}")
	return names

def split_and_rename_pdf(input_file, output_folder):
	"""Divide il PDF in singole pagine e rinomina ogni pagina in base ai nomi estratti."""
	try:
		# Carica i nomi dal file txt (ora torna lookup normalizzata)
		employee_lookup = load_employee_names("dipendenti.txt")
		if not employee_lookup:
			messagebox.showerror("Errore", "Nessun nome dipendente trovato nel file.")
			return

		# Estrai i nomi dal PDF utilizzando la lista dei dipendenti
		names_list = extract_names_from_pdf(input_file, employee_lookup)
		try:
			reader = PdfReader(input_file)
		except Exception as e:
			logging.exception("Errore apertura PDF")
			messagebox.showerror("Errore", f"Impossibile aprire il PDF: {e}")
			return

		num_pages = len(reader.pages)
		# sicurezza: tronca o estendi names_list per corrispondere al numero di pagine
		if len(names_list) > num_pages:
			names_list = names_list[:num_pages]
		elif len(names_list) < num_pages:
			for i in range(len(names_list), num_pages):
				names_list.append(f"Nome_Sconosciuto_{i+1}")

		created = 0
		for i, name in enumerate(names_list):
			writer = PdfWriter()
			writer.add_page(reader.pages[i])

			base_name = sanitize_filename(name)
			counter = 1
			output_path = os.path.join(output_folder, f"{base_name}.pdf")

			while os.path.exists(output_path):
				output_path = os.path.join(output_folder, f"{base_name}_{counter}.pdf")
				counter += 1

			with open(output_path, "wb") as output_file:
				writer.write(output_file)
			created += 1

		messagebox.showinfo("Completato", f"Sono stati creati {created} file PDF.")
	except Exception as e:
		logging.exception("Errore durante la divisione del PDF")
		messagebox.showerror("Errore", f"Errore durante la divisione del PDF: {e}")

# Funzioni dell'interfaccia grafica rimangono invariate.

def select_file():
    file_path = filedialog.askopenfilename(title="Seleziona il file PDF", filetypes=[("File PDF", "*.pdf")])
    entry_file.delete(0, tk.END)
    entry_file.insert(0, file_path)

def select_folder():
    folder_path = filedialog.askdirectory(title="Seleziona la cartella di output")
    entry_folder.delete(0, tk.END)
    entry_folder.insert(0, folder_path)

def start_process():
	input_file = entry_file.get()
	output_folder = entry_folder.get()

	if not os.path.isfile(input_file):
		messagebox.showerror("Errore", "Il file PDF specificato non esiste.")
		return

	if not os.path.isdir(output_folder):
		messagebox.showerror("Errore", "La cartella di output specificata non esiste.")
		return

	# disabilita pulsanti e avvia in thread per non bloccare la GUI
	def worker():
		try:
			status_var.set("Elaborazione in corso...")
			button_start.config(state=tk.DISABLED)
			button_edit.config(state=tk.DISABLED)
			split_and_rename_pdf(input_file, output_folder)
		finally:
			status_var.set("Pronto")
			button_start.config(state=tk.NORMAL)
			button_edit.config(state=tk.NORMAL)

	threading.Thread(target=worker, daemon=True).start()

def edit_employee_list():
    """Apre una finestra per modificare la lista dei dipendenti."""
    edit_window = tk.Toplevel(root)
    edit_window.title("Modifica Lista Dipendenti")
    
    # Dimensioni e posizione della finestra
    window_width = 400
    window_height = 500
    screen_width = edit_window.winfo_screenwidth()
    screen_height = edit_window.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    edit_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    # Area di testo scrollabile
    text_area = scrolledtext.ScrolledText(edit_window, width=40, height=25)
    text_area.pack(padx=10, pady=10)

    # Carica il contenuto attuale del file
    try:
        with open("dipendenti.txt", 'r', encoding='utf-8') as file:
            content = file.read()
            text_area.insert(tk.END, content)
    except FileNotFoundError:
        text_area.insert(tk.END, "# Inserisci un nome per riga\n")

    def save_changes():
        """Salva le modifiche nel file."""
        try:
            with open("dipendenti.txt", 'w', encoding='utf-8') as file:
                file.write(text_area.get("1.0", tk.END))
            messagebox.showinfo("Successo", "Lista dipendenti salvata correttamente!")
            edit_window.destroy()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante il salvataggio: {e}")

    # Pulsanti
    button_frame = tk.Frame(edit_window)
    button_frame.pack(pady=10)
    
    tk.Button(button_frame, text="Salva", command=save_changes).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Chiudi", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)

# Creazione interfaccia grafica
root = tk.Tk()
root.title("Dividi e rinomina PDF")

window_width = 500
window_height = 170
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width/2 - window_width/2)
center_y = int(screen_height/2 - window_height/2)
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

tk.Label(root, text="File PDF:").grid(row=0, column=0, pady=5, padx=5)
entry_file = tk.Entry(root, width=50)
entry_file.grid(row=0, column=1, pady=5, padx=5)
tk.Button(root, text="Sfoglia", command=select_file).grid(row=0, column=2, pady=5, padx=5)

tk.Label(root, text="Cartella di output:").grid(row=1, column=0, pady=5, padx=5)
entry_folder = tk.Entry(root, width=50)
entry_folder.grid(row=1, column=1, pady=5, padx=5)
tk.Button(root, text="Sfoglia", command=select_folder).grid(row=1, column=2, pady=5, padx=5)

# Mantieni riferimento ai pulsanti per abil/disable
button_start = tk.Button(root, text="Avvia", command=start_process, width=20)
button_start.grid(row=2, column=1, pady=10)

button_edit = tk.Button(root, text="Modifica Lista Dipendenti", command=edit_employee_list)
button_edit.grid(row=3, column=1, pady=10)

# Etichetta di stato
status_var = tk.StringVar(value="Pronto")
status_label = tk.Label(root, textvariable=status_var)
status_label.grid(row=4, column=1, pady=5)

root.mainloop()