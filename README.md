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
- ✅ **NOUVEAU** : Traitement intelligent avec IA pour l'analyse post-OCR
- ✅ **NOUVEAU** : Identification intelligente des types de réduction
- ✅ **NOUVEAU** : Extraction robuste des prix même avec du bruit OCR

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

# Installation de base (parsing traditionnel uniquement)
# Aucune dépendance externe requise (Python 3.6+)

# Installation avec support IA (recommandé pour OCR)
pip install -r requirements.txt
```

### Configuration de l'IA (optionnel)

Pour bénéficier du traitement intelligent post-OCR :

1. Obtenir une clé API OpenAI sur https://platform.openai.com/
2. Définir la clé API :

```bash
# Option 1: Fichier .env (recommandé)
cp .env.example .env
# Éditer .env et ajouter votre clé API

# Option 2: Variable d'environnement
export OPENAI_API_KEY='votre-clé-api'

# Option 3: Dans le code Python
from receipt_parser import ReceiptParser
parser = ReceiptParser(use_ai=True, ai_api_key='votre-clé-api')
```

**Note** : Sans clé API, le système fonctionne normalement avec le parsing traditionnel.

## Utilisation

### En ligne de commande

```bash
# Depuis un fichier
python receipt_csv.py examples/receipt1.txt

# Depuis stdin
cat examples/receipt1.txt | python receipt_csv.py

# Sauvegarder dans un fichier
python receipt_csv.py examples/receipt1.txt -o output.csv

# Afficher l'aide
python receipt_csv.py --help
```

### En tant que module Python

```python
from receipt_parser import ReceiptParser
from csv_generator import CSVGenerator

# Charger le reçu
with open('receipt.txt', 'r') as f:
    receipt_text = f.read()

# Parser et générer le CSV (avec IA activée par défaut si clé API disponible)
parser = ReceiptParser()
generator = CSVGenerator()

receipt = parser.parse(receipt_text)
csv_output = generator.generate(receipt)

# Sauvegarder ou afficher
print(csv_output)
```

#### Utilisation avancée avec IA

```python
from receipt_parser import ReceiptParser
from csv_generator import CSVGenerator

# Parser avec IA explicitement activée
parser = ReceiptParser(use_ai=True, ai_api_key='votre-clé')

# Pour du texte OCR bruité
receipt_text = """
2O24-O3-15  # O au lieu de 0 (erreur OCR)
App St0re   # 0 au lieu de o
Applicati0n A    l x 9.99    9.99  # l au lieu de 1
"""

receipt = parser.parse(receipt_text)
# L'IA aidera à corriger les erreurs OCR et extraire les bonnes données
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

## Limitations et bonnes pratiques

### Limitations connues

1. **Ordre des éléments** : Les réductions sont appliquées au produit précédent. Pour de meilleurs résultats, placez les réductions juste après le produit concerné.
2. **Format texte uniquement** : Actuellement, seul le format texte est supporté (pas de PDF ni d'images directement).
3. **Parsing simple** : Le parser traditionnel utilise des expressions régulières simples. Pour les formats complexes ou OCR bruité, utilisez le mode IA.

### Traitement intelligent avec IA

L'IA améliore considérablement le traitement des reçus issus d'OCR :

**Avantages :**
- ✅ Correction automatique des erreurs OCR courantes (0/O, 1/l, 5/S, etc.)
- ✅ Identification intelligente des types de réduction (Coupon, Promo, Fidélité, etc.)
- ✅ Extraction robuste même avec mise en page complexe
- ✅ Reconnaissance contextuelle des produits et prix
- ✅ Meilleure gestion des formats de reçus variés

**Comment ça marche :**
1. Si une clé API OpenAI est configurée, l'IA est utilisée en premier
2. Si l'IA échoue ou n'est pas disponible, le système bascule automatiquement sur le parsing traditionnel
3. Aucune interruption de service : le système fonctionne toujours

**Cas d'usage :**
- Reçus scannés avec du bruit ou des artefacts
- Texte OCR avec des erreurs de reconnaissance
- Formats de reçus non standard
- Identification précise des types de promotions

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
# Exécuter tous les tests
python -m unittest discover tests -v

# Exécuter les tests de parsing traditionnel
python -m unittest tests/test_receipt_csv.py -v

# Exécuter les tests d'IA
python -m unittest tests/test_ai_processor.py -v
```

## Exemples de reçus

Le répertoire `examples/` contient plusieurs exemples de reçus :
- `receipt1.txt` : Reçu simple avec un moyen de paiement
- `receipt2.txt` : Reçu avec plusieurs moyens de paiement
- `receipt3.txt` : Reçu avec réductions multiples
- `receipt_complex.txt` : Reçu complexe avec plusieurs réductions et paiements

## Développement futur

- [x] Support pour l'IA et traitement post-OCR intelligent
- [x] Identification intelligente des types de réduction
- [ ] Support pour les fichiers PDF
- [ ] Support pour l'OCR d'images (Tesseract)
- [ ] Interface web
- [ ] API REST
- [ ] Support pour plus de formats de reçus
- [ ] Support pour plus de modèles d'IA (modèles locaux, Anthropic, etc.)

## Licence

MIT
