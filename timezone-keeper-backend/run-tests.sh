#!/bin/bash

PROJECT_ROOT_DIR="$(dirname $( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd ))"
SCRIPT_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# run component and unit tests
DOCOLOR="${DOCOLOR:-0}"
txtred=
txtgrn=
txtylw=
txtrst=


if [ ${DOCOLOR} -eq 1 ]
then
  txtred=$(tput setaf 1)    # Red
  txtgrn=$(tput setaf 2)    # Green
  txtylw=$(tput setaf 3)    # Yellow
  txtrst=$(tput sgr0)       # Text reset
fi

SUCCESS="${txtgrn}[SUCCESS]${txtrst}"
FAILURE="${txtred}[FAILURE]${txtrst}"
WARNING="${txtylw}[WARNING]${txtrst}"

export success=0
export failure=0
export warning=0

function checkreturn {
    if [ $? -eq 0 ] ; then
        success=`expr $success + 1`
        echo "${SUCCESS}"
    else
        failure=`expr $failure + 1`
        echo "${FAILURE}"
    fi
}

function cleanup {
    #no cleanup actions for now
    exit ${failure}
}

# Catch ctrl-c to perform any cleanup necessary
trap cleanup INT


echo ""
echo "------------- TEST: Running unit tests."

nosetests -s test/test_user_api.py
checkreturn


echo ""
echo "------------- SUMMARY"
echo "${txtgrn}Success: ${success}${txtrst}"
echo "${txtred}Failure: ${failure}${txtrst}"
echo "${txtylw}Warning: ${warning}${txtrst}"

cleanup
