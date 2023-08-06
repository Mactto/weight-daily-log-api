#!/bin/bash

python -m ebc.worker_manager - <<'EOF'
worker_config = {
    'nginx': {
        'num_workers': 1,
        'cmd': [
            '/usr/sbin/nginx',
            '-g',
            'daemon off;'
        ],
        'start_condition_cmd': [
            '/usr/bin/curl',
            '-sf',
            'http://127.0.0.1:16824/_ping'
        ],
        'stop_signal': 'SIGQUIT',
        'stop_order': 1
    },
    'app-server': {
        'num_workers': 1,
        'cmd': [
            '/bin/bash',
            'run.sh'
        ],
        'stop_order': 2,
        'signal_to_pg': True
    }
}
EOF
