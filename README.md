# PAINSApp
Here I provide an application which enables researchers to perform PAINS analysis for prepared compounds collections. PAINS (Pan Assay Interference Compounds) are compounds with certain substructural motifs, which tend to display false positive outcoms in High-throughput screening (HTS) [1,2]. Therefore, it is advantageous to filter molecular libraries for the presence of such compounds.

PAINSApp is simple application written in Python. It's raw frontend bases on tkinter library, which allows python-programmers to build simple GUI. Program accept two kinds of files as an input:
  a) ChEMBL file - file which is an output of preprocessed ChEMBL bioactivity reports with the use of the ChEMBL_parsing_script         (https://github.com/Adam-maz/ChEMBL_parsing_script).
  b) In-house CSV file - simple CSV file that contains only SMILES (as "Smiles") and ID (as "Id")
I've attached examples for input files within this repository.

Application requires installed pandas, rdkit and tqdm (and tkinter for Linux users) in virtual environment.



**References**:
1. Seven Year Itch: Pan-Assay Interference Compounds (PAINS) in 2017 - Utility and Limitations
2. Pan Assay Interference Compounds (PAINS) and Other Promiscuous Compounds in Antifungal Research
