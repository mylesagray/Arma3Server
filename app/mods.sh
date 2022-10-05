#!/bin/bash
mkdir -p "/arma3/steamapps/workshop/content/107410/"
cd "/arma3/steamapps/workshop/content/107410/"
# extensive use of bash string manipulation:
# ##*/ returns everything beyond the last /
# %/* returns drops everything beyond the last /
# ${STRING,,} returns a lowercase $STRING
find . -depth -exec /bin/bash -c 'PATH="{}"; FILE=${PATH##*/}; if [ "$FILE" != "${FILE,,}" ]; then /bin/mv "$PATH" "${PATH%/*}/${FILE,,}"; echo "$PATH --> ${PATH%/*}/${FILE,,}";fi' \;