#!/bin/bash
find /arma3/ -depth -exec rename 's/(.*)\/([^\/]*)/$1\/\L$2/' {} \;