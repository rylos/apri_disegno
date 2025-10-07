#!/bin/bash

# Script installazione apri_disegno per Linux Mint
# Eseguire con: sudo ./install.sh

set -e

echo "=== Installazione apri_disegno ==="

# Verifica esecuzione come root
if [[ $EUID -ne 0 ]]; then
   echo "Errore: Eseguire come root (sudo ./install.sh)"
   exit 1
fi

# Verifica utente prod
if ! id "prod" &>/dev/null; then
    echo "Errore: Utente 'prod' non trovato"
    exit 1
fi

# Clona repository se non esiste
if [ ! -d "/home/prod/apri_disegno" ]; then
    echo "Clonazione repository..."
    cd /home/prod
    sudo -u prod git clone https://github.com/rylos/apri_disegno.git
    chown -R prod:prod /home/prod/apri_disegno
else
    echo "Repository già presente, aggiornamento..."
    cd /home/prod/apri_disegno
    sudo -u prod git pull
fi

# Crea directory mount points
echo "Creazione mount points..."
mkdir -p /mnt/srv01/DB_DISEGNI
mkdir -p /mnt/srv03/elaborati_tecnici

# Crea directory samba
mkdir -p /etc/samba

# Copia credenziali samba
echo "Configurazione credenziali samba..."
cp /home/prod/apri_disegno/etc/samba/credenziali /etc/samba/credenziali
chmod 600 /etc/samba/credenziali
chown root:root /etc/samba/credenziali

# Backup fstab
cp /etc/fstab /etc/fstab.backup.$(date +%Y%m%d_%H%M%S)

# Aggiunge righe fstab se non presenti
echo "Configurazione fstab..."
if ! grep -q "srv01.liftingitalia.local" /etc/fstab; then
    echo "" >> /etc/fstab
    cat /home/prod/apri_disegno/etc/fstab.add.txt >> /etc/fstab
    echo "Righe fstab aggiunte"
else
    echo "Righe fstab già presenti"
fi

# Installa dipendenze
echo "Installazione dipendenze..."
apt update
apt install -y cifs-utils python3

# Rende eseguibile il programma
chmod +x /home/prod/apri_disegno/apri_disegno.py

# Crea wrapper per riavvio automatico
cat > /home/prod/apri_disegno/apri_disegno_loop.sh << 'EOF'
#!/bin/bash
while true; do
    cd /home/prod/apri_disegno
    gnome-terminal --geometry=182x59+0+0 --hide-menubar --wait -- python3 apri_disegno.py
    sleep 0.1
done
EOF
chmod +x /home/prod/apri_disegno/apri_disegno_loop.sh
chown prod:prod /home/prod/apri_disegno/apri_disegno_loop.sh

# Crea icona desktop per utente prod
echo "Creazione icona desktop..."
cat > /home/prod/Scrivania/apri_disegno.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Apri Disegno
Comment=Ricerca e apertura disegni PDF
Exec=/home/prod/apri_disegno/apri_disegno_loop.sh
Icon=applications-engineering
Terminal=false
Categories=Office;Engineering;
StartupNotify=true
EOF

chmod +x /home/prod/Scrivania/apri_disegno.desktop
chown prod:prod /home/prod/Scrivania/apri_disegno.desktop

# Crea icona MES Qualitas
cat > /home/prod/Scrivania/qualitas.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=MES Qualitas
Comment=Sistema MES Qualitas
Exec=xdg-open http://mes2.liftingitalia.local:81/QualitasWebClient/Account/Login
Icon=applications-internet
Terminal=false
Categories=Network;WebBrowser;
StartupNotify=true
EOF

chmod +x /home/prod/Scrivania/qualitas.desktop
chown prod:prod /home/prod/Scrivania/qualitas.desktop

# Crea icona Elaborati Tecnici
cat > /home/prod/Scrivania/elaborati_tecnici.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Elaborati Tecnici
Comment=Cartella elaborati tecnici di rete
Exec=xdg-open /mnt/srv03/elaborati_tecnici
Icon=folder-documents
Terminal=false
Categories=System;FileManager;
StartupNotify=true
EOF

chmod +x /home/prod/Scrivania/elaborati_tecnici.desktop
chown prod:prod /home/prod/Scrivania/elaborati_tecnici.desktop

# Configura avvio automatico
mkdir -p /home/prod/.config/autostart
cp /home/prod/Scrivania/apri_disegno.desktop /home/prod/.config/autostart/
chown -R prod:prod /home/prod/.config/autostart

# Test mount
echo "Test mount..."
systemctl daemon-reload
if ! mount | grep -q "srv01.liftingitalia.local"; then
    mount /mnt/srv01/DB_DISEGNI 2>/dev/null || echo "Mount srv01 già presente o non disponibile"
fi
if ! mount | grep -q "srv03.liftingitalia.local"; then
    mount /mnt/srv03/elaborati_tecnici 2>/dev/null || echo "Mount srv03 già presente o non disponibile"
fi

# Configura cron per aggiornamento giornaliero
echo "Configurazione aggiornamento automatico..."
if ! crontab -u prod -l 2>/dev/null | grep -q "git pull origin main"; then
    (crontab -u prod -l 2>/dev/null; echo "0 6 * * * cd /home/prod/apri_disegno && git pull origin main >/dev/null 2>&1") | crontab -u prod -
    echo "Cron job aggiunto"
else
    echo "Cron job già presente"
fi

# Configura anacron per recupero se PC spento
mkdir -p /etc/anacrontab.d
cat > /etc/anacrontab.d/apri_disegno << 'EOF'
1	5	apri_disegno_update	sudo -u prod bash -c "cd /home/prod/apri_disegno && git pull origin main >/dev/null 2>&1"
EOF

echo "=== Installazione completata ==="
echo "Eseguire: cd /home/prod/apri_disegno && python3 apri_disegno.py"
echo "Aggiornamento automatico: ogni giorno alle 6:00 (anacron se PC spento)"