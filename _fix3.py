import pathlib

def add(p, old, new):
    c = p.read_text('utf-8')
    c = c.replace(old, new)
    p.write_text(c, 'utf-8')

p = pathlib.Path('e:/data_control/server/services/query_service.py')

add(p, '        QueryResponse(', '        QueryResponse(')
add(p, '        Response(', '        Response(')
add(p, '        ranking', '        ranking')
add(p, '        items', '        items')
add(p, '        query', '        query')
add(p, '        {', '        {')

print('Fixed')