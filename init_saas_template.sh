#!/bin/bash
#
# Script d'initialisation de template SaaS
# SaaS Template Initialization Script
#
# Usage: ./init_saas_template.sh <db_name> [modules]
#

set -e

# Couleurs pour l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ODOO_HOME="/opt/GetapERP/GetapERP-V18/odoo"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-getappro}"
DB_PASSWORD="${DB_PASSWORD:-Hr@f066133663}"
MODULES="${2:-base,web,mail,portal}"
DB_NAME="$1"

# Vérification des paramètres
if [ -z "$DB_NAME" ]; then
    echo -e "${RED}Error: Database name required${NC}"
    echo "Usage: $0 <db_name> [modules]"
    echo "Example: $0 template_restaurant 'base,web,mail,portal,sale,stock'"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}SaaS Template Initialization${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo "  Database: $DB_NAME"
echo "  Host: $DB_HOST:$DB_PORT"
echo "  User: $DB_USER"
echo "  Modules: $MODULES"
echo ""

# Vérifier que PostgreSQL est accessible
echo -e "${YELLOW}[1/4] Checking PostgreSQL connection...${NC}"
if ! psql -h "$DB_HOST" -U "$DB_USER" -d postgres -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${RED}Error: Cannot connect to PostgreSQL${NC}"
    echo "Please check:"
    echo "  - PostgreSQL is running"
    echo "  - DB_HOST=$DB_HOST"
    echo "  - DB_USER=$DB_USER"
    echo "  - DB_PASSWORD is correct"
    exit 1
fi
echo -e "${GREEN}✓ PostgreSQL connection OK${NC}"
echo ""

# Vérifier que odoo-bin existe
echo -e "${YELLOW}[2/4] Checking Odoo installation...${NC}"
if [ ! -f "$ODOO_HOME/odoo-bin" ]; then
    echo -e "${RED}Error: odoo-bin not found at $ODOO_HOME/odoo-bin${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Odoo binary found${NC}"
echo ""

# Vérifier que la base n'existe pas déjà
echo -e "${YELLOW}[3/4] Checking if database already exists...${NC}"
if psql -h "$DB_HOST" -U "$DB_USER" -d postgres -c "SELECT datname FROM pg_database WHERE datname='$DB_NAME';" 2>/dev/null | grep -q "$DB_NAME"; then
    echo -e "${RED}Error: Database '$DB_NAME' already exists${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Database does not exist (OK)${NC}"
echo ""

# Lancer l'initialisation
echo -e "${YELLOW}[4/4] Initializing Odoo database...${NC}"
echo "This may take a few minutes..."
echo ""

cd "$ODOO_HOME"

# Exporter l'environnement
export PYTHONPATH="$ODOO_HOME:$PYTHONPATH"
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# Lancer odoo-bin
if python odoo-bin \
    -d "$DB_NAME" \
    -i "$MODULES" \
    --without-demo=all \
    --stop-after-init \
    --db_host "$DB_HOST" \
    --db_port "$DB_PORT" \
    --db_user "$DB_USER" \
    --db_password "$DB_PASSWORD" \
    --logfile=/tmp/odoo_init_${DB_NAME}.log; then

    echo -e "${GREEN}✓ Database initialization completed${NC}"
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}SUCCESS!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Template database created successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Access the database:"
    echo "     URL: http://localhost:8069/web?db=$DB_NAME"
    echo "  2. Configure the template as needed"
    echo "  3. Mark it as ready in SaaS Manager"
    echo ""

    # Afficher les logs s'il y a des erreurs
    if grep -i "error\|warning" /tmp/odoo_init_${DB_NAME}.log | head -5; then
        echo -e "${YELLOW}Warnings/Errors detected (see log file):${NC}"
        echo "  /tmp/odoo_init_${DB_NAME}.log"
    fi

else
    echo -e "${RED}✗ Database initialization failed${NC}"
    echo ""
    echo "Check the log file for details:"
    echo "  /tmp/odoo_init_${DB_NAME}.log"
    echo ""
    echo "Common errors:"
    echo "  - ModuleNotFoundError: Install missing packages with: pip install -r requirements.txt"
    echo "  - Permission denied: Check PostgreSQL user permissions"
    echo "  - Connection refused: Check PostgreSQL is running"
    exit 1
fi

