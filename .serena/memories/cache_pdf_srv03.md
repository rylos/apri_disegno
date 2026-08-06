# Generazione delle cache .pdf_cache.txt su srv03 (2026-08-06)

`update_pdf_cache.sh` gira su **srv03** (Synology, `ssh -p 2222 admin@srv03`, utente `admin`,
**niente sudo**) e produce le cache lette da CLI e web app.

## Come e' schedulato
Task Scheduler DSM, voce `id=32` in `/etc/crontab` → **06:00 ogni giorno** (la cache risulta
scritta alle 06:03). Lo script vive in `/volume1/homes/admin/update_pdf_cache.sh`, copia del
file nel repo; backup della versione precedente in `update_pdf_cache.sh.bak-20260806`.

⚠️ **Non verificato quale path esegue davvero il task**: `synoschedtask` non e' nel PATH via ssh
e `/usr/syno/etc/synoschedtask.xml` richiede root. Da controllare in DSM se un giorno la cache
smette di aggiornarsi.

## Cosa genera
| share | filtro | voci |
|---|---|---|
| `/volume1/Elaborati_Tecnici` | `--changed-within 1y` | 23.841 (2,5 MB) |
| `/volume1/Elaborati_Tecnici_OLD` | nessuno (e' un archivio) | 558.013 (60,4 MB) |

Criterio: PDF che stanno in una cartella il cui **nome contiene "pdf"** (case-insensitive),
esclusi `#snapshot`, `@eaDir`, `#recycle`.

## Riscrittura del 2026-08-06 — cosa e' cambiato e perche'
1. **Una sola invocazione di fd per share**. Prima lo script lanciava `fd` **una volta per ogni
   cartella PDF trovata** (5.734 processi su Elaborati_Tecnici). Misurato a cache di filesystem
   calda e ripetuto: **62 s → 6 s**, con user+sys da 65 s a 18 s. A cache fredda il guadagno e'
   molto minore (81 s → 72 s) perche' li' domina l'I/O sui metadati: **non aspettarsi 10× in
   produzione alle 06:00**, il guadagno vero e' sul carico CPU.
   L'output e' stato verificato **identico riga per riga** a quello del vecchio metodo.
2. **Scrittura atomica** su `.tmp` + `mv`. Prima la redirezione `>` troncava `.pdf_cache.txt`
   all'avvio: per tutta la scansione (oltre un minuto) chi leggeva la cache trovava un file
   parziale o vuoto, e la web app se ne sarebbe portata dietro un indice vuoto per 8 ore.
3. **Cache vuota = si tiene la precedente**: una scansione fallita non deve cancellare la share
   dai risultati.
4. `PATH` esplicito nello script: `fd` sta in `/usr/local/bin/fd` (pacchetto SynoCli) e **non e'
   nel PATH di una ssh non interattiva**, anche se lo e' per cron.

## Trappole di fd (versione 10.3.0 su srv03)
- `--strip-cwd-prefix` **rifiuta di convivere con un argomento path**: va omesso il `.` finale e
  lasciato che fd usi la cwd. Senza, l'output ha il prefisso `./` e non combacia col vecchio.
- Il pattern `--full-path '/[^/]*pdf[^/]*/'` riproduce la semantica del vecchio `fd -t d -i pdf`
  (segmento di directory che *contiene* "pdf", non che si chiama esattamente "PDF").

## Trasferire file su srv03
**scp non funziona** (SFTP disabilitato su DSM): usare `ssh -p 2222 admin@srv03 'cat > dest' < file`.

Vedi anche `mem:web_app`, `mem:project_overview`.
