# Portare un PC clonato Clonezilla all'ultima release

I PC di produzione non vengono installati da zero: si ripristina un'**immagine Clonezilla** che
contiene una versione vecchia del progetto e le configurazioni sbagliate descritte sotto.
Un PC appena clonato **non è pronto**: va sempre eseguita questa procedura.

Contesto sul parco macchine, accessi e catena di avvio: [[client_linux_mint]].

## Cosa c'è di sbagliato nell'immagine (verificato il 2026-08-06)
1. **Codice fermo** alla release presente al momento della cattura (ricerche 1,3-1,6 s invece di ~1 ms).
2. **Aggiornamento automatico rotto**: cron utente alle 6:00 + un file in `/etc/anacrontab.d/`,
   directory che **anacron non legge** su Debian/Ubuntu. Se il PC non è acceso alle 6:00 in punto,
   non aggiorna mai e non recupera.
3. **Chiave host SSH condivisa**: tutte e quattro le macchine presentano la stessa
   `ssh_host_ed25519_key` (`SHA256:oqhbVztBZNmi1HTdK…`), clonata e mai rigenerata. Conseguenza:
   `ssh` non segnala nulla se ci si collega al PC sbagliato, e la chiave privata è la stessa ovunque.
   Il `machine-id` invece risulta già rigenerato correttamente.
4. **Residui di cache** dell'immagine (`.pdf_index.json`, `.cache_timestamp`, `.last_pull`) che
   riferiscono uno stato non più valido.

## Procedura (in ordine)

### 1. Hostname univoco — farlo per primo
```bash
sudo hostnamectl set-hostname pc-prodNN        # NN = numero libero, verificarlo prima
sudo sed -i "s/\b<vecchio-nome>\b/pc-prodNN/g" /etc/hosts
```
Verificare che il nome non sia già in uso: `cd ~/dev/dhcp-kea && ./kea-cmd.sh leases | grep -i prod`.
Al 2026-08-06 esistono pc-prod01, pc-prod02, prod04, mes4 — **la numerazione salta il 3, prod03 non esiste**.
Un clone che tiene il nome dell'originale crea due host con lo stesso nome su IP diversi.

### 2. Rigenerare la chiave host SSH
```bash
sudo rm -f /etc/ssh/ssh_host_*
sudo ssh-keygen -A
sudo systemctl restart ssh
```
Poi da pc-work: `ssh-keygen -R <ip>` prima di ricollegarsi, altrimenti `known_hosts` segnala conflitto.

### 3. Aggiornare l'applicazione
```bash
cd /home/prod/apri_disegno
sudo -u prod git pull origin main
sudo ./install.sh
```
`install.sh` è **idempotente** e sicuro da rilanciare su un clone: fa `git pull` se il repo esiste,
aggiunge le righe fstab solo se assenti, riscrive wrapper e icone, e soprattutto configura il
**timer systemd** `apri-disegno-update.timer` rimuovendo cron e `/etc/anacrontab.d/apri_disegno`.

### 4. Pulire i residui dell'immagine
```bash
rm -f /home/prod/apri_disegno/.pdf_index.json \
      /home/prod/apri_disegno/.cache_timestamp \
      /home/prod/apri_disegno/.last_pull
```

### 5. Riavviare l'app
```bash
pkill -f "python3 apri_disegno.py"
```
Non spegne nulla: il wrapper riapre la finestra in 100 ms con il codice nuovo.

## Verifica finale
```bash
cd /home/prod/apri_disegno
git log -1 --format='%h %ad' --date=short                    # deve coincidere con origin/main
XDG_RUNTIME_DIR=/run/user/$(id -u) systemctl --user list-timers apri-disegno-update.timer
crontab -l | grep -c apri_disegno                            # deve essere 0
ls -la /etc/anacrontab.d/apri_disegno 2>&1                   # deve essere assente
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub             # deve differire dagli altri PC
python3 -c "
import time, importlib.util
s=importlib.util.spec_from_file_location('ad','/home/prod/apri_disegno/apri_disegno.py')
ad=importlib.util.module_from_spec(s); s.loader.exec_module(ad)
b=ad.get_network_path(); ad._index=ad.load_index(b)
t=time.perf_counter(); r,_=ad.cerca(b,'F353.01')
print('%d risultati in %.1f ms, indice %d disegni' % (len(r),(time.perf_counter()-t)*1000,len(ad._index['db'])))"
```
L'ultimo comando deve stampare una ricerca **in millisecondi**: se impiega più di un secondo l'indice
non sta funzionando e il PC sta girando col codice vecchio.

## Quando conviene rifare l'immagine
L'immagine attuale è antecedente al 2026-08-06. Rifarla dopo aver applicato questa procedura su una
macchina di riferimento **evita i punti 2, 3 e 4** ai cloni futuri. Prima della cattura:
`sudo rm -f /etc/ssh/ssh_host_*` e `sudo truncate -s 0 /etc/machine-id`, così ogni clone se li
rigenera al primo avvio invece di ereditarli identici.
