# Quick Start Guide - Email Provisioning System

## 📧 Système d'Emails d'Approvisionnement SaaS

Ce guide vous aidera à configurer et tester le système d'envoi d'emails automatiques pour les instances SaaS.

## ✅ Checklist d'Installation

### 1. Vérifier les Modifications du Code
- [ ] Les 4 méthodes d'envoi d'email sont ajoutées à `saas_instance.py`
- [ ] Les appels aux méthodes sont intégrés dans les actions
- [ ] Les 2 nouveaux templates d'email sont dans `mail_template_data.xml`

### 2. Configuration du Serveur SMTP

**Étape 1:** Accédez aux paramètres Odoo
```
Paramètres → Technique → Email → Serveurs de Messagerie Sortante
```

**Étape 2:** Créez une nouvelle configuration SMTP

Pour **Gmail:**
- **Nom du Serveur:** Gmail
- **Serveur SMTP:** smtp.gmail.com
- **Port SMTP:** 587
- **Utilisateur:** votre.email@gmail.com
- **Mot de passe:** votre_mot_de_passe_app (App Password)
- **Chiffrement:** TLS

Pour **SendGrid:**
- **Nom du Serveur:** SendGrid
- **Serveur SMTP:** smtp.sendgrid.net
- **Port SMTP:** 587
- **Utilisateur:** apikey
- **Mot de passe:** votre_clé_api
- **Chiffrement:** TLS

Pour **Mailgun:**
- **Nom du Serveur:** Mailgun
- **Serveur SMTP:** smtp.mailgun.org
- **Port SMTP:** 587
- **Utilisateur:** votre_email@votre_domaine
- **Mot de passe:** votre_clé_smtp
- **Chiffrement:** TLS

**Étape 3:** Testez la connexion
- Cliquez sur le bouton **"Tester la Connexion"**
- Vous devez voir le message "Connection Test Successful"

### 3. Configurer l'Email par Défaut

```
Paramètres → Technique → Paramètres Système
```

Cherchez et configurez:
- `mail.default.from` - Adresse email par défaut (ex: no-reply@example.com)

### 4. Vérifier les Partenaires

Chaque client qui recevra des emails doit avoir une adresse email:

```
Contacts → Sélectionner un Contact → Onglet "Informations de Contact" → Email
```

## 🧪 Test du Système

### Test 1: Vérifier les Templates

1. Allez à: **Paramètres** → **Technique** → **Email** → **Modèles**
2. Vérifiez que ces templates existent:
   - ✓ SaaS: Instance Provisioned
   - ✓ SaaS: Instance Suspended
   - ✓ SaaS: Instance Reactivated
   - ✓ SaaS: Instance Terminated

### Test 2: Vérifier les Méthodes

1. Ouvrez une instance SaaS existante
2. Vérifiez les boutons d'action disponibles:
   - ✓ Provision Instance
   - ✓ Suspend
   - ✓ Reactivate
   - ✓ Terminate

### Test 3: Test Complet de Provisionnement

1. **Créez une instance de test:**
   - Allez à: **SaaS** → **Instances** → **Créer**
   - Remplissez les champs:
     - Nom: "Test Instance"
     - Client: Sélectionnez un client avec email
     - Template: Sélectionnez une template
     - Plan: Sélectionnez un plan
     - Serveur: Sélectionnez un serveur

2. **Provisionnez l'instance:**
   - Cliquez sur **"Provision Instance"**
   - Attendez que l'opération se termine

3. **Vérifiez l'email:**
   - Ouvrez la boîte mail du client
   - Cherchez un email avec le sujet: "Your SaaS Instance is Ready - [Nom Instance]"
   - Vérifiez que l'email contient:
     - ✓ URL d'accès
     - ✓ Login admin
     - ✓ Mot de passe admin
     - ✓ Nom du plan

### Test 4: Test de Suspension

1. Ouvrez l'instance de test
2. Cliquez sur **"Suspend"**
3. Vérifiez que:
   - ✓ L'état change à "Suspended"
   - ✓ Un email de suspension est reçu

### Test 5: Test de Réactivation

1. Ouvrez l'instance suspendue
2. Cliquez sur **"Reactivate"**
3. Vérifiez que:
   - ✓ L'état change à "Active"
   - ✓ Un email de réactivation est reçu

### Test 6: Test de Suppression

1. Ouvrez l'instance
2. Cliquez sur **"Terminate"**
3. Vérifiez que:
   - ✓ L'état change à "Terminated"
   - ✓ La base de données est supprimée
   - ✓ Un email de suppression est reçu

## 📊 Vérifier les Logs

Pour déboguer, consultez les logs Odoo:

```bash
# Afficher les derniers logs
tail -50 /var/log/odoo/odoo.log

# Filtrer les logs du SaaS Manager
grep "saas_manager" /var/log/odoo/odoo.log

# Suivre les logs en temps réel
tail -f /var/log/odoo/odoo.log | grep "saas_manager"

# Chercher les erreurs d'email
grep -i "email" /var/log/odoo/odoo.log
```

## 🔍 Troubleshooting

### Problème: Les emails ne sont pas reçus

**Solution 1: Vérifier la configuration SMTP**
```bash
# Tester la connexion SMTP
python3 -c "
import smtplib
smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.starttls()
smtp.login('votre.email@gmail.com', 'mot_de_passe')
print('✓ SMTP connection successful')
"
```

**Solution 2: Vérifier les paramètres dans Odoo**
```
Paramètres → Technique → Paramètres Système
- mail.smtp.host
- mail.smtp.port
- mail.smtp.user
- mail.smtp.password
```

**Solution 3: Vérifier les logs**
```bash
grep -A 5 "Failed to send" /var/log/odoo/odoo.log
```

### Problème: "Template not found"

1. Redémarrez Odoo
2. Mettez à jour le module SaaS Manager
3. Vérifiez que les templates existent:
   ```
   Paramètres → Technique → Email → Modèles
   ```

### Problème: "Customer has no email"

1. Allez à: **Contacts** → Sélectionnez le client
2. Ajoutez une adresse email dans l'onglet "Informations de Contact"
3. Sauvegardez et réessayez

### Problème: Les emails vont au spam

1. Configurez **SPF** et **DKIM** pour votre domaine
2. Utilisez une adresse d'expéditeur fiable
3. Vérifiez que le serveur SMTP est approuvé

## 📝 Personnaliser les Templates

1. Allez à: **Paramètres** → **Technique** → **Email** → **Modèles**
2. Cherchez "SaaS: Instance Provisioned"
3. Cliquez pour l'éditer
4. Modifiez le sujet et le contenu HTML
5. Sauvegardez

**Variables disponibles:**
- `{{ object.name }}` - Nom de l'instance
- `{{ object.domain }}` - Domaine complet
- `{{ object.protocol }}` - HTTP/HTTPS
- `{{ object.admin_login }}` - Login admin
- `{{ object.admin_password }}` - Mot de passe admin
- `{{ object.partner_id.name }}` - Nom du client
- `{{ object.partner_id.email }}` - Email du client
- `{{ object.plan_id.name }}` - Nom du plan
- `{{ object.database_name }}` - Nom de la base de données

## 📞 Support et Documentation

Pour plus de détails:
- Consultez: `EMAIL_PROVISIONING.md`
- Consultez: `CHANGELOG_EMAIL_SYSTEM.md`

## 🚀 Déploiement en Production

Avant de déployer en production:

1. **Testez** tous les cas d'utilisation
2. **Configurez** le domaine SPF/DKIM
3. **Utilisez** un service email professionnel (SendGrid, Mailgun, etc.)
4. **Surveillez** les logs pour les erreurs
5. **Sauvegardez** régulièrement votre base de données

## ✨ Prochaines Étapes

- [ ] Configurer le serveur SMTP
- [ ] Vérifier les adresses email des clients
- [ ] Tester le système complet
- [ ] Personnaliser les templates d'email
- [ ] Déployer en production

---

**Dernière mise à jour:** 31 Décembre 2025
**Version:** 1.0

