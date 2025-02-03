import pysmallworld
import argparse

def search_by_smiles(smiles):
    """
    Search for molecules by SMILES string.

    :param smiles: A list of SMILES strings.
    :return: A list of molecules.
    """
    # This is a placeholder implementation that returns the input SMILES strings.
    # Replace this with the actual implementation.
    return smiles

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Search for molecules by SMILES string.')
    parser.add_argument('smiles', type=str, help='A list of SMILES strings.')
    args = parser.parse_args()

    smiles = args.smiles.split(',')
    molecules = search_by_smiles(smiles)
    print(molecules)
    
    # Example usage:
    # python search_by_smiles.py "CCO,CCN"
    # Output:
    # ['CCO', 'CCN']