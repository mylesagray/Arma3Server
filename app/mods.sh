#!/bin/bash
cd "/arma3/steamapps/workshop/content/107410/"
find . -depth -exec rename -v -E 's/(.*)\/([^\/]*)/$1\/\L$2/' {} \;
