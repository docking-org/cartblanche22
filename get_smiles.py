

import requests
import time 

def call_api(smile, dist, adist, db, matched_smiles):
    credentials = ('gpcr', 'xtal')
    import urllib.parse
    smile_text = urllib.parse.quote(smile)
    url = "https://swp.docking.org/search/view?smi={smile}&db={db}&fmt=tsv&dist={adist}&sdist={dist}&length=25".format(smile=smile_text, db=db, adist=adist, dist=dist)
    r = requests.get(url, auth=credentials)
    print(matched_smiles)
    print(r.text)
    if not r.text.split('\n')[1]:
        url = "https://sw.docking.org/search/view?smi={smile}&db=all-zinc.smi.anon&fmt=tsv&dist={adist}&sdist={dist}&length=25".format(smile=smile_text, db=db, adist=adist, dist=dist)
        r = requests.get(url, auth=credentials)
        print(r.text)
       
    with open('results.txt', 'a') as f:
        lines = r.text.split('\n')
        lines = lines[1:]
        for line in lines:
            if line:
                f.write(line.split('\t')[0].split(' ')[1])
                f.write('\t')
                f.write(matched_smiles)
                f.write('\n')

res = []
with open('smiles.txt', 'r') as f:
    smiles = f.readlines()
    dist = 0
    adist = 0
    for smile in smiles:
        res.append(call_api(smile, dist, adist, 'zinc22-All-070123.smi.anon', smile))
        time.sleep(6)
    
results = {}

for r in res:
    matched_smiles = r[1]
    r = r[0]
    text = r.split('\n')
    text = text[1:]
    for line in text:
        if line:
            line = line.split('\t')
            results[line[0].split(' ')[1]] = {
                'smiles': line[0].split(' ')[0],
                'matched_smiles': matched_smiles,
            }
