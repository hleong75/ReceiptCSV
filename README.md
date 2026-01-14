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
- ✅ Format CSV avec séparateur point-virgule (;)
- ✅ Format de date YYYY-MM-DD
- ✅ Montants numériques avec point (.) comme séparateur décimal

## Colonnes du CSV

1. Date d'achat
2. Nom de l'application / marchand
3. Nom du produit
4. Quantité
5. Prix unitaire
6. Sous-total produit
7. Type de réduction
8. Montant de la réduction
9. Moyen de paiement
10. Devise

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/hleong75/ReceiptCSV.git
cd ReceiptCSV

# Aucune dépendance externe requise (Python 3.6+)
```

## Utilisation

### En ligne de commande

```bash
# Depuis un fichier
python receipt_csv.py examples/receipt1.txt

# Depuis stdin
cat examples/receipt1.txt | python receipt_csv.py

# Sauvegarder dans un fichier
python receipt_csv.py examples/receipt1.txt -o output.csv
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
Date d'achat;Nom de l'application / marchand;Nom du produit;Quantité;Prix unitaire;Sous-total produit;Type de réduction;Montant de la réduction;Moyen de paiement;Devise
2024-03-15;App Store;Application A;1;9.99;9.99;Coupon;2.00;Apple Pay;EUR
2024-03-15;App Store;Application B;1;2.99;2.99;;;Apple Pay;EUR
```

## Règles de traitement

- **Une ligne = un produit** : Chaque produit génère au moins une ligne dans le CSV
- **Plusieurs moyens de paiement** : Si plusieurs moyens de paiement sont utilisés, le montant est réparti proportionnellement entre les produits
- **Réductions globales** : Les réductions non liées à un produit spécifique sont réparties proportionnellement
- **Champs vides** : Les champs sans valeur sont laissés vides dans le CSV

## Tests

```bash
# Exécuter les tests
python -m unittest tests/test_receipt_csv.py

# Exécuter les tests avec verbosité
python -m unittest tests/test_receipt_csv.py -v
```

## Exemples de reçus

Le répertoire `examples/` contient plusieurs exemples de reçus :
- `receipt1.txt` : Reçu simple avec un moyen de paiement
- `receipt2.txt` : Reçu avec plusieurs moyens de paiement
- `receipt3.txt` : Reçu avec réductions multiples

## Développement futur

- [ ] Support pour les fichiers PDF
- [ ] Support pour l'OCR d'images
- [ ] Interface web
- [ ] API REST
- [ ] Support pour plus de formats de reçus

## Licence

MIT
