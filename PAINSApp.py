import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import messagebox
from PIL import Image, ImageTk
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams
from tqdm import tqdm
from tkinter import ttk


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("PAINSApp")

        self.df = None
        self.file_type = None

        self.menu()
        self.button()

        self.initialize_widgets()

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def initialize_widgets(self):
        """Widget initialization"""

        self.text_widget = tk.Text(
            self.root, height=20, width=80, bg="light blue"
        )
        self.text_widget.grid(row=1, column=0, pady=10, padx=10, sticky="nsew")

        self.scrollbar = tk.Scrollbar(self.root, command=self.text_widget.yview)
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        self.text_widget.config(yscrollcommand=self.scrollbar.set)

        self.image_frame = tk.Frame(self.root)
        self.image_frame.grid(row=2, column=0, pady=10, padx=10, sticky="nsew")

        self.progress = ttk.Progressbar(
            self.root, orient="horizontal", mode="determinate"
        )
        self.progress.grid(row=3, column=0, pady=10, padx=10, sticky="ew")

    def clear_widgets(self):
        """Removes all widgets from the window and returns the application to its initial state"""
        for widget in self.root.winfo_children():
            widget.destroy()

        self.menu()
        self.button()
        self.initialize_widgets()

    def load_file(self, file_type):
        filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
        self.file_path = filedialog.askopenfilename(
            title="Select file", filetypes=filetypes
        )

        if self.file_path:
            try:
                self.df = pd.read_csv(self.file_path)
                self.file_type = file_type

                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert(tk.END, self.df.to_string())

                self.root.update_idletasks()

            except Exception as e:
                messagebox.showerror("Error", f"Cannot open CSV file: {str(e)}")
        else:
            pass

    def preparation_and_pains_assay(self):
        if self.df is not None:
            params = FilterCatalogParams()
            params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
            catalog = FilterCatalog(params)

            matches = []
            clean = []

            self.progress["maximum"] = self.df.shape[0]
            self.progress["value"] = 0
            self.root.update_idletasks()

            for index, row in tqdm(self.df.iterrows(), total=self.df.shape[0]):
                molecule = Chem.MolFromSmiles(row["Smiles"])
                entry = catalog.GetFirstMatch(molecule)
                if entry is not None:
                    matches.append(
                        {
                            "ID": row["ID"],
                            "rdkit_molecule": molecule,
                            "pains": entry.GetDescription().capitalize(),
                        }
                    )
                else:
                    clean.append(index)

                self.progress["value"] = index + 1
                self.root.update_idletasks()

            matches_df = pd.DataFrame(matches)
            self.df = self.df.loc[clean]

            results = []
            results.append(f"Number of compounds with PAINS: {len(matches_df)}")
            results.append(f"Number of compounds without PAINS: {len(self.df)}")

            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert(tk.END, "\n".join(results) + "\n\n")

            if not matches_df.empty:
                self.display_molecules(matches_df)

            self.progress["value"] = 0
            self.root.update_idletasks()

        else:
            messagebox.showwarning(
                "Alert", "No data to analyze. Import CSV file previously."
            )

    def display_molecules(self, matches_df):
        for widget in self.image_frame.winfo_children():
            widget.destroy()

        if not matches_df.empty and "rdkit_molecule" in matches_df.columns:
            img = Draw.MolsToGridImage(
                list(matches_df["rdkit_molecule"]),
                legends=[
                    f"{row['ID']}: {row['pains']}"
                    for _, row in matches_df.iterrows()
                ],
                molsPerRow=4,
                subImgSize=(200, 200),
            )

            img_tk = ImageTk.PhotoImage(image=img)

            label = tk.Label(self.image_frame, image=img_tk)
            label.image = img_tk
            label.pack()
        else:
            self.image_frame.update_idletasks()

    def run_analysis(self):
        self.display_molecules(pd.DataFrame())

        if self.file_type == "chembl":
            self.df.drop(
                columns=[
                    "Standard_Type",
                    "Standard_Relation",
                    "Standard_Units",
                    "Document_ChEMBL_ID",
                    "Target_Name",
                    "Action_Type",
                    "Standard_Value",
                ],
                inplace=True,
                errors="ignore",
            )
            self.df.rename(columns={"Molecule_ChEMBL_ID": "ID"}, inplace=True)
            self.preparation_and_pains_assay()
        elif self.file_type == "own_csv":
            self.preparation_and_pains_assay()
        else:
            messagebox.showwarning(
                "Alert", "No data to analyze. Import CSV file previously."
            )

    def button(self):
        def on_run_analysis(event):
            self.run_analysis()

        def clear_output(event):
            self.clear_widgets()

            self.df = None
            self.file_type = None

        self.b = tk.Button(self.root, text="Run analysis")
        self.b.bind("<Button-1>", on_run_analysis)
        self.b.grid(row=0, column=0, pady=10, padx=10)

        self.b2 = tk.Button(self.root, text="Clear output")
        self.b2.bind("<Button-1>", clear_output)
        self.b2.grid(row=0, column=1, pady=10, padx=10)

    def menu(self):
        self.main_menu = tk.Menu(self.root)
        self.root.config(menu=self.main_menu)

        self.file_menu = tk.Menu(self.main_menu, tearoff=0)
        self.main_menu.add_cascade(label="File", menu=self.file_menu)

        self.import_menu = tk.Menu(self.file_menu, tearoff=0)
        self.file_menu.add_cascade(label="Import data", menu=self.import_menu)

        self.import_menu.add_command(
            label="Chembl file", command=lambda: self.load_file("chembl")
        )
        self.import_menu.add_command(
            label="In-house CSV", command=lambda: self.load_file("own_csv")
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
