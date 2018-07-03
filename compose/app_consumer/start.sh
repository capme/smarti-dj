#!/bin/bash
/app/chkinstreq.sh
supervisord -c /etc/supervisord.conf
