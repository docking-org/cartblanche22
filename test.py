import requests

smilelist= 'C1CCC(-C2NNCNN2)CC1\nC1CCC(C2CNNC2)C1\nC1=CC=CC=C1C2=CC=CC=C2'
adist = '1'
dist = '0'
response = requests.post('https://cartblanche22.docking.org/smiles.txt', files=(('smiles-in',smilelist), ('adist', adist), ('dist',dist)))
                         
print(response.text)