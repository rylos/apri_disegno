# Parco client Linux Mint (rilevato il 2026-08-06)

I client della CLI **non stanno in DNS e non rispondono al ping**: `nmap` senza `-Pn` non li trova.
Si individuano dai lease del DHCP Kea (`cd ~/dev/dhcp-kea && ./kea-cmd.sh leases`), poi
`nmap -Pn -p22 --open 192.168.0.0/23`.

| Host | IP | Note |
|---|---|---|
| pc-prod01 | 192.168.0.129 | 12 core, 11 GB |
| pc-prod02 | 192.168.1.163 | 4 core, 15 GB |
| prod04 | 192.168.1.131 | 4 core, 15 GB |
| mes4 | 192.168.0.235 | 4 core, 7 GB — postazione MES, ha comunque il client |

Nessun `prod03`: non compare né nei lease né nella scansione SSH.

## Configurazione comune
- Linux Mint 22.2, Python 3.12.3, schermo 1920x1080
- Accesso: `ssh prod@<ip>` con la chiave di marco (utente `prod`, **non** marco/root)
- App in `/home/prod/apri_disegno`, avviata da `apri_disegno_loop.sh` (untracked, generato da `install.sh`)
- `gnome-terminal --geometry=195x59+0+0`, riavvio automatico se chiusa
- Mount CIFS con `x-systemd.automount`: `mount | grep cifs` può non mostrarli finché non si accede al percorso — **non è un guasto**
- Aggiornamento: crontab utente `prod` → `0 6 * * * cd /home/prod/apri_disegno && git pull origin main`

## Problema noto: l'aggiornamento automatico salta i PC accesi dopo le 6:00
`/etc/cron.daily` **non contiene nulla** per apri_disegno: l'anacron citato nel README non è installato.
Se il PC non è acceso alle 6:00 in punto, quel giorno non aggiorna e non recupera mai.
Stato dei fetch rilevato il 2026-08-06: pc-prod01 e mes4 aggiornati in giornata, prod04 fermo al 2026-07-21,
**pc-prod02 fermo al 2026-03-04** (5 mesi).

Conseguenza pratica: il canale git funziona (fetch verso GitHub OK da tutti e quattro, unico file locale
non tracciato è `apri_disegno_loop.sh`, quindi il pull non va mai in conflitto), ma **non si può dare per
scontato che una modifica alla CLI arrivi a tutti**. Verificare host per host dopo ogni release.
