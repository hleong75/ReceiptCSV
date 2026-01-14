# ReceiptCSV

Un outil d'extraction et de structuration de données à partir de reçus d'application.

## Description

ReceiptCSV extrait les données structurées des reçus (texte, PDF ou OCR) et génère un fichier CSV avec une ligne par produit acheté.

## Fonctionnalités

- ✅ Extraction des produits achetés
- ✅ Extraction des moyens de paiement utilisés
- ✅ Gestion des réductions appliquées
- ✅ Répartition proportionnelle pour plusieurs moyens de paiement
- ✅ Répartition proportionnelle des réductions globales
- ✅ Support des fichiers PDF
- ✅ Format CSV avec séparateur point-virgule (;)
- ✅ Format de date YYYY-MM-DD
- ✅ Montants numériques avec point (.) comme séparateur décimal

## Colonnes du CSV

1. Date d'achat
2. Nom du produit
3. Prix
4. Remise
5. Prix Total
6. Moyen de paiement
7. Devise

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/hleong75/ReceiptCSV.git
cd ReceiptCSV

# Pour le support PDF, installer les dépendances
pip install -r requirements.txt
```

## Utilisation

### En ligne de commande

```bash
# Depuis un fichier texte
python receipt_csv.py examples/receipt1.txt

# Depuis un fichier PDF
python receipt_csv.py examples/receipt1.pdf

# Depuis stdin
cat examples/receipt1.txt | python receipt_csv.py

# Sauvegarder dans un fichier
python receipt_csv.py examples/receipt1.txt -o output.csv
python receipt_csv.py examples/receipt1.pdf -o output.csv

# Afficher l'aide
python receipt_csv.py --help
```

### En tant que module Python

```python
from receipt_parser import ReceiptParser
from csv_generator import CSVGenerator

# Charger le reçu texte
with open('receipt.txt', 'r') as f:
    receipt_text = f.read()

# Parser et générer le CSV
parser = ReceiptParser()
generator = CSVGenerator()

receipt = parser.parse(receipt_text)
csv_output = generator.generate(receipt)

# Sauvegarder ou afficher
print(csv_output)
```

### Utilisation avec PDF

```python
from pathlib import Path
from pdf_extractor import PDFExtractor
from receipt_parser import ReceiptParser
from csv_generator import CSVGenerator

# Extraire le texte depuis un PDF
pdf_path = Path('receipt.pdf')
extractor = PDFExtractor()
receipt_text = extractor.extract_text(pdf_path)

# Parser et générer le CSV
parser = ReceiptParser()
generator = CSVGenerator()

receipt = parser.parse(receipt_text)
csv_output = generator.generate(receipt)

print(csv_output)
```

### Format des reçus

Le format attendu pour les reçus texte est flexible mais doit contenir :

```
Date (YYYY-MM-DD ou DD/MM/YYYY)
Nom du marchand
Produit 1    Quantité x Prix unitaire    Sous-total
Produit 2    Prix
Réduction    Montant
Paiement: Méthode    Montant
```

### Exemple

**Fichier d'entrée (receipt1.txt):**
```
2024-03-15
App Store
Application A    1 x 9.99    9.99
Application B    2.99
Coupon App A    -2.00
Paiement: Apple Pay    10.98
```

**Sortie CSV:**
```csv
Date d'achat;Nom du produit;Prix;Remise;Prix Total;Moyen de paiement;Devise
2024-03-15;Application A;9.99;2.00;7.99;Apple Pay;EUR
2024-03-15;Application B;2.99;;2.99;Apple Pay;EUR
```

## Règles de traitement

- **Une ligne = un produit** : Chaque produit génère au moins une ligne dans le CSV
- **Plusieurs moyens de paiement** : Si plusieurs moyens de paiement sont utilisés, le montant est réparti proportionnellement entre les produits
- **Réductions globales** : Les réductions non liées à un produit spécifique sont réparties proportionnellement
- **Champs vides** : Les champs sans valeur sont laissés vides dans le CSV

## Limitations et bonnes pratiques

### Limitations connues

1. **Ordre des éléments** : Les réductions sont appliquées au produit précédent. Pour de meilleurs résultats, placez les réductions juste après le produit concerné.
2. **Parsing simple** : Le parser utilise des expressions régulières simples. Les formats de reçus très complexes peuvent nécessiter une adaptation.
3. **Qualité PDF** : Pour les fichiers PDF, la qualité de l'extraction dépend de la qualité du document. Les PDF numérisés (images) ne sont pas supportés sans OCR.

### Bonnes pratiques

1. **Structure du reçu** : Pour de meilleurs résultats, formatez vos reçus comme suit :
   ```
   Date (YYYY-MM-DD ou DD/MM/YYYY)
   Nom du marchand
   Produit 1    Quantité x Prix    Total
   Réduction produit 1    Montant
   Produit 2    Prix
   Réduction globale    Montant
   Paiement: Méthode 1    Montant
   Paiement: Méthode 2    Montant
   ```

2. **Réductions** : Placez les réductions immédiatement après le produit auquel elles s'appliquent.

3. **Montants** : Utilisez toujours le format avec 2 décimales (ex: 9.99 ou 9,99).

4. **Moyens de paiement** : Incluez le mot "Paiement" ou "Payment" pour une meilleure détection.

## Tests

```bash
# Exécuter les tests
python -m unittest tests/test_receipt_csv.py

# Exécuter les tests avec verbosité
python -m unittest tests/test_receipt_csv.py -v
```

## Exemples de reçus

Le répertoire `examples/` contient plusieurs exemples de reçus :
- `receipt1.txt` / `receipt1.pdf` : Reçu simple avec un moyen de paiement
- `receipt2.txt` / `receipt2.pdf` : Reçu avec plusieurs moyens de paiement
- `receipt3.txt` / `receipt3.pdf` : Reçu avec réductions multiples

## Développement futur

- [x] Support pour les fichiers PDF
- [ ] Support pour l'OCR d'images
- [ ] Interface web
- [ ] API REST
- [ ] Support pour plus de formats de reçus

## Licence

MIT
