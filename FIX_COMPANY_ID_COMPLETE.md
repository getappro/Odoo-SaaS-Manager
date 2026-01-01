# 🔧 GUIDE COMPLET - Résoudre l'Erreur company_id

**Date:** 1er Janvier 2026  
**Problème:** Erreur `object.company_id` toujours présente malgré les corrections  
**Cause:** Les anciens templates restent en cache dans la base de données  
**Solution:** Supprimer les anciens templates et forcer la recréation

---

## ❌ SYMPTÔME

Logs montrant toujours l'erreur:
```
AttributeError: 'saas.instance' object has no attribute 'company_id'
Failed to render inline_template: {{ (object.company_id.email_formatted or user.email_formatted) }}
```

Cela signifie que **les anciens templates sont toujours actifs dans la base de données**.

---

## ✅ SOLUTION COMPLÈTE (5 ÉTAPES)

### ÉTAPE 1: Arrêter Odoo
```bash
pkill -f "odoo-bin"
```

### ÉTAPE 2: Supprimer les anciens templates de la BD
```bash
psql -U getappro -d dev -c "DELETE FROM mail_template WHERE name IN ('SaaS: Instance Provisioned', 'SaaS: Instance Suspended', 'SaaS: Instance Reactivated', 'SaaS: Instance Terminated', 'SaaS: Subscription Expiring');"
```

### ÉTAPE 3: Redémarrer Odoo
```bash
cd /opt/GetapERP/GetapERP-V18
bash restart_odoo.sh
```

### ÉTAPE 4: Accéder à Odoo
- Ouvrir un navigateur
- Aller à http://dev.africasys.ma/
- Vider le cache du navigateur (Ctrl+Shift+Del)

### ÉTAPE 5: Mettre à jour le module
```
Paramètres → Applications → SaaS Manager → Mettre à jour
```

---

## 🔍 VÉRIFICATION

Après ces étapes, vérifier dans les logs:

✓ Les nouveaux templates sont créés lors de la mise à jour du module  
✓ Les templates utilisent `user.email_formatted` (pas `object.company_id`)  
✓ Aucune erreur AttributeError

Vérifier dans la BD:
```bash
psql -U getappro -d dev -c "SELECT id, name, email_from FROM mail_template WHERE name LIKE '%SaaS%';"
```

Doit montrer `{{ user.email_formatted }}` dans le champ `email_from`.

---

## 🚀 TESTER L'ENVOI D'EMAIL

1. Créer une nouvelle instance SaaS
2. Cliquer "Provision Instance"
3. Vérifier que le client reçoit un email
4. Consulter les logs pour vérifier pas d'erreur:
   ```bash
   tail -20 /var/log/odoo/odoo.log | grep -E "provisioning email|sent successfully|error"
   ```

---

## 📝 POURQUOI CETTE ERREUR?

Les données dans Odoo sont de deux types:

1. **Code** (fichiers .py, .xml)
   - Stockés dans les fichiers du disque
   - Chargés au démarrage d'Odoo
   - **Vos corrections sont ici** ✓

2. **Données** (templates, configurations)
   - Stockées dans la base PostgreSQL
   - Créées une fois lors de l'installation du module
   - **Les anciens templates restaient ici** ❌

**Solution:** Supprimer les données obsolètes pour que les nouvelles soient créées.

---

## 💡 EXPLICATION TECHNIQUE

Le XML avec `noupdate="1"` signifie:
- Créer le template si n'existe pas ✓
- Ne pas mettre à jour si existe déjà ✗

Donc les anciens templates (avec `object.company_id`) restaient actifs même après modification du code.

**Fix:** Supprimer les enregistrements de la BD → Odoo les recrée avec les nouvelles données.

---

## ✨ STATUS APRÈS LA FIX

| Élément | Avant | Après |
|---------|-------|-------|
| **Code** | ✓ Corrigé | ✓ Corrigé |
| **Templates BD** | ❌ Anciens | ✅ Nouveaux |
| **Envoi email** | ❌ Erreur | ✅ Fonctionne |
| **Logs** | ❌ Error | ✅ Success |

---

## 🎯 PROCHAINES ÉTAPES

1. ✓ Code corrigé (déjà fait)
2. **→ Supprimer les anciens templates (À FAIRE)**
3. **→ Redémarrer Odoo (À FAIRE)**
4. **→ Mettre à jour le module (À FAIRE)**
5. **→ Tester l'envoi d'email (À FAIRE)**

---

## 📞 EN CAS DE PROBLÈME

**Erreur: psql: command not found**
```bash
# Installer psql
sudo apt-get install postgresql-client
```

**Erreur: Access denied**
```bash
# Utiliser le bon utilisateur
psql -U postgres -d dev -c "..."
```

**Module ne se met pas à jour**
```bash
# Forcer la réinstallation
Paramètres → Applications → SaaS Manager → Désinstaller puis Installer
```

---

**Suivez ces étapes et l'erreur sera résolue! ✅**

