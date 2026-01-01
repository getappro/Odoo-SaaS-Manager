# Guide de Troubleshooting - Système d'Emails SaaS

## 📖 Dépannage Avancé du Système d'Emails

### ⚠️ Problème 1: Les emails ne sont pas reçus du tout

#### Étape 1: Vérifier que le serveur SMTP est configuré
```bash
# Accédez à Odoo
# Paramètres → Technique → Email → Serveurs de Messagerie Sortante

# Vérifiez:
✓ Serveur SMTP (ex: smtp.gmail.com)
✓ Port (ex: 587 pour TLS, 465 pour SSL)
✓ Utilisateur (votre email)
✓ Mot de passe (correctement défini)
✓ Chiffrement (TLS ou SSL)
```

#### Étape 2: Tester la connexion SMTP
```bash
python3 << 'EOF'
import smtplib

# Configuration pour Gmail
smtp_server = "smtp.gmail.com"
smtp_port = 587
username = "votre.email@gmail.com"
password = "votre_app_password"

try:
    server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
    server.starttls()
    server.login(username, password)
    print("✓ Connexion SMTP réussie!")
    server.quit()
except smtplib.SMTPAuthenticationError:
    print("✗ Erreur d'authentification - Vérifiez votre login/password")
except smtplib.SMTPException as e:
    print(f"✗ Erreur SMTP: {str(e)}")
except Exception as e:
    print(f"✗ Erreur de connexion: {str(e)}")
EOF
```

#### Étape 3: Vérifier dans les paramètres Odoo
```sql
-- Connectez-vous à la base PostgreSQL
psql -d [database_name] -U [user]

-- Vérifiez la configuration du serveur
SELECT * FROM ir_mail_server WHERE name LIKE '%Gmail%' OR name LIKE '%SMTP%';

-- Vérifiez que le serveur est actif
SELECT id, name, smtp_host, smtp_port, smtp_user, smtp_encryption FROM ir_mail_server;
```

#### Étape 4: Vérifier que le client a une adresse email
```bash
# Via l'interface Odoo:
# Contacts → Sélectionner le client → Onglet "Informations de Contact" → Email

# Via SQL:
SELECT id, name, email FROM res_partner WHERE name = 'Nom du Client';
```

---

### ⚠️ Problème 2: Message "Template not found"

**Erreur dans les logs:**
```
Email template 'saas_manager.mail_template_instance_provisioned' not found
```

#### Solution 1: Redémarrer Odoo
```bash
cd /opt/GetapERP/GetapERP-V18
bash restart_odoo.sh
```

#### Solution 2: Mettre à jour le module
```
Paramètres → Applications
Chercher: "SaaS Manager"
Cliquer: "Mettre à jour"
```

#### Solution 3: Vérifier que les templates existent
```bash
# Via l'interface Odoo:
# Paramètres → Technique → Email → Modèles

# Via SQL:
SELECT id, name, model_id FROM mail_template WHERE name LIKE '%SaaS%';

-- Doit retourner 4 résultats:
-- 1. SaaS: Instance Provisioned
-- 2. SaaS: Instance Suspended
-- 3. SaaS: Instance Reactivated
-- 4. SaaS: Instance Terminated
```

#### Solution 4: Réinstaller les données
```bash
# Supprimer et réinstaller les données du template
psql -d [database_name] -U [user] << 'EOF'
DELETE FROM mail_template WHERE module = 'saas_manager';
EOF

# Redémarrer Odoo
bash restart_odoo.sh
```

---

### ⚠️ Problème 3: "Customer has no email address"

**Erreur dans les logs:**
```
Customer [Nom] has no email address. Cannot send provisioning email
```

#### Solution:
```
Contacts → Sélectionner le client
Onglet "Informations de Contact"
Ajouter l'email dans le champ "Email"
Cliquer "Enregistrer"
```

---

### ⚠️ Problème 4: Les emails vont au spam

#### Cause 1: SPF non configuré

**Solution:** Configurez les enregistrements SPF de votre domaine
```dns
v=spf1 include:smtp.sendgrid.net ~all
```

#### Cause 2: DKIM non configuré

**Solution:** Configurez DKIM dans votre fournisseur email (SendGrid, Mailgun, etc.)

#### Cause 3: Serveur SMTP non approuvé

**Solution:** Utilisez un service email professionnel:
- ✓ SendGrid
- ✓ Mailgun
- ✓ Amazon SES
- ✓ Google Workspace

---

### ⚠️ Problème 5: Timeout lors de l'envoi d'email

**Erreur dans les logs:**
```
Timeout: Failed to send email after 30 seconds
```

#### Solution 1: Augmenter le timeout
```python
# Modifier dans saas_instance.py:
template.send_mail(
    self.id,
    force_send=True,
    raise_exception=False,
    timeout=60  # Augmenter de 30 à 60 secondes
)
```

#### Solution 2: Vérifier la connexion réseau
```bash
# Tester la connectivité au serveur SMTP
ping smtp.gmail.com
telnet smtp.gmail.com 587
```

#### Solution 3: Vérifier que le serveur SMTP n'est pas surchargé
```bash
# Réduire le nombre d'envois simultanés
# Ou utiliser un système de queue (Celery)
```

---

### ⚠️ Problème 6: Erreur 550 "Relay access denied"

**Erreur dans les logs:**
```
SMTP Error 550: Relay access denied. Explain: 550 Relay access denied
```

#### Solution:
```
Vérifiez que l'adresse de l'expéditeur (From) est autorisée sur le serveur SMTP
- Elle doit correspondre au compte utilisateur
- Ou être dans une liste d'adresses autorisées du serveur
```

---

### ⚠️ Problème 7: Erreur 535 "Authentication failed"

**Erreur dans les logs:**
```
SMTP Error 535: Username and password not accepted
```

#### Solution 1: Vérifier le mot de passe
```bash
# Pour Gmail, vous devez utiliser un "App Password" :
# https://myaccount.google.com/apppasswords
# PAS votre mot de passe Google

# Pour autres services:
# Vérifiez les credentials dans le fournisseur email
```

#### Solution 2: Réinitialiser le mot de passe dans Odoo
```
Paramètres → Technique → Email → Serveurs de Messagerie Sortante
Sélectionner le serveur
Mettre à jour le mot de passe
Tester la connexion
```

---

### ⚠️ Problème 8: Les logs ne montrent rien

#### Solution 1: Vérifier que les logs d'Odoo sont actifs
```bash
# Vérifiez le niveau de log dans odoo.conf
grep "log_level" /opt/GetapERP/GetapERP-V18/odoo.conf

# Doit être: log_level = info (ou debug)
```

#### Solution 2: Vérifier l'emplacement des logs
```bash
# Les logs sont généralement dans:
ls -la /var/log/odoo/

# Ou spécifiés dans odoo.conf:
grep "logfile" /opt/GetapERP/GetapERP-V18/odoo.conf
```

#### Solution 3: Activer les logs de email
```python
# Ajouter dans saas_instance.py:
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)  # Activer le mode debug
```

---

## 🔍 Commandes Utiles de Diagnostic

### Vérifier la configuration SMTP
```sql
SELECT id, name, smtp_host, smtp_port, smtp_user, smtp_encryption 
FROM ir_mail_server 
WHERE active = true;
```

### Vérifier les partenaires sans email
```sql
SELECT id, name, email 
FROM res_partner 
WHERE email IS NULL OR email = '';
```

### Vérifier les templates d'email
```sql
SELECT id, name, model_id, subject 
FROM mail_template 
WHERE name LIKE '%SaaS%';
```

### Vérifier les instances créées
```sql
SELECT id, name, partner_id, state, admin_login, admin_password 
FROM saas_instance 
ORDER BY create_date DESC 
LIMIT 10;
```

### Vérifier les logs des emails envoyés
```bash
grep -i "email" /var/log/odoo/odoo.log | tail -50
grep "Sending.*email\|email sent" /var/log/odoo/odoo.log
```

---

## 📊 Statistiques d'Envoi

### Pour vérifier combien d'emails ont été envoyés:
```sql
SELECT 
    COUNT(*) as total_messages,
    COUNT(CASE WHEN state = 'sent' THEN 1 END) as sent,
    COUNT(CASE WHEN state = 'failed' THEN 1 END) as failed
FROM mail_mail;
```

### Pour voir les détails des erreurs:
```sql
SELECT id, message_id, state, failure_reason 
FROM mail_mail 
WHERE state = 'failed' 
ORDER BY create_date DESC;
```

---

## 🧪 Test Complet du Système

```bash
#!/bin/bash

# Script de test complet

echo "Testing Email Provisioning System"
echo "=================================="

# Test 1: Vérifier SMTP
echo "1. Testing SMTP Configuration..."
python3 << 'EOF'
import smtplib
try:
    s = smtplib.SMTP('localhost', 25)
    s.quit()
    print("✓ SMTP on localhost is working")
except:
    print("✗ SMTP on localhost is NOT working")
EOF

# Test 2: Vérifier les templates
echo ""
echo "2. Testing Email Templates..."
psql -d [database_name] -U [user] -c \
  "SELECT name FROM mail_template WHERE name LIKE '%SaaS%';"

# Test 3: Vérifier les partenaires
echo ""
echo "3. Testing Partner Email Configuration..."
psql -d [database_name] -U [user] -c \
  "SELECT name, email FROM res_partner WHERE email IS NOT NULL LIMIT 5;"

# Test 4: Vérifier les instances
echo ""
echo "4. Testing SaaS Instances..."
psql -d [database_name] -U [user] -c \
  "SELECT name, state, partner_id FROM saas_instance ORDER BY create_date DESC LIMIT 5;"

echo ""
echo "✓ Diagnostics completed"
```

---

## 📞 Support Avancé

### Pour les erreurs liées au serveur SMTP:
1. Contactez votre fournisseur email (Gmail, SendGrid, etc.)
2. Vérifiez les logs d'erreur fournis
3. Consultez la documentation de votre fournisseur

### Pour les erreurs liées à Odoo:
1. Vérifiez les logs Odoo
2. Consultez la documentation Odoo officielle
3. Postez sur les forums Odoo Community

### Pour les erreurs liées au module SaaS:
1. Consultez les fichiers de documentation du module
2. Vérifiez que toutes les modifications sont appliquées
3. Redémarrez Odoo complètement

---

## 📝 Notes Importantes

⚠️ **Les erreurs d'email ne bloquent pas le provisionnement**
- Le client recevra quand même ses identifiants
- Les emails sont des notifications, pas critiques

✓ **Toutes les actions sont loggées**
- Chaque tentative d'envoi est tracée
- Les erreurs incluent les détails complets

✓ **Vous pouvez relancer manuellement**
- Si un email n'est pas envoyé, vous pouvez le relancer manuellement depuis le template

---

**Fin du guide de troubleshooting**

