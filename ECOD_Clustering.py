from rdkit import Chem
from rdkit.Chem import AllChem
from Bio.PDB import PDBParser, Structure, NeighborSearch
from collections import Counter
import tempfile
import os
import pandas as pd
pd.set_option('display.max_columns', None)

dataframe_filepath = '/mnt/evafs/groups/sfglab/mwisniewski/PhD/data/dataframes/LP_PDBBind.csv'
ECOD_dataframe_filepath = '/mnt/evafs/groups/sfglab/mwisniewski/ingenix/data/ECOD/ecod.develop291.domains.txt'
datadir = '/mnt/evafs/groups/sfglab/mwisniewski/PhD/data/lp'

dataframe = pd.read_csv(dataframe_filepath)
dataframe['closest_chain_to_ligand'] = ''
dataframe['closest_chain_residue_to_ligand'] = ''
dataframe['ECOD'] = ''

ECOD_dataframe = pd.read_csv(ECOD_dataframe_filepath,sep='\t')

def parse_range(s):
    start, end = map(int, s.split('-'))
    return range(start, end + 1)
def preprocess_ECOD_df(ECOD_dataframe):
    ECOD_dataframe['pdb_range']
    ECOD_dataframe['Cluster'] = ECOD_dataframe[['arch_name','x_name','h_name','t_name','f_name']].apply(lambda row: ' - '.join(row), axis=1)
    ECOD_dataframe = ECOD_dataframe[~ECOD_dataframe['ecod_domain_id'].str.contains('e5j3dA3')]
    ECOD_dataframe['pdb_range'] = ECOD_dataframe['pdb_range'].apply(lambda x: x.split(','))
    ECOD_dataframe =ECOD_dataframe.explode(column=['pdb_range'])
    ECOD_dataframe = ECOD_dataframe.dropna(subset=['pdb_range'])
    ECOD_dataframe['pdb_range'] = ECOD_dataframe['pdb_range'].apply(lambda x: x.split(':')[-1])
    ECOD_dataframe = ECOD_dataframe.drop_duplicates(subset=['pdb_range','chain','pdb'])
    ECOD_dataframe['pdb_range'] = ECOD_dataframe['pdb_range'].apply(lambda x: ''.join(c for c in x if c.isdigit() or c in ['-']))
    ECOD_dataframe = ECOD_dataframe[ECOD_dataframe['pdb_range'].str.contains('-')]
    ECOD_dataframe['pdb_range'] = ECOD_dataframe['pdb_range'].apply(lambda x: parse_range(x))
    print(ECOD_dataframe.head())
    print(len(ECOD_dataframe))

    return ECOD_dataframe

def mol2_to_biopython_structure(mol2_file):
    # Wczytanie ligandu z pliku Mol2
    mol = Chem.MolFromMol2File(mol2_file)
    # Tworzenie pliku tymczasowego dla PDB
    temp_pdb_file = tempfile.NamedTemporaryFile(suffix='.pdb',delete=False).name
    # Zapisanie ligandu do pliku PDB
    Chem.MolToPDBFile(mol,temp_pdb_file)
    # Tworzenie parsera PDB
    parser = PDBParser()
    # Parsowanie danych z pliku PDB
    pdb_struct = parser.get_structure('ligand',temp_pdb_file)
    # Usuwanie tymczasowego pliku
    os.unlink(temp_pdb_file)
    return pdb_struct
def find_closest_chain_to_ligand(protein_pdb_file,ligand_mol2_file):
    # Inicjalizacja parsera PDB
    parser = PDBParser()
    # Wczytanie struktur białka i ligandu
    protein_structure = parser.get_structure('protein',protein_pdb_file)
    ligand_structure = mol2_to_biopython_structure(ligand_mol2_file)
    # Pobranie łańcuchów białka
    protein_chains = list(protein_structure.get_chains())
    # Inicjalizacja wyszukiwania sąsiadów
    ns = NeighborSearch(list(protein_structure.get_atoms()))
    ligand_closest_chains = []
    # Iteracja po atomach ligandu
    for ligand_atom in ligand_structure.get_atoms():
        # Znalezienie najbliższego atomu białka dla danego atomu liganda
        closest_atoms = ns.search(ligand_atom.get_coord(),4.8)
        atom_closest_chains = [(str(closest_atom.get_parent().get_parent())[-2],closest_atom.get_parent().get_id()[1])
                               for closest_atom in closest_atoms
                               if closest_atom.get_parent().get_full_id()[0] == 'protein']
        count_atom_closest_chains = Counter(atom_closest_chains)
        try:
            atom_closest_chain = count_atom_closest_chains.most_common(1)[0][0]
        except:
            atom_closest_chain = None
        ligand_closest_chains.append(atom_closest_chain)

    count_ligand_closest_chains = Counter(ligand_closest_chains)
    ligand_closest_chain_and_residue = count_ligand_closest_chains.most_common(1)[0][0]

    return ligand_closest_chain_and_residue
def find_ECOD(molecule,closest_chain_to_ligand,ECOD_dataframe):
    option = ECOD_dataframe[ECOD_dataframe['pdbid']]
    option = ECOD_dataframe[ECOD_dataframe['chain']]
    return None

print('ECOD Dataframe Preprocessing')
ECOD_dataframe = preprocess_ECOD_df(ECOD_dataframe)


#for index,row in dataframe.iterrows():

#    molecule = row['pdbid']
#    print(molecule)
#    protein_pdb_file = os.path.join(datadir,'protein','pdb',molecule+'_protein.pdb')
#    ligand_mol2_file = os.path.join(datadir,'ligand','mol2',molecule+'_ligand.mol2')
#    ligand_closest_chain, ligand_closest_residue_id = find_closest_chain_to_ligand(protein_pdb_file,ligand_mol2_file)
#    dataframe.at[index,'closest_chain_to_ligand'] = ligand_closest_chain
#    dataframe.at[index,'closest_chain_residue_to_ligand'] = ligand_closest_residue_id

