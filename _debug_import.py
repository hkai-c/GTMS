import sys, importlib, os
sys.path.insert(0, '.')

for key in list(sys.modules.keys()):
    if 'server' in key:
        del sys.modules[key]

import server.schemas
print('server.schemas loaded OK')

spec = importlib.util.find_spec('server.schemasification_schema')
print('find_spec:', spec)

pkg = sys.modules['server.schemas']
print('__path__:', pkg.__path__)

for f in sorted(os.listdir(pkg.__path__[0])):
    if f.endswith('.py'):
        print(f'  {f}')
