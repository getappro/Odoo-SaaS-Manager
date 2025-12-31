# 🔧 CORRECTION: Erreur ModuleNotFoundError reportlab

## 📌 Le Problème Exact

Vous avez cette erreur:
```
ModuleNotFoundError: No module named 'reportlab'
```

**Cause:** Le subprocess qui lance `odoo-bin` n'hérite pas du même environnement Python que le processus Odoo courant.

---

## ✅ Solution Rapide (3 étapes)

### 1️⃣ Vérifier que reportlab est installé

```bash
# Vérifier l'installation
pip show reportlab

# Si non installé, installer les dépendances
cd /opt/GetapERP/GetapERP-V18/odoo
pip install -r requirements.txt
```

### 2️⃣ Vérifier le Python utilisé

```bash
# Vérifier le Python courant
python --version
which python

# Important: Doit être le même que celui d'Odoo!
```

### 3️⃣ Redémarrer Odoo et Réessayer

```bash
# Arrêter Odoo
pkill -f "odoo-bin"

# Redémarrer
cd /opt/GetapERP/GetapERP-V18
./odoo/odoo-bin -c odoo.conf &
```

---

## 🚀 Solution Alternative: Utiliser le Script Helper

Un script a été créé pour initialiser les templates directement:

```bash
# Initialiser un template
cd /opt/GetapERP/GetapERP-V18/extra-addons/GetapPRO/odoo-saas-manager
./init_saas_template.sh template_restaurant

# Avec modules spécifiques
./init_saas_template.sh template_ecommerce 'base,web,mail,portal,sale,stock,website'
```

Le script:
- ✅ Configure automatiquement l'environnement
- ✅ Vérifie PostgreSQL
- ✅ Initialise la base avec les bons modules
- ✅ Affiche des logs clairs

---

## 🔍 Diagnostic Complet

Si le problème persiste, lancez ce diagnostic:

```bash
#!/bin/bash
echo "=== Python Environment ==="
which python
python --version
python -c "import sys; print(f'Executable: {sys.executable}')"

echo ""
echo "=== Vérifier reportlab ==="
python -c "import reportlab; print(f'✓ reportlab OK: {reportlab.__version__}')" || echo "✗ reportlab NOT FOUND"

echo ""
echo "=== Vérifier lxml ==="
python -c "import lxml; print('✓ lxml OK')" || echo "✗ lxml NOT FOUND"

echo ""
echo "=== Vérifier PIL ==="
python -c "import PIL; print('✓ PIL OK')" || echo "✗ PIL NOT FOUND"

echo ""
echo "=== Vérifier psycopg2 ==="
python -c "import psycopg2; print('✓ psycopg2 OK')" || echo "✗ psycopg2 NOT FOUND"

echo ""
echo "=== PYTHONPATH ==="
echo $PYTHONPATH

echo ""
echo "=== Odoo Binary ==="
ls -la /opt/GetapERP/GetapERP-V18/odoo/odoo-bin
```

---

## 🛠️ Solutions Avancées

### Si vous utilisez un Virtual Environment

```bash
# Vérifier si un venv est actif
echo $VIRTUAL_ENV

# S'il n'y a rien, l'activer
# Trouvez d'abord où il est
find /opt -name "bin/activate" -type f 2>/dev/null

# Puis l'activer (exemple)
source /opt/GetapERP/GetapERP-V18/.venv/bin/activate

# Réinstaller les dépendances
pip install -r /opt/GetapERP/GetapERP-V18/odoo/requirements.txt
```

### Si vous avez plusieurs Versions de Python

```bash
# Voir toutes les versions disponibles
ls /usr/bin/python*

# Vérifier laquelle est utilisée par Odoo
head -1 /opt/GetapERP/GetapERP-V18/odoo/odoo-bin

# Installer reportlab avec la bonne version
/usr/bin/python3.10 -m pip install reportlab
```

---

## 📝 Vérification Post-Correction

Après avoir corrigé le problème, testez avec ce script:

```bash
#!/bin/bash

echo "Test 1: Importer tous les modules"
python -c "
import sys
modules = ['odoo', 'reportlab', 'lxml', 'PIL', 'psycopg2']
for m in modules:
    try:
        __import__(m)
        print(f'✓ {m}')
    except ImportError as e:
        print(f'✗ {m}: {e}')
"

echo ""
echo "Test 2: Lancer odoo-bin en test"
cd /opt/GetapERP/GetapERP-V18/odoo
python odoo-bin --help | head -20

echo ""
echo "Test 3: Vérifier la connexion PostgreSQL"
psql -h localhost -U getappro -d postgres -c "SELECT 1"

echo ""
echo "Si tous les tests passent, vous pouvez créer des templates!"
```

---

## 🎯 Procédure Complète de Correction

1. **Arrêter Odoo**
   ```bash
   pkill -f "odoo-bin"
   ```

2. **Installer les dépendances manquantes**
   ```bash
   cd /opt/GetapERP/GetapERP-V18/odoo
   pip install -r requirements.txt
   ```

3. **Vérifier l'installation**
   ```bash
   python -c "import reportlab; print('OK')"
   ```

4. **Redémarrer Odoo**
   ```bash
   cd /opt/GetapERP/GetapERP-V18
   ./odoo/odoo-bin -c odoo.conf &
   ```

5. **Réessayer de créer un template**
   - Via l'interface: SaaS Manager > Templates > Create > "Create Template DB"
   - Ou via le script: `./init_saas_template.sh template_name`

---

## 💡 Conseils Supplémentaires

### Pour les Producteurs
- Utilisez le script `init_saas_template.sh` au lieu de la méthode via interface
- Plus rapide et plus fiable
- Logs détaillés pour le débogage

### Pour le Développement
- Exécutez dans la console Odoo:
  ```python
  from odoo.tools import config
  print(f"Python: {config.get('python_interpreter', 'default')}")
  ```

### Pour les Devops
- Ajouter au playbook Ansible:
  ```yaml
  - name: Install Odoo dependencies
    pip:
      requirements: /opt/GetapERP/GetapERP-V18/odoo/requirements.txt
      virtualenv: /opt/GetapERP/GetapERP-V18/.venv
  ```

---

## 📞 Si le Problème Persiste

Collectez ces informations:
1. Output de `python -c "import reportlab; print(reportlab.__file__)"`
2. Output de `echo $PYTHONPATH`
3. Output de `echo $VIRTUAL_ENV`
4. Contenu du fichier `/tmp/odoo_init_*.log` (s'il existe)
5. Output complet de l'erreur

---

**Date:** Décembre 2024
**Status:** ✅ RÉSOLU
**Prochaine étape:** Créer des templates et des instances!

