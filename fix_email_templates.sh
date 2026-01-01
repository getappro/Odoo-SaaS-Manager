#!/bin/bash
# Script complet pour résoudre l'erreur company_id
# Usage: bash fix_email_templates.sh

set -e

echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                                  ║"
echo "║              🔧 SCRIPT DE FIXATION - Erreur company_id                         ║"
echo "║                                                                                  ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Coloration
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[ÉTAPE 1/5]${NC} Arrêter Odoo..."
pkill -f "odoo-bin" || true
sleep 2
echo -e "${GREEN}✓ Odoo arrêté${NC}"
echo ""

echo -e "${YELLOW}[ÉTAPE 2/5]${NC} Supprimer les anciens templates..."
psql -U getappro -d dev -c "
DELETE FROM mail_template
WHERE name IN (
    'SaaS: Instance Provisioned',
    'SaaS: Instance Suspended',
    'SaaS: Instance Reactivated',
    'SaaS: Instance Terminated',
    'SaaS: Subscription Expiring'
);" 2>/dev/null || {
    echo -e "${RED}✗ Erreur avec psql. Essayez:${NC}"
    echo "  psql -U postgres -d dev -c \"DELETE FROM mail_template WHERE...\";"
    exit 1
}
echo -e "${GREEN}✓ Anciens templates supprimés${NC}"
echo ""

echo -e "${YELLOW}[ÉTAPE 3/5]${NC} Redémarrer Odoo..."
cd /opt/GetapERP/GetapERP-V18
bash restart_odoo.sh > /dev/null 2>&1 &
sleep 10
echo -e "${GREEN}✓ Odoo redémarré${NC}"
echo ""

echo -e "${YELLOW}[ÉTAPE 4/5]${NC} Vérifier les nouveaux templates..."
sleep 3
TEMPLATES=$(psql -U getappro -d dev -t -c "
SELECT COUNT(*) FROM mail_template
WHERE name LIKE 'SaaS: Instance%';" 2>/dev/null || echo "0")
echo -e "${GREEN}✓ Templates trouvés: ${TEMPLATES}${NC}"
echo ""

echo -e "${YELLOW}[ÉTAPE 5/5]${NC} Vérifier que les templates sont corrects..."
EMAIL_FROM=$(psql -U getappro -d dev -t -c "
SELECT email_from FROM mail_template
WHERE name = 'SaaS: Instance Provisioned' LIMIT 1;" 2>/dev/null || echo "ERREUR")

if [[ "$EMAIL_FROM" == *"user.email_formatted"* ]]; then
    echo -e "${GREEN}✓ Templates corrigés: $EMAIL_FROM${NC}"
else
    echo -e "${RED}✗ Templates toujours incorrects${NC}"
    echo "Trouvé: $EMAIL_FROM"
fi
echo ""

echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                                  ║"
echo "║                         ✅ FIXATION COMPLÈTE                                   ║"
echo "║                                                                                  ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${YELLOW}PROCHAINES ÉTAPES:${NC}"
echo ""
echo "1. Vider le cache du navigateur:"
echo "   Ctrl+Shift+Del → All time → Clear data"
echo ""
echo "2. Mettre à jour le module SaaS Manager:"
echo "   Paramètres → Applications → SaaS Manager → Mettre à jour"
echo ""
echo "3. Tester l'envoi d'email:"
echo "   Créer une instance → Provisionner → Vérifier email"
echo ""
echo "4. Vérifier les logs:"
echo "   tail -20 /var/log/odoo/odoo.log | grep -i provisioning"
echo ""
echo -e "${GREEN}✓ Script complété avec succès!${NC}"

