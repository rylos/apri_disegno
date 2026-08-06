# Comandi Suggeriti

## CLI
```bash
python3 apri_disegno.py
python3 -m py_compile apri_disegno.py      # verifica sintassi
```

## Web (sviluppo locale)
```bash
cd apri_disegno_web
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py                               # dev server su :5000
```

## Deploy web in produzione (docker.liftingitalia.local:5000)
```bash
# 1. backup + tag di rollback
# ATTENZIONE: l'immagine in uso e' apri_disegno_web-apri_disegno_web:latest (nome generato da
# compose). apri_disegno_web:latest esiste ancora ma e' un residuo vecchio: taggare quella
# darebbe un rollback verso un'immagine mai in produzione.
ssh root@docker 'cp -a /docker/apri_disegno_web /docker/apri_disegno_web.bak-$(date +%Y%m%d) && \
                 docker tag apri_disegno_web-apri_disegno_web:latest \
                            apri_disegno_web-apri_disegno_web:rollback-$(date +%Y%m%d)'

# 2. sync (MAI includere .env: contiene le credenziali Samba)
rsync -az --delete --exclude venv/ --exclude __pycache__/ --exclude .env \
      --exclude flask.log --exclude .git/ \
      apri_disegno_web/ root@docker:/docker/apri_disegno_web/

# 3. rebuild
ssh root@docker 'cd /docker/apri_disegno_web && docker compose up -d --build'

# 4. verifica
ssh root@docker 'curl -s http://localhost:5000/stats; curl -s -X POST -d "search_term=F353" http://localhost:5000/search | head -c 300'
```

Rollback: ripristinare `/docker/apri_disegno_web.bak-<data>` (contiene anche il docker-compose.yml
funzionante) e `docker compose up -d`.

⚠️ **Un volume CIFS che non monta impedisce l'avvio dell'intero container**, non degrada solo
quella fonte: prima di aggiungere un volume nuovo, verificare l'accesso con
`smbclient //srv03.liftingitalia.local/<share> -U prod%<pass> -c ls`.

## Installazione client Linux Mint
```bash
git clone https://github.com/rylos/apri_disegno.git && cd apri_disegno
sudo ./install.sh
```

## Script cache server (srv03) — vedi `mem:cache_pdf_srv03`
Gira via Task Scheduler DSM alle 06:00 e genera **due** cache (correnti + archivio storico).

```bash
# esecuzione manuale (dura alcuni minuti: l'archivio ha 558.000 PDF)
ssh -p 2222 admin@srv03 'bash /volume1/homes/admin/update_pdf_cache.sh'

# stato delle due cache
ssh -p 2222 admin@srv03 'ls -la /volume1/Elaborati_Tecnici/.pdf_cache.txt \
                                /volume1/Elaborati_Tecnici_OLD/.pdf_cache.txt'

# aggiornare lo script sul NAS: scp NON funziona (SFTP disabilitato su DSM)
ssh -p 2222 admin@srv03 'cat > /volume1/homes/admin/update_pdf_cache.sh' < update_pdf_cache.sh
```

## Debug e troubleshooting
```bash
ls -la /mnt/srv01/DB_DISEGNI/
ls -la /mnt/srv03/elaborati_tecnici/.pdf_cache.txt
grep -i "codice" /mnt/srv03/elaborati_tecnici/.pdf_cache.txt
cat .cache_timestamp                        # timestamp cache CLI
mount | grep cifs
systemctl status mnt-srv01-DB_DISEGNI.automount
systemctl status mnt-srv03-elaborati_tecnici.automount
ls -la /home/prod/Scrivania/*.desktop
```

## Qualità codice (opzionali, non installati di default)
```bash
black apri_disegno.py
ruff check apri_disegno.py
mypy apri_disegno.py
```

## Git
```bash
git status && git diff
git add -A && git commit -m "Descrizione modifiche"
git push origin main
```
