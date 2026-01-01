# 🚀 Guide Rapide - Modèle SaaS Server

## 5 minutes pour commencer

### 1. Créer un serveur
Aller à **SaaS Manager > Configuration > Servers** et cliquer sur **Create**

```
Name: Production Server 1
Code: prod-1
Server URL: http://localhost:8069
Server IP: 127.0.0.1
Port: 8069
DB Host: localhost
DB Port: 5432
DB User: odoo
DB Password: odoo
Master Password: admin
Max Instances: 100
CPU Cores: 4
Memory: 16 GB
Disk: 500 GB
```

### 2. Tester la connexion
Cliquer sur le bouton **Test Connection** pour vérifier que le serveur est accessible

### 3. Activer le serveur
Cliquer sur le bouton **Activate** pour mettre le serveur en ligne
- ✅ Vérifie automatiquement la connexion
- ✅ Change l'état en `active`
- ✅ Marque la santé comme `healthy`

### 4. Créer une template
Aller à **SaaS Manager > Configuration > Templates** et créer une nouvelle template

```
Name: Restaurant Template
Code: restaurant
Server: Production Server 1  (sélectionner le serveur créé)
Template Database: template_restaurant
```

### 5. Créer la base template
Cliquer sur le bouton **Create Database** pour :
- ✅ Créer la BD PostgreSQL
- ✅ Installer les modules de base
- ✅ Marquer comme prête

### 6. Créer une instance client
Aller à **SaaS Manager > Operations > Instances** et créer une instance

```
Name: Client ABC
Customer: Sélectionner client
Template: Restaurant Template
Plan: Sélectionner plan
Server: Production Server 1  (auto-sélectionné si capacité)
```

Le système :
- ✅ Clone automatiquement la template
- ✅ Crée la BD client en 10 secondes
- ✅ Configure l'instance
- ✅ Marque comme active

## Opérations quotidiennes

### Monitorer la santé des serveurs
```python
# Vérifier la santé d'un serveur
server.action_check_health()

# Obtenir le meilleur serveur disponible
best_server = self.env['saas.server'].get_available_server(min_capacity_percent=20)
```

### Vérifier la capacité
La capacité est calculée automatiquement :
```
Available Capacity = (Max Instances - Current Instances) / Max Instances * 100
```

### Actions rapides
| Action | Effect |
|--------|--------|
| **Activate** | Met le serveur en ligne (test connexion) |
| **Deactivate** | Met le serveur hors ligne (si vide) |
| **Maintenance** | Mode maintenance (instances restent actives) |
| **Check Health** | Vérification de santé RPC |
| **Test Connection** | Teste la connexion |
| **View Instances** | Affiche toutes les instances du serveur |

## Statuts serveur

```
┌─────────────┬──────────────────────────────────────┐
│ État        │ Signification                        │
├─────────────┼──────────────────────────────────────┤
│ Draft       │ Créé mais pas encore testée          │
│ Active      │ En service, prêt à héberger          │
│ Maintenance │ En maintenance, instances actives    │
│ Offline     │ Indisponible (connexion échouée)    │
│ Disabled    │ Désactivé volontairement            │
└─────────────┴──────────────────────────────────────┘
```

## Santé du serveur

```
Healthy     ✓ Serveur en ligne et réactif
Warning     ⚠ Serveur lent ou problème détecté
Critical    ✗ Serveur indisponible
Unknown     ? Jamais vérifié
```

## Cas d'usage courants

### 1. Ajouter un nouveau serveur
```python
server = self.env['saas.server'].create({
    'name': 'Server 2',
    'code': 'server-2',
    'server_url': 'https://saas2.example.com',
    'max_instances': 100,
})
server.action_activate()
```

### 2. Migrer une instance vers un autre serveur
```python
# Lister les serveurs disponibles
servers = self.env['saas.server'].search([
    ('state', '=', 'active'),
    ('available_capacity', '>=', 20)
])

# Changer le serveur de l'instance
instance.server_id = servers[0]
```

### 3. Augmenter la capacité d'un serveur
```python
server.max_instances = 150
```

### 4. Vérifier la capacité totale
```python
total_instances = sum(s.instance_count for s in servers)
total_capacity = sum(s.max_instances for s in servers)
print(f"Utilisation: {total_instances}/{total_capacity}")
```

## Monitoring automatique

Le système vérifie automatiquement la santé de tous les serveurs :
- **Fréquence** : Toutes les 15 minutes
- **Vérification** : RPC appel via `/jsonrpc`
- **Mise à jour** : `health_status` et `state`
- **Log** : `odoo.addons.saas_manager.models.saas_server`

## Logs & Débogage

### Voir les logs
```bash
# Tous les événements serveur
tail -f /var/log/odoo/odoo.log | grep saas_server

# Seulement les erreurs
tail -f /var/log/odoo/odoo.log | grep "ERROR.*saas_server"
```

### Logs importants
```
New SaaS server created: [name] ([code])
Server [name] state changed to: [state]
Testing connection to server [name]: [url]
Connection to server [name] successful
Health check failed for server [name]: [error]
```

## Astuces & Bonnes pratiques

### ✓ À faire
- ✅ Toujours tester la connexion avant d'activer
- ✅ Monitorer la capacité disponible
- ✅ Vérifier la santé régulièrement
- ✅ Documenter les changements
- ✅ Backup avant migration

### ✗ À éviter
- ❌ Ne pas désactiver serveur avec instances
- ❌ Ne pas supprimer serveur avec instances
- ❌ Ne pas mettre max_instances à 0
- ❌ Ne pas modifier BD directement
- ❌ Ne pas ignorer les alertes de santé

## Dépannage

### "Cannot activate server. Connection test failed"
→ Vérifier que `server_url` est correct et accessible

### "No available server found"
→ Tous les serveurs sont à capacité. Ajouter un nouveau serveur.

### "Server is OFFLINE"
→ Vérifier les logs. Peut être réseau ou serveur Odoo arrêté.

### "Cannot deactivate server while it has instances"
→ Migrer ou supprimer les instances d'abord

## Quelques requêtes SQL utiles

```sql
-- Voir tous les serveurs
SELECT id, name, code, state, health_status FROM saas_server;

-- Serveurs actifs avec capacité disponible
SELECT name, instance_count, max_instances, 
       (100 * (max_instances - instance_count) / max_instances) as capacity
FROM saas_server 
WHERE state = 'active'
ORDER BY capacity DESC;

-- Instances par serveur
SELECT s.name, COUNT(i.id) as count
FROM saas_server s
LEFT JOIN saas_instance i ON s.id = i.server_id
GROUP BY s.id, s.name;
```

## API Python

```python
# Créer serveur
server = self.env['saas.server'].create({
    'name': 'New Server',
    'code': 'new-server',
    'server_url': 'http://localhost:8069',
})

# Activer
server.action_activate()

# Obtenir meilleur serveur
best = self.env['saas.server'].get_available_server(20)

# Vérifier santé
server.action_check_health()

# Voir instances
instances = server.instance_ids
```

## Support

📖 **Documentation complète** : `SAAS_SERVER_MODEL.md`
📋 **Résumé complet** : `SAAS_SERVER_COMPLETE_SUMMARY.md`
🧪 **Exemples tests** : `tests/test_saas_server.py`
🔍 **Logs** : `odoo.addons.saas_manager.models.saas_server`

---

**Dernière mise à jour** : Décembre 2025
**Version** : 1.0.0
**Statut** : Production Ready ✓

