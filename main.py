import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PyPDF2 import PdfReader, PdfWriter
import pdfplumber

def load_employee_names(filename):
    """Carica la lista dei nomi dipendenti da un file txt."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            # Rimuove spazi extra e righe vuote
            names = [line.strip() for line in file if line.strip()]
        return names
    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante la lettura del file dei nomi: {e}")
        return []

def extract_names_from_pdf(pdf_path, employee_names):
    """Estrae i nomi cercando corrispondenze con la lista dei dipendenti."""
    names = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    names.append(f"Nome_Sconosciuto_{i+1}")
                    continue

                found_name = False
                # Cerca ogni nome della lista nel testo della pagina
                for employee_name in employee_names:
                    if employee_name in text:
                        names.append(employee_name)
                        found_name = True
                        print(f"Nome trovato: {employee_name}")
                        break
                
                if not found_name:
                    print(f"Nessun nome trovato nella pagina {i+1}")
                    names.append(f"Nome_Sconosciuto_{i+1}")
                    
    except Exception as e:
        print(f"Errore durante l'estrazione: {e}")
        messagebox.showerror("Errore", f"Errore durante l'estrazione dei nomi: {e}")
    return names

def split_and_rename_pdf(input_file, output_folder):
    """Divide il PDF in singole pagine e rinomina ogni pagina in base ai nomi estratti."""
    try:
        # Carica i nomi dal file txt
        employee_names = load_employee_names("dipendenti.txt")
        if not employee_names:
            messagebox.showerror("Errore", "Nessun nome dipendente trovato nel file.")
            return

        # Estrai i nomi dal PDF utilizzando la lista dei dipendenti
        names_list = extract_names_from_pdf(input_file, employee_names)
        reader = PdfReader(input_file)

        for i, name in enumerate(names_list):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])

            base_name = name
            counter = 1
            output_path = os.path.join(output_folder, f"{base_name}.pdf")

            while os.path.exists(output_path):
                output_path = os.path.join(output_folder, f"{base_name}_{counter}.pdf")
                counter += 1

            with open(output_path, "wb") as output_file:
                writer.write(output_file)

        messagebox.showinfo("Completato", f"Sono stati creati {len(names_list)} file PDF.")
    except Exception as e:
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

    split_and_rename_pdf(input_file, output_folder)

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

tk.Button(root, text="Avvia", command=start_process, width=20).grid(row=2, column=1, pady=10)

tk.Button(root, text="Modifica Lista Dipendenti", command=edit_employee_list).grid(row=3, column=1, pady=10)

root.mainloop()