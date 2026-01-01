# Système d'Emails de Provisionnement SaaS - Résumé des Modifications

## Date: 31 Décembre 2025

## Modifications Apportées

### 1. Fichier: `saas_manager/models/saas_instance.py`

#### Modifications à `action_provision_instance()`
- Ajout de l'appel à `self._send_provisioning_email()` après l'activation de l'instance
- Les détails de connexion (login, password, URL) sont maintenant envoyés par email au client

#### Nouvelles Méthodes Ajoutées

**`_send_provisioning_email()`**
- Envoie un email au client avec les détails complets de l'instance
- Template: `saas_manager.mail_template_instance_provisioned`
- Inclus: URL, login, password, plan
- Gestion d'erreurs: les erreurs d'email ne bloquent pas le provisionnement

**`_send_suspension_email()`**
- Envoie une notification lors de la suspension de l'instance
- Template: `saas_manager.mail_template_instance_suspended`
- Appelée automatiquement par `action_suspend()`

**`_send_reactivation_email()`**
- Envoie une notification lors de la réactivation de l'instance
- Template: `saas_manager.mail_template_instance_reactivated`
- Appelée automatiquement par `action_reactivate()`

**`_send_termination_email()`**
- Envoie une notification lors de la suppression de l'instance
- Template: `saas_manager.mail_template_instance_terminated`
- Appelée automatiquement par `action_terminate()`

#### Modifications aux Actions
- `action_suspend()` - Appel ajouté à `_send_suspension_email()`
- `action_reactivate()` - Appel ajouté à `_send_reactivation_email()`
- `action_terminate()` - Appel ajouté à `_send_termination_email()`

### 2. Fichier: `saas_manager/data/mail_template_data.xml`

#### Templates Existants
- `mail_template_instance_provisioned` - Mise à jour pour utiliser `{{ object.protocol }}`

#### Nouveaux Templates Ajoutés

**`mail_template_instance_reactivated`**
```xml
<record id="mail_template_instance_reactivated" model="mail.template">
    <!-- Notifie le client de la réactivation -->
    <!-- Affiche le lien d'accès avec le bon protocole -->
    <!-- Montre la date/heure de réactivation -->
</record>
```

**`mail_template_instance_terminated`**
```xml
<record id="mail_template_instance_terminated" model="mail.template">
    <!-- Confirme la suppression de l'instance -->
    <!-- Avertit que les données sont permanemment supprimées -->
    <!-- Fournit les détails de la base supprimée -->
</record>
```

## Flux d'Exécution

### Lors du Provisionnement
```
user clicks action_provision_instance()
  ↓
validates server & capacity
  ↓
_clone_template_database()
  ↓
_neutralize_database()
  ↓
_customize_instance()
  ↓
_create_client_admin()
  ↓
_configure_subdomain()
  ↓
write state to 'active'
  ↓
_send_provisioning_email() ← NOUVEAU
  ↓
notification popup
```

### Lors de la Suspension
```
user clicks action_suspend()
  ↓
validate state
  ↓
write state to 'suspended'
  ↓
_send_suspension_email() ← NOUVEAU
  ↓
notification popup
```

### Lors de la Réactivation
```
user clicks action_reactivate()
  ↓
validate state
  ↓
write state to 'active'
  ↓
_send_reactivation_email() ← NOUVEAU
  ↓
notification popup
```

### Lors de la Suppression
```
user clicks action_terminate()
  ↓
verify is_admin
  ↓
_delete_database()
  ↓
write state to 'terminated'
  ↓
_send_termination_email() ← NOUVEAU
  ↓
notification popup
```

## Configuration Requise

### Serveur SMTP
L'administrateur doit configurer un serveur SMTP dans Odoo:
- **Paramètres** → **Technique** → **Email** → **Serveurs Sortants**

### Emails des Clients
Chaque client (partenaire) doit avoir une adresse email configurée.

## Tests Recommandés

### 1. Test de Provisionnement
```gherkin
Given un template SaaS existe
And un client (partenaire) a une email
When je crée une instance et la provisionne
Then l'instance est en état 'active'
And un email est reçu par le client
And l'email contient les détails d'accès
```

### 2. Test de Suspension
```gherkin
Given une instance est en état 'active'
And le client a une email
When je suspends l'instance
Then l'instance est en état 'suspended'
And un email de suspension est reçu
```

### 3. Test de Réactivation
```gherkin
Given une instance est en état 'suspended'
And le client a une email
When je réactive l'instance
Then l'instance est en état 'active'
And un email de réactivation est reçu
```

### 4. Test de Résiliation
```gherkin
Given une instance existe
And je suis admin SaaS
When je résilie l'instance
Then l'instance est en état 'terminated'
And la base de données est supprimée
And un email de résiliation est reçu
```

## Gestion d'Erreurs

Tous les envois d'emails utilisent `force_send=True` et `raise_exception=False`:

```python
template.send_mail(
    self.id,
    force_send=True,        # Envoyer immédiatement
    raise_exception=False   # Ne pas interrompre le processus si erreur
)
```

**Cela signifie:**
- Les erreurs d'email ne bloquent PAS le provisionnement
- Les logs contiennent les détails des erreurs
- Le client recevra quand même ses identifiants (créés dans _create_client_admin)

## Documentation Complète

Pour la documentation détaillée, voir: `EMAIL_PROVISIONING.md`

## Déploiement

Pour déployer ces modifications:

1. **Redémarrer Odoo:**
   ```bash
   bash restart_odoo.sh
   ```

2. **Mettre à jour le module:**
   - Aller à **Applications**
   - Chercher "SaaS Manager"
   - Cliquer "Mettre à jour"

3. **Configurer le serveur SMTP:**
   - Aller à **Paramètres** → **Technique** → **Email** → **Serveurs Sortants**
   - Créer/Tester la configuration SMTP

4. **Tester le provisionnement:**
   - Créer une instance SaaS
   - Provisionner l'instance
   - Vérifier que l'email est reçu

## Notes

- Les templates d'email peuvent être personnalisés dans l'interface Odoo
- Les emails utilisent les variables Qweb d'Odoo
- Les logs incluent tous les détails des tentatives d'envoi
- Les adresses email du client peuvent être modifiées sans perte de données

## Évolutions Possibles (Phase 2)

- [ ] Emails en arrière-plan avec Celery
- [ ] Support SMS
- [ ] Préférences de notification par client
- [ ] Templates multilingues
- [ ] Webhooks pour intégrations
- [ ] Historique des communications
- [ ] Confirmation de lecture
- [ ] Rappels automatiques

## Support

Pour toute question ou problème:
1. Consultez les logs Odoo
2. Vérifiez la configuration SMTP
3. Vérifiez que le client a une email
4. Consultez `EMAIL_PROVISIONING.md` pour la documentation détaillée

