#!/bin/bash
cd /volume1/Elaborati_Tecnici/
fd -t d -i pdf -E "#snapshot" -E "@eaDir" -E "#recycle" | while read dir; do
    fd -t f -e pdf --changed-within 1y . "$dir"
done > /volume1/Elaborati_Tecnici/.pdf_cache.txt 2>/dev/null
