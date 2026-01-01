# Email Provisioning System - Documentation

## Vue d'ensemble

Le système de provisioning des instances SaaS intègre un système d'envoi d'emails automatiques pour informer les clients des changements d'état de leurs instances.

## Fonctionnalités implémentées

### 1. Email de Provisionnement (Instance Provisioned)
**Déclencheur:** Lors de la réussite de `action_provision_instance()`

**Template:** `saas_manager.mail_template_instance_provisioned`

**Contenu:**
- Nom de l'instance
- URL d'accès (avec le bon protocole HTTP/HTTPS)
- Identifiant administrateur
- Mot de passe administrateur
- Plan souscrit
- Bouton d'accès direct

**Code:**
```python
def _send_provisioning_email(self):
    """Envoyer les détails de connexion après provisionnement"""
    template = self.env.ref('saas_manager.mail_template_instance_provisioned')
    template.send_mail(self.id, force_send=True, raise_exception=False)
```

### 2. Email de Suspension (Instance Suspended)
**Déclencheur:** Lors de `action_suspend()`

**Template:** `saas_manager.mail_template_instance_suspended`

**Contenu:**
- Raison de la suspension
- Nom et URL de l'instance
- Instructions pour la réactivation

**Code:**
```python
def _send_suspension_email(self):
    """Notifier le client de la suspension"""
    template = self.env.ref('saas_manager.mail_template_instance_suspended')
    template.send_mail(self.id, force_send=True, raise_exception=False)
```

### 3. Email de Réactivation (Instance Reactivated)
**Déclencheur:** Lors de `action_reactivate()`

**Template:** `saas_manager.mail_template_instance_reactivated`

**Contenu:**
- Confirmation de réactivation
- URL d'accès
- Date/heure de réactivation
- Bouton d'accès direct

**Code:**
```python
def _send_reactivation_email(self):
    """Notifier le client de la réactivation"""
    template = self.env.ref('saas_manager.mail_template_instance_reactivated')
    template.send_mail(self.id, force_send=True, raise_exception=False)
```

### 4. Email de Résiliation (Instance Terminated)
**Déclencheur:** Lors de `action_terminate()`

**Template:** `saas_manager.mail_template_instance_terminated`

**Contenu:**
- Confirmation de suppression
- Nom et base de données supprimés
- Date/heure de suppression
- Avertissement: données permanemment supprimées

**Code:**
```python
def _send_termination_email(self):
    """Notifier le client de la suppression définitive"""
    template = self.env.ref('saas_manager.mail_template_instance_terminated')
    template.send_mail(self.id, force_send=True, raise_exception=False)
```

## Configuration requise

### 1. Serveur de Messagerie
Vous devez configurer un serveur SMTP dans Odoo:
- Menu: **Paramètres** → **Technique** → **Email** → **Serveurs de Messagerie Sortante**
- Entrez vos paramètres SMTP (Gmail, SendGrid, etc.)

### 2. Adresse Email du Client
Assurez-vous que chaque client (partenaire) a une adresse email:
- Menu: **Contacts** → Sélectionner un contact
- Onglet: **Informations de Contact**
- Champ: **Email**

### 3. Modèles d'Email
Les modèles sont créés automatiquement lors de l'installation du module:
- Fichier: `saas_manager/data/mail_template_data.xml`

## Gestion des Erreurs

Tous les envois d'emails utilisent la gestion d'erreurs suivante:

```python
try:
    # Vérifier que le template existe
    template = self.env.ref('...', raise_if_not_found=False)
    if not template:
        _logger.warning("Template not found")
        return False
    
    # Vérifier que le client a une email
    if not self.partner_id.email:
        _logger.warning("Customer has no email")
        return False
    
    # Envoyer l'email
    template.send_mail(self.id, force_send=True, raise_exception=False)
    
    _logger.info("Email sent successfully")
    return True
    
except Exception as e:
    _logger.error(f"Email sending failed: {str(e)}")
    # N'affecte pas le provisionnement - juste une notification
    return False
```

**Important:** Les erreurs d'envoi d'email n'interrompent PAS le processus de provisionnement. Les emails sont des notifications, pas des critères fonctionnels.

## Personnalisation

Pour personnaliser les templates d'email:

1. Accédez à: **Paramètres** → **Technique** → **Email** → **Modèles**

2. Cherchez: `SaaS: Instance Provisioned` (ou autre)

3. Modifiez le contenu HTML/sujet selon vos besoins

4. Les variables disponibles sont:
   - `{{ object.name }}` - Nom de l'instance
   - `{{ object.domain }}` - Domaine complet
   - `{{ object.protocol }}` - HTTP/HTTPS
   - `{{ object.admin_login }}` - Login admin
   - `{{ object.admin_password }}` - Mot de passe admin
   - `{{ object.partner_id.name }}` - Nom du client
   - `{{ object.plan_id.name }}` - Nom du plan
   - `{{ object.database_name }}` - Nom de la base de données
   - `{{ object.write_date }}` - Date de modification

## Tests

### Test Manuel
1. Créer une instance SaaS
2. Cliquer sur "Provision Instance"
3. Vérifier que l'email est reçu par le client

### Logs
Pour déboguer, consultez les logs:
```bash
tail -f /var/log/odoo/odoo.log | grep "saas_manager"
```

Les logs incluent:
```
Sending provisioning email to client@example.com for instance MyInstance
Provisioning email sent successfully to client@example.com for instance MyInstance
```

## Limitations et Considérations

1. **Force Send:** Les emails sont envoyés immédiatement avec `force_send=True`
2. **No Exception:** `raise_exception=False` pour ne pas interrompre le processus
3. **Email Required:** Le client DOIT avoir une email pour recevoir les notifications
4. **Template Required:** Les templates doivent exister dans la base de données

## Évolutions Futures (Phase 2)

- [ ] Notification SMSous pour les informations critiques
- [ ] Webhooks pour intégrations externes
- [ ] Templates multilingues
- [ ] Envoi d'emails en arrière-plan avec Celery
- [ ] Historique des emails envoyés
- [ ] Préférences de notification par client

## Support

Pour toute question ou problème, consultez les logs:
```
/var/log/odoo/odoo.log
```

Ou cherchez les erreurs avec:
```bash
grep "email" /var/log/odoo/odoo.log
```

