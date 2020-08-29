import psutil

from gullveig.agent.modules import get_int_marker_for_percentage, get_resource_remaining_percent


def key():
    return 'mod_res'


def supports():
    return True


def get_report(config):
    swap = psutil.swap_memory()
    swap_percent = get_resource_remaining_percent(swap.used, swap.total)
    memory = psutil.virtual_memory()
    memory_percent = get_resource_remaining_percent(memory.used, memory.total)
    cpu_freq = psutil.cpu_freq()
    cpu_load = psutil.cpu_percent(None, False)

    report = {
        'meta': {},
        'metric': [
            {
                's': 'swap',
                'm': 'used',
                'v': swap.used,
                'f': 0,
                't': swap.total,
                'd': 'b'
            },
            {
                's': 'mem',
                'm': 'used',
                'v': memory.used,
                'f': 0,
                't': memory.total,
                'd': 'b'
            },
            {
                's': 'mem',
                'm': 'shared',
                'v': memory.shared,
                'f': 0,
                't': memory.total,
                'd': 'b'
            },
            {
                's': 'mem',
                'm': 'buff',
                'v': memory.buffers,
                'f': 0,
                't': memory.total,
                'd': 'b'
            },
            {
                's': 'cpu',
                'm': 'freq',
                'v': cpu_freq.current,
                'f': cpu_freq.min,
                't': cpu_freq.max,
                'd': 'GHz'
            },
            {
                's': 'cpu',
                'm': 'load',
                'v': cpu_load,
                'f': 0,
                't': 100,
                'd': '%'
            }
        ],
        'status': [
            {
                's': 'swap',
                't': 'used',
                'r': swap_percent,
                'st': get_int_marker_for_percentage(swap_percent, 30, 10) if swap.total > 0 else 0,  # Sigh...
                'm': True
            },
            {
                's': 'mem',
                't': 'used',
                'r': memory_percent,
                'st': get_int_marker_for_percentage(memory_percent, 10, 5),
                'm': True
            },
            {
                's': 'cpu',
                't': 'load',
                'r': cpu_load,
                'st': get_int_marker_for_percentage(100 - cpu_load, 10, 5),
                'm': True
            },
        ]
    }

    return report
