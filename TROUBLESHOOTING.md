# 🔧 Solution: Erreur ModuleNotFoundError: No module named 'reportlab'

## 🎯 Le Problème

Quand vous lancez `action_create_template_db()`, l'erreur suivante apparaît:

```
ModuleNotFoundError: No module named 'reportlab'
```

## 🔍 Cause Racine

Le subprocess créé pour lancer `odoo-bin` n'hérite pas du même environnement Python que le processus Odoo courant. Même si `reportlab` est installé dans votre environnement, le subprocess ne peut pas y accéder.

## ✅ Solutions

### Solution 1: Utiliser le même Python Interpreter (Recommandé)

Le code a déjà été amélioré pour utiliser `sys.executable`:

```python
cmd = [
    sys.executable,  # ← Utilise le même Python que le processus courant
    odoo_bin_path,
    '-d', template_db_name,
    ...
]
```

**À faire:**
1. Redémarrez Odoo
2. Réessayez la création du template

### Solution 2: Installer les Dépendances Requises

```bash
# Vérifier si reportlab est installé
pip list | grep reportlab

# Si non installé, installer les dépendances
cd /opt/GetapERP/GetapERP-V18/odoo
pip install -r requirements.txt

# Ou installer reportlab directement
pip install reportlab
```

### Solution 3: Vérifier l'Environnement Virtual

Si vous utilisez un virtual environment:

```bash
# Vérifier quel Python est actif
which python
which python3

# Vérifier que le virtual environment est activé
echo $VIRTUAL_ENV

# Si non activé, l'activer
source /path/to/venv/bin/activate

# Réinstaller les dépendances
pip install -r /opt/GetapERP/GetapERP-V18/odoo/requirements.txt
```

### Solution 4: Vérifier le PYTHONPATH

Ajouter le chemin d'Odoo au PYTHONPATH:

```bash
# Vérifier le PYTHONPATH courant
echo $PYTHONPATH

# Ajouter le chemin d'Odoo (temporaire)
export PYTHONPATH="/opt/GetapERP/GetapERP-V18/odoo:$PYTHONPATH"

# Pour le rendre permanent, ajouter à ~/.bashrc ou ~/.zshrc
echo 'export PYTHONPATH="/opt/GetapERP/GetapERP-V18/odoo:$PYTHONPATH"' >> ~/.bashrc
source ~/.bashrc
```

### Solution 5: Utiliser un Wrapper Shell

Créer un script `init_template.sh`:

```bash
#!/bin/bash
cd /opt/GetapERP/GetapERP-V18/odoo
export PYTHONPATH="/opt/GetapERP/GetapERP-V18/odoo:$PYTHONPATH"

python odoo-bin \
    -d "$1" \
    -i base,web,mail,portal \
    --without-demo=all \
    --stop-after-init \
    --db_host localhost \
    --db_user getappro \
    --db_password 'Hr@f066133663'
```

Puis modifier le code pour utiliser ce script:

```python
cmd = [
    '/bin/bash',
    '/opt/GetapERP/GetapERP-V18/init_template.sh',
    template_db_name,
]
```

---

## 🧪 Tester les Dépendances

Pour vérifier que tous les modules sont disponibles:

```python
# Dans la console Python
import sys
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")

# Tester chaque module critique
try:
    import reportlab
    print("✓ reportlab OK")
except ImportError as e:
    print(f"✗ reportlab MISSING: {e}")

try:
    import PIL
    print("✓ PIL OK")
except ImportError as e:
    print(f"✗ PIL MISSING: {e}")

try:
    import lxml
    print("✓ lxml OK")
except ImportError as e:
    print(f"✗ lxml MISSING: {e}")

try:
    import psycopg2
    print("✓ psycopg2 OK")
except ImportError as e:
    print(f"✗ psycopg2 MISSING: {e}")
```

---

## 📋 Checklist de Diagnostic

- [ ] Vérifiez le Python utilisé: `which python`
- [ ] Vérifiez que reportlab est installé: `pip show reportlab`
- [ ] Vérifiez le PYTHONPATH: `echo $PYTHONPATH`
- [ ] Vérifiez le virtual environment: `echo $VIRTUAL_ENV`
- [ ] Vérifiez les logs Odoo: `tail -f /var/log/odoo/odoo.log`
- [ ] Vérifiez que odoo-bin est exécutable: `ls -la /opt/GetapERP/GetapERP-V18/odoo/odoo-bin`

---

## 🚀 Après Correction

Une fois le problème résolu, réessayez:

1. **Via la Console Odoo:**
```bash
cd /opt/GetapERP/GetapERP-V18
./odoo/odoo-bin shell

# Dans la console
template = env['saas.template'].browse(1)
template.action_create_template_db()
```

2. **Via l'Interface Web:**
- Allez à SaaS Manager > Templates
- Sélectionnez un template
- Cliquez sur "Create Template DB"

---

## 📚 Référence

- [Odoo Requirements.txt](https://github.com/odoo/odoo/blob/18.0/requirements.txt)
- [Reportlab Documentation](https://www.reportlab.com/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

---

**Date:** Décembre 2024
**Version Odoo:** 18.0
**Problème:** ModuleNotFoundError: No module named 'reportlab'

