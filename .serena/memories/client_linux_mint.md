# Parco client Linux Mint — inventario e funzionamento (2026-08-06)

## Come trovarli
**Non stanno in DNS e non rispondono al ping**: `nmap` senza `-Pn` non li vede, e non compaiono
nelle sessioni SMB di srv01 (i mount sono automount, si attivano solo all'uso).

```bash
cd ~/dev/dhcp-kea && ./kea-cmd.sh leases | grep -iE "prod|mes"   # lease Kea = fonte affidabile
nmap -Pn -p22 --open 192.168.0.0/23                              # -Pn obbligatorio
ssh prod@<ip>                                                     # utente prod, NON marco/root
```

| Host | IP | MAC WiFi | Hardware |
|---|---|---|---|
| pc-prod01 | 192.168.0.129 | 9c:c7:d3:b8:6a:9a | 12 core, 11 GB |
| pc-prod02 | 192.168.1.163 | 24:eb:16:c6:5f:07 | 4 core, 15 GB |
| prod04 | 192.168.1.131 | b8:f7:75:b8:00:56 | 4 core, 15 GB |
| mes4 | 192.168.0.235 | 34:6f:24:54:4d:9b | 4 core, 7 GB — postazione MES, ha comunque il client |

Tutti Linux Mint 22.2, Python 3.12.3, Cinnamon, schermo 1920x1080.
Tutti connessi **via WiFi**: la scheda cablata (`enp1s0`, MAC `78:55:36:*`) esiste ma non è usata
e non ha mai preso un lease.

**Non esiste un prod03**: nessun lease, nessun host in rete, nessun hostname duplicato tra i quattro
(gli unici nomi duplicati nei lease sono notebook con cavo+WiFi). La numerazione salta semplicemente il 3.

I PC sono costruiti ripristinando un'**immagine Clonezilla** che contiene una release vecchia e
configurazioni da correggere: procedura di allineamento in [[clonezilla_aggiornamento_client]].

## Come funziona l'avvio (catena completa)
1. **Autostart**: `~/.config/autostart/apri_disegno.desktop` → esegue `apri_disegno_loop.sh` al login
   della sessione Cinnamon (`Terminal=false`, quindi nessuna finestra propria).
2. **Wrapper `/home/prod/apri_disegno/apri_disegno_loop.sh`** (generato da `install.sh`, **untracked**):
   ciclo `while true` infinito che lancia
   `gnome-terminal --geometry=195x59+0+0 --hide-menubar --wait -- python3 apri_disegno.py`.
   `--wait` fa sì che il ciclo resti fermo finché la finestra è aperta; alla chiusura riparte dopo
   `sleep 0.1`. **È questo il motivo per cui l'app "non si può chiudere"**: l'utente chiude la
   finestra e questa si riapre in 100 ms in alto a sinistra.
   Dal 2026-08-06 il wrapper fa anche `git pull` prima di riaprire, se l'ultimo è più vecchio di 4 h
   (marcatore `.last_pull`), così una nuova versione entra in funzione alla prima riapertura.
3. **Icone in `~/Scrivania`** (non `~/Desktop`, sistema in italiano):
   `apri_disegno.desktop` (stesso wrapper), `elaborati_tecnici.desktop` (`xdg-open /mnt/srv03/...`),
   `MES.desktop` (link a SFC PRODUZIONE).
4. **Mount CIFS** da `/etc/fstab` con `x-systemd.automount,x-systemd.idle-timeout=60`:
   si montano **su richiesta** e si smontano dopo 60 s di inattività. `mount | grep cifs` che non
   li mostra **non è un guasto**. Credenziali in `/etc/samba/credenziali` (utente `prod` del dominio).

## Aggiornamento automatico
Timer systemd **utente** `apri-disegno-update.timer` (`~/.config/systemd/user/`):
`OnCalendar=*-*-* 06:00:00`, `Persistent=true`, `RandomizedDelaySec=300`.

```bash
XDG_RUNTIME_DIR=/run/user/$(id -u) systemctl --user list-timers apri-disegno-update.timer
```

**Storia del bug (non ripeterlo)**: prima c'erano un cron utente alle 6:00 più un file in
`/etc/anacrontab.d/`. Quella directory **non viene letta da anacron** su Debian/Ubuntu, quindi il
recupero non è mai esistito: i PC accesi dopo le 6:00 non si aggiornavano mai. Rilevato il 2026-08-06:
pc-prod02 era fermo a 5 mesi prima, prod04 a 16 giorni. Il cron è stato rimosso, sostituito dal timer.

## Aggiornare i client a mano
```bash
for ip in 192.168.0.129 192.168.1.163 192.168.1.131 192.168.0.235; do
  ssh prod@$ip 'cd /home/prod/apri_disegno && git pull --quiet origin main && pkill -f "python3 apri_disegno.py"'
done
```
`pkill` non spegne nulla: il wrapper riapre la finestra in 100 ms con il codice nuovo. Va fatto,
altrimenti il processo in esecuzione continua con la versione vecchia in memoria.

L'unico file locale non tracciato è `apri_disegno_loop.sh` (più `.pdf_index.json` e `.last_pull`,
entrambi in `.gitignore`), quindi **il pull non va mai in conflitto**.
