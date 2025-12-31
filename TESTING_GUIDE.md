# 🧪 Guide de Test - action_create_template_db()

## ✅ Checklist de Test

### Avant de Commencer
- [ ] Odoo 18.0 installé et en cours d'exécution
- [ ] PostgreSQL accessible
- [ ] Module saas_manager installé
- [ ] Droits administrateur
- [ ] Logs Odoo accessibles

---

## 🧪 Test 1: Vérifier les Prérequis

### 1.1 PostgreSQL Accessibility

```bash
# Tester la connexion PostgreSQL
psql -h localhost -U odoo -d postgres -c "SELECT version();"

# Vérifier les droits CREATE DATABASE
psql -h localhost -U odoo -d postgres -c "
SELECT usecreatedb FROM pg_user WHERE usename='odoo';
"
```

**Résultat Attendu:**
```
 usecreatedb 
─────────────
 t
(1 row)
```

### 1.2 Vérifier Odoo Configuration

```bash
# Vérifier la configuration Odoo
grep -E "db_host|db_port|db_user" /opt/GetapERP/GetapERP-V18/odoo.conf

# Vérifier odoo-bin
which odoo-bin
ls -la /opt/GetapERP/GetapERP-V18/odoo/odoo-bin
```

---

## 🧪 Test 2: Test Unitaire Basique

### 2.1 Créer un Template via Console

```bash
cd /opt/GetapERP/GetapERP-V18

# Lancer la console Odoo
./odoo/odoo-bin shell

# Dans la console Python
>>> template = env['saas.template'].create({
...     'name': 'Test Template',
...     'code': 'test_template',
...     'template_db': 'template_test_001',
... })
>>> print(f"Template créé: {template.name} (ID: {template.id})")
>>> print(f"Is Ready: {template.is_template_ready}")
```

**Résultat Attendu:**
```
Template créé: Test Template (ID: 1)
Is Ready: False
```

### 2.2 Vérifier que le Template Existe

```python
>>> template_id = template.id
>>> template = env['saas.template'].browse(template_id)
>>> print(template.template_db)
```

**Résultat Attendu:**
```
template_test_001
```

---

## 🧪 Test 3: Créer la Base de Données Template

### 3.1 Via Console Odoo

```python
>>> # Récupérer le template
>>> template = env['saas.template'].browse(1)
>>> 
>>> # Créer la base de données
>>> try:
...     result = template.action_create_template_db()
...     print("Succès!")
...     print(result)
... except Exception as e:
...     print(f"Erreur: {e}")
```

**Résultat Attendu:**
```
Succès!
{'type': 'ir.actions.client', 'tag': 'display_notification', ...}
```

### 3.2 Vérifier que la Base est Créée

```bash
# Lister les bases de données PostgreSQL
psql -h localhost -U odoo -d postgres -c "
SELECT datname FROM pg_database 
WHERE datname LIKE 'template_%' 
ORDER BY datname;
"
```

**Résultat Attendu:**
```
    datname      
──────────────────
 template_test_001
(1 row)
```

### 3.3 Vérifier que le Template est Marqué Prêt

```python
>>> template.refresh()
>>> print(f"Is Ready: {template.is_template_ready}")
```

**Résultat Attendu:**
```
Is Ready: True
```

---

## 🧪 Test 4: Cloner le Template

### 4.1 Cloner pour une Instance

```python
>>> template = env['saas.template'].browse(1)
>>> 
>>> try:
...     result = template.clone_template_db('saas_client_001_db')
...     print("Clone réussi!")
... except Exception as e:
...     print(f"Erreur de clone: {e}")
```

**Résultat Attendu:**
```
Clone réussi!
```

### 4.2 Vérifier que la Base Clonée Existe

```bash
# Lister les bases clonées
psql -h localhost -U odoo -d postgres -c "
SELECT datname FROM pg_database 
WHERE datname LIKE 'saas_client_%' 
ORDER BY datname;
"
```

**Résultat Attendu:**
```
      datname       
───────────────────
 saas_client_001_db
(1 row)
```

---

## 🧪 Test 5: Test d'Erreurs

### 5.1 Base Déjà Existante

```python
>>> # Essayer de créer une base qui existe déjà
>>> template = env['saas.template'].create({
...     'name': 'Duplicate',
...     'code': 'duplicate',
...     'template_db': 'template_test_001',  # Déjà existant
... })
>>> 
>>> try:
...     template.action_create_template_db()
... except Exception as e:
...     print(f"Erreur Attendue: {e}")
```

**Résultat Attendu:**
```
Erreur Attendue: Template database 'template_test_001' already exists!
```

### 5.2 Clone d'un Template Non Prêt

```python
>>> template = env['saas.template'].create({
...     'name': 'Not Ready',
...     'code': 'not_ready',
...     'template_db': 'template_not_ready',
... })
>>> 
>>> try:
...     template.clone_template_db('client_db')
... except Exception as e:
...     print(f"Erreur Attendue: {e}")
```

**Résultat Attendu:**
```
Erreur Attendue: Template 'Not Ready' is not ready. Please create the template database first.
```

### 5.3 Code Template Invalide

```python
>>> # Code doit être en minuscules
>>> try:
...     template = env['saas.template'].create({
...         'name': 'Invalid',
...         'code': 'InvalidCode',  # Pas en minuscules!
...         'template_db': 'template_invalid',
...     })
... except Exception as e:
...     print(f"Erreur Attendue: {e}")
```

**Résultat Attendu:**
```
Erreur Attendue: Template code must be lowercase.
```

---

## 🧪 Test 6: Test via Interface Web

### 6.1 Créer un Template

1. Allez à **SaaS Manager > Templates**
2. Cliquez sur **Create**
3. Remplissez les champs:
   - **Name**: "E-commerce SaaS"
   - **Code**: "ecommerce"
   - **Template DB**: "template_ecommerce"
4. Cliquez sur **Save**

**Résultat Attendu:**
- Template créé avec succès
- Status: "Not Ready" (badge rouge)

### 6.2 Créer la Base de Données

1. Cliquez sur le bouton **"Create Template DB"**
2. Attendez 5-10 minutes
3. Vous devriez voir une notification "Template Created Successfully"

**Résultat Attendu:**
- Status change to "Ready" (badge vert)
- Base de données PostgreSQL créée
- Modules Odoo installés

### 6.3 Voir les Instances

1. Cliquez sur **"View Instances"** (si des instances existent)

**Résultat Attendu:**
- Liste vide si aucune instance
- Vous devriez voir un nombre > 0 après création d'instances

### 6.4 Accéder à la Base Template

1. Cliquez sur **"Access Template"**
2. Une nouvelle onglet s'ouvre

**Résultat Attendu:**
- Interface Odoo de la base template
- Modules de base installés
- Prêt pour configuration

---

## 📊 Résultats du Test

### Test Summary Table

| # | Test | Résultat | Notes |
|---|------|----------|-------|
| 1.1 | PostgreSQL Accessible | ✅/❌ | |
| 1.2 | Odoo Configuration | ✅/❌ | |
| 2.1 | Create Template | ✅/❌ | |
| 2.2 | Verify Template | ✅/❌ | |
| 3.1 | Create Template DB | ✅/❌ | |
| 3.2 | DB Created in PG | ✅/❌ | |
| 3.3 | Template Marked Ready | ✅/❌ | |
| 4.1 | Clone Template | ✅/❌ | |
| 4.2 | Clone DB Exists | ✅/❌ | |
| 5.1 | Error: DB Exists | ✅/❌ | |
| 5.2 | Error: Not Ready | ✅/❌ | |
| 5.3 | Error: Invalid Code | ✅/❌ | |
| 6.1 | UI: Create | ✅/❌ | |
| 6.2 | UI: Create DB | ✅/❌ | |
| 6.3 | UI: View Instances | ✅/❌ | |
| 6.4 | UI: Access Template | ✅/❌ | |

---

## 🐛 Débogage

### Vérifier les Logs

```bash
# Logs Odoo
tail -f /var/log/odoo/odoo.log

# Filter par saas_template
grep -i saas /var/log/odoo/odoo.log | tail -50
```

### Mode Debug

```python
>>> # Dans la console Odoo
>>> import logging
>>> logging.getLogger('odoo.addons.saas_manager').setLevel(logging.DEBUG)
```

### Vérifier PostgreSQL Logs

```bash
# PostgreSQL logs
tail -f /var/log/postgresql/postgresql.log
```

---

## ✨ Cas de Succès

Si tous les tests passent:
1. ✅ Module prêt pour production
2. ✅ API fonctionnelle
3. ✅ Gestion d'erreurs complète
4. ✅ Performance acceptable
5. ✅ Sécurité validée

---

## 🔴 Cas de Problèmes

### PostgreSQL Connection Failed
```
→ Vérifier odoo.conf: db_host, db_port, db_user, db_password
→ Vérifier que PostgreSQL est en cours d'exécution
→ Vérifier les droits de l'utilisateur odoo
```

### Odoo Binary Not Found
```
→ Vérifier que odoo-bin est accessible
→ Vérifier le chemin complet: /opt/GetapERP/GetapERP-V18/odoo/odoo-bin
→ Vérifier les permissions
```

### Permission Denied
```
→ Vérifier les droits PostgreSQL de l'utilisateur
→ ALTER USER odoo CREATEDB;
```

### Timeout
```
→ Augmenter le timeout (par défaut 300s)
→ Vérifier les ressources serveur (RAM, CPU, disque)
```

---

**Test Créé:** Décembre 2024
**Version Testée:** 18.0.1.0.0
**Environnement:** Production

