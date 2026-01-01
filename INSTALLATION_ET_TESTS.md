# Installation et Test - Modèle SaaS Server

## 📦 Installation du module

### Prérequis
- Odoo 18.0 installé
- Module `saas_manager` existant
- Python 3.11+
- Package `requests` installé

### Étape 1 : Vérifier que requests est installé
```bash
pip install requests
```

### Étape 2 : Mettre à jour le module
```bash
cd /opt/GetapERP/GetapERP-V18
python -m odoo.bin -u saas_manager -d your_database_name -c odoo.conf
```

### Étape 3 : Vérifier dans l'interface Odoo
1. Aller à **Apps > SaaS Manager**
2. Vérifier que le module est installé (version 18.0.1.0.0)
3. Aller à **SaaS Manager > Configuration > Servers**
4. Vérifier que vous pouvez créer un serveur

## 🧪 Tests manuels

### Test 1 : Créer un serveur
1. Allez à **SaaS Manager > Configuration > Servers**
2. Cliquez sur **Create**
3. Remplissez les informations :
   - **Name** : "Test Server"
   - **Code** : "test-server" (en minuscules)
   - **Server URL** : "http://localhost:8069"
   - **Server IP** : "127.0.0.1"
   - **DB Host** : "localhost"
   - **DB User** : "odoo"
   - **Master Password** : "admin"
   - **Max Instances** : 100
   - **CPU Cores** : 4
   - **Memory (GB)** : 16
   - **Disk (GB)** : 500
4. Cliquez sur **Save**

✅ Le serveur doit être créé et affichert avec état "Draft"

### Test 2 : Tester la connexion
1. Ouvrez le serveur créé
2. Cliquez sur **Test Connection**
3. Vérifiez que le message indique "Connection successful"

✅ Une notification doit confirmer la connexion

### Test 3 : Activer le serveur
1. Cliquez sur le bouton **Activate**
2. Le serveur doit passer à l'état "Active"
3. `is_online` doit être True
4. `health_status` doit être "healthy"

✅ Le serveur doit être en ligne

### Test 4 : Créer une template sur ce serveur
1. Aller à **SaaS Manager > Configuration > Templates**
2. Créer une nouvelle template
3. Sélectionner le serveur activé dans le champ "Server"
4. Remplir les autres champs
5. Cliquer sur **Create Database**

✅ La base de données template doit être créée

### Test 5 : Vérifier les calculs
1. Aller à **SaaS Manager > Operations > Instances**
2. Créer une instance liée au serveur
3. Retourner au serveur
4. Vérifier que :
   - `instance_count` s'est incrémenté
   - `available_capacity` a diminué

✅ Les calculs doivent être corrects

### Test 6 : Tester les validations
1. Essayer de créer un serveur avec un code en majuscules
   ❌ Doit afficher une erreur

2. Essayer de créer un serveur avec une URL invalide
   ❌ Doit afficher une erreur

3. Essayer de créer un serveur avec max_instances = 0
   ❌ Doit afficher une erreur

✅ Les validations doivent fonctionner

### Test 7 : Tester la protection contre suppression
1. Créer une instance sur le serveur
2. Essayer de supprimer le serveur
   ❌ Doit afficher une erreur

3. Essayer de désactiver le serveur
   ❌ Doit afficher une erreur

✅ Les protections doivent fonctionner

## 🧬 Tests unitaires

### Exécuter tous les tests
```bash
python -m odoo.bin -u saas_manager -d your_database --test-enable
```

### Exécuter seulement les tests saas_server
```bash
python -m pytest \
  /opt/GetapERP/GetapERP-V18/extra-addons/GetapPRO/odoo-saas-manager/saas_manager/tests/test_saas_server.py \
  -v
```

### Résultats attendus
```
test_server_creation ...................... PASSED
test_code_unique ........................... PASSED
test_code_lowercase ........................ PASSED
test_server_url_validation ................. PASSED
test_max_instances_validation .............. PASSED
test_instance_count_compute ................ PASSED
test_available_capacity_compute ............ PASSED
test_is_online_compute ..................... PASSED
test_delete_server_with_instances_fails .... PASSED
test_deactivate_server_with_instances_fails  PASSED
test_get_available_server .................. PASSED
test_get_available_server_no_capacity ...... PASSED

========================= 12 passed ========================
```

## 🔍 Vérifications du modèle

### Vérifier le modèle en Python
```python
# Dans la console Python d'Odoo
from odoo import api, SUPERUSER_ID

env = api.Environment(cr, SUPERUSER_ID, {})

# Voir tous les serveurs
servers = env['saas.server'].search([])
for server in servers:
    print(f"{server.name} ({server.code}): {server.state}")

# Créer un serveur
server = env['saas.server'].create({
    'name': 'Test via Python',
    'code': 'test-python',
    'server_url': 'http://localhost:8069',
})

# Activer
server.action_activate()

# Vérifier la capacité
print(f"Capacité disponible : {server.available_capacity}%")
```

## 📊 Requêtes SQL pour vérifier

### Voir tous les serveurs
```sql
SELECT id, name, code, state, health_status, 
       instance_count, available_capacity
FROM saas_server
ORDER BY id;
```

### Voir les instances par serveur
```sql
SELECT s.name as serveur, 
       COUNT(i.id) as nb_instances,
       s.max_instances,
       (100 * (s.max_instances - COUNT(i.id)) / s.max_instances) as capacite_libre
FROM saas_server s
LEFT JOIN saas_instance i ON s.id = i.server_id
GROUP BY s.id, s.name, s.max_instances
ORDER BY s.name;
```

### Vérifier les accès
```sql
SELECT * FROM ir_model_access 
WHERE model_id = (SELECT id FROM ir_model WHERE model = 'saas.server');
```

## 🛠️ Dépannage

### "ModuleNotFoundError: No module named 'requests'"
```bash
pip install requests
# Puis redémarrer Odoo
```

### "Cannot create database" lors de la création de template
- Vérifier que le serveur est actif
- Vérifier la connexion RPC avec "Test Connection"
- Vérifier les logs : `tail -f /var/log/odoo/odoo.log | grep saas_server`

### Les calculs (instance_count, available_capacity) ne se mettent pas à jour
- C'est normal, ils sont calculés à la volée
- Actualiser la page si nécessaire
- Pour forcer : `server.flush()` en Python

### "Server code must be lowercase"
- Vérifier que le code est en minuscules uniquement
- Ex: `prod-1` ✓, `Prod-1` ✗

## 📋 Checklist de validation complète

- [ ] Module mis à jour sans erreur
- [ ] Menu "Servers" visible sous Configuration
- [ ] Création serveur fonctionne
- [ ] Test connexion fonctionne
- [ ] Activation serveur fonctionne
- [ ] Validations fonctionnent
- [ ] Instances comptabilisées correctement
- [ ] Capacité calculée correctement
- [ ] CRON de monitoring active
- [ ] Tests unitaires passent
- [ ] Logs fonctionnent
- [ ] Sécurité (accès) configurée

## 📞 Support

### Logs importants
```
odoo.addons.saas_manager.models.saas_server
```

### Fichiers de référence
- `QUICK_START_SAAS_SERVER.md` - Utilisation rapide
- `SAAS_SERVER_MODEL.md` - Documentation complète
- `SAAS_SERVER_COMPLETE_SUMMARY.md` - Architecture détaillée
- `test_saas_server.py` - Exemples de code

### Commandes utiles
```bash
# Redémarrer Odoo
odoo-bin -c odoo.conf

# Mettre à jour et activer les tests
odoo-bin -u saas_manager -d db_name --test-enable

# Voir les logs en temps réel
tail -f /var/log/odoo/odoo.log

# Vérifier la syntaxe Python
python -m py_compile saas_manager/models/saas_server.py

# Vérifier les imports
python -c "from saas_manager.models.saas_server import SaaSServer; print('OK')"
```

## ✅ Après installation

1. **Configurer les serveurs** - Ajouter au moins 1 serveur actif
2. **Créer des templates** - Sur les serveurs
3. **Configurer les plans** - Pour les instances
4. **Tester la création d'instance** - Via une template
5. **Monitorer la santé** - Vérifier régulièrement

## 📈 Prochaines étapes

Après installation, vous pouvez :
1. Ajouter d'autres serveurs
2. Créer d'autres templates
3. Configurer les alertes (Phase 2)
4. Mettre en place le monitoring avancé (Phase 2)
5. Intégrer avec Prometheus (Phase 2)

---

**Status** : ✅ Prêt pour production
**Version** : 1.0.0
**Dernière mise à jour** : Décembre 2025

