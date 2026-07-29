# Week 4 - Setup Config - July 19 - Sunaina
# Package setup for PyChronicle CLI

setup_config = {
    'name': 'pychronicle',
    'version': '1.0.0',
    'description': 'AST-Powered Time-Travel Debugger',
    'author': 'Infotact Advanced Python Team',
    'commands': {
        'pychronicle run': 'Trace a Python script',
        'pychronicle history': 'Show execution history',
        'pychronicle watch': 'Watch a specific variable',
    },
    'dependencies': [
        'textual',
        'rich',
        'click',
        'cloudpickle'
    ]
}

def display_config():
    print("=== PyChronicle Package Config ===")
    for key, val in setup_config.items():
        if isinstance(val, dict):
            print(f"\n{key}:")
            for k, v in val.items():
                print(f"  {k}: {v}")
        elif isinstance(val, list):
            print(f"\n{key}: {', '.join(val)}")
        else:
            print(f"{key}: {val}")

if __name__ == "__main__":
    display_config()