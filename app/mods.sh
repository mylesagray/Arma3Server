#!/bin/bash
find /arma3/steamapps/workshop/content/107410 -depth -exec rename 's/(.*)\/([^\/]*)/$1\/\L$2/' {} \;
