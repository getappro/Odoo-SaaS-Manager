# Modèle SaaS Server

## Vue d'ensemble

Le modèle `saas.server` permet de gérer et monitorer les serveurs Odoo qui hébergent les instances SaaS. Chaque serveur peut héberger plusieurs instances clients.

## Fonctionnalités principales

### 1. Configuration du serveur
- **Informations de base** : Nom, code unique, description
- **URL et accès** : URL du serveur, adresse IP, port, credentials SSH
- **Configuration PostgreSQL** : Host, port, user, password, master password
- **Ressources** : CPU cores, mémoire (GB), espace disque (GB)

### 2. Gestion de la capacité
- **Max instances** : Nombre maximum d'instances que le serveur peut héberger
- **Instance count** : Nombre actuel d'instances hébergées (calculé automatiquement)
- **Available capacity** : Pourcentage de capacité disponible (calculé automatiquement)

### 3. Monitoring
- **État du serveur** : Draft, Active, Maintenance, Offline, Disabled
- **Statut de santé** : Healthy, Warning, Critical, Unknown
- **Vérification en ligne** : Vérification automatique de l'état du serveur via RPC
- **Dernière vérification** : Timestamp de la dernière vérification de santé

### 4. Actions disponibles

#### action_check_health()
Vérifie l'état de santé du serveur en tentant une connexion RPC.
- Met à jour `health_status` et `last_check_date`
- Change l'état en `active` si le serveur est en ligne, `offline` sinon

#### action_activate()
Active le serveur après vérification de la connexion.
- Teste d'abord la connexion au serveur
- Change l'état à `active` et `health_status` à `healthy`

#### action_deactivate()
Désactive le serveur (seulement si aucune instance n'est hébergée).

#### action_maintenance()
Met le serveur en mode maintenance.

#### action_test_connection()
Teste la connexion au serveur (affiche une notification du résultat).

#### action_view_instances()
Affiche toutes les instances hébergées sur ce serveur.

### 5. Méthodes utilitaires

#### _test_connection()
Teste la connexion RPC au serveur via le endpoint `/jsonrpc`.
Utilise le service `common.version` pour vérifier la disponibilité.

Retourne : `bool` (True si la connexion est réussie)

#### get_available_server(min_capacity_percent=20)
Classe method pour obtenir un serveur disponible avec suffisamment de capacité.

```python
server = self.env['saas.server'].get_available_server(min_capacity_percent=20)
```

Lève `UserError` si aucun serveur disponible n'est trouvé.

## Flux de travail typique

### 1. Créer un nouveau serveur
1. Accédez à **SaaS Manager > Configuration > Servers**
2. Cliquez sur **Create**
3. Remplissez les informations de base (nom, code, URL du serveur)
4. Configurez la connexion PostgreSQL
5. Définissez les ressources du serveur (CPU, mémoire, disque)
6. Sauvegardez

### 2. Activer le serveur
1. Cliquez sur le bouton **Test Connection** pour vérifier la connexion
2. Si le test réussit, cliquez sur **Activate**
3. Le serveur est maintenant prêt à héberger des instances

### 3. Monitorer le serveur
1. Utilisez le bouton **Check Health** pour vérifier l'état
2. Consultez les métriques de capacité disponible
3. Consultez l'historique des vérifications de santé

### 4. Créer une instance sur ce serveur
```python
server = self.env['saas.server'].get_available_server()
instance = self.env['saas.instance'].create({
    'name': 'Client Instance',
    'database_name': 'client_db',
    'subdomain': 'client',
    'template_id': template.id,
    'plan_id': plan.id,
    'server_id': server.id,  # Lier au serveur
    'partner_id': partner.id,
})
```

## Sécurité

- **Groupes d'accès** :
  - `group_saas_user` : Lecture seule
  - `group_saas_manager` : Lecture/Écriture (pas création/suppression)
  - `group_saas_admin` : Accès complet

- **Contraintes** :
  - Code unique (lowercase obligatoire)
  - URL du serveur unique
  - URL doit commencer par `http://` ou `https://`
  - `max_instances` doit être > 0
  - Impossible de supprimer un serveur avec des instances hébergées

## Intégration avec SaaS Instance

Le modèle `saas.instance` a été mis à jour avec un champ `server_id` pour lier chaque instance à un serveur.

```python
class SaaSInstance(models.Model):
    _name = 'saas.instance'
    
    server_id = fields.Many2one(
        'saas.server',
        string='Server',
        required=True,
        ondelete='restrict',
    )
```

## API RPC

Le serveur utilise l'API RPC d'Odoo pour la communication :

### Test de connexion
```json
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "common",
        "method": "version"
    },
    "id": 1
}
```

## Logging

Tous les événements sont enregistrés dans les logs :
- Création de serveur
- Changement d'état
- Vérifications de santé
- Tentatives de connexion

Consultez les logs avec la clé : `odoo.addons.saas_manager.models.saas_server`

## À venir (Phase 2)

- [ ] Monitoring en temps réel via Prometheus
- [ ] Alertes automatiques en cas de problème
- [ ] Migration d'instances entre serveurs
- [ ] Load balancing automatique
- [ ] Backup automatique
- [ ] Replication haute disponibilité

