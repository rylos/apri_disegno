#!/bin/bash
# Genera le cache dei PDF per la ricerca disegni (gira su srv03, Task Scheduler DSM).
#
# Una sola invocazione di fd per share: la versione precedente lanciava un fd per
# ogni cartella PDF trovata (5.734 processi su Elaborati_Tecnici, 81 s contro 6 s).
# Scrittura atomica su file temporaneo: con la redirezione diretta la cache restava
# troncata per tutta la durata della scansione, e chi la leggeva in quella finestra
# si ritrovava un indice vuoto.

set -u

PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export PATH

# Solo i PDF che stanno in una cartella il cui nome contiene "pdf" (case-insensitive):
# e' lo stesso criterio delle altre due fonti dell'applicazione.
PDF_DIR_RE='/[^/]*pdf[^/]*/'

EXCLUDES=(-E '#snapshot' -E '@eaDir' -E '#recycle')

# Genera la cache di una share.
#   $1 = percorso share, $2..= argomenti extra per fd (es. filtro data)
build_cache() {
    local share="$1"; shift
    local out="$share/.pdf_cache.txt"
    local tmp="$out.tmp"

    if [ ! -d "$share" ]; then
        echo "share assente, salto: $share" >&2
        return 1
    fi

    cd "$share" || return 1

    # Nessun path esplicito: fd usa la cwd, ed e' l'unico modo di avere
    # --strip-cwd-prefix (che rifiuta di convivere con un argomento path)
    if ! fd -t f -e pdf -i --full-path "$PDF_DIR_RE" --strip-cwd-prefix \
            "${EXCLUDES[@]}" "$@" > "$tmp" 2>/dev/null; then
        echo "scansione fallita: $share" >&2
        rm -f "$tmp"
        return 1
    fi

    # Una cache vuota nasconderebbe l'intera share: meglio tenere la precedente
    if [ ! -s "$tmp" ]; then
        echo "scansione vuota, cache precedente conservata: $share" >&2
        rm -f "$tmp"
        return 1
    fi

    chmod 666 "$tmp" 2>/dev/null
    mv -f "$tmp" "$out"
    echo "$(wc -l < "$out") PDF in $share"
}

# Elaborati tecnici correnti: solo i PDF toccati nell'ultimo anno, come da sempre
build_cache /volume1/Elaborati_Tecnici --changed-within 1y

# Archivio storico: nessun filtro data, per definizione non viene piu' modificato
build_cache /volume1/Elaborati_Tecnici_OLD
