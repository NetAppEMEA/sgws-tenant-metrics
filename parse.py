import re
from pprint import pprint

results = {}
p = re.compile('\[(\w{4})(?:\(\w{4}\)):(\d+|\w{4}|"urn:sgws:identity::\d+:.+?"|".*?")\]')

def process_result(r):
    req_type = r.get('ATYP')
    if not (req_type == 'SGET' or req_type == 'SPUT' or req_type == 'SHEA' or req_type == 'SUPD' or req_type == 'SDEL'):
        return
    bucket = r.get('S3BK')
    acc = r.get('SACC')
    user = r.get('SUSR')
    tenant_id = r.get('S3AI')
    size = int(r.get('CSIZ', '0'))

    if tenant_id == '1': #CRR
        tenant_id = 'crr'
    if tenant_id == '': #Anonymous access
        tenant_id = 'anonymous_access'

    if not results.has_key(tenant_id):
        results[tenant_id] = {}
    
    if not results[tenant_id].has_key(bucket):
        results[tenant_id][bucket] = {'put_ops_count': 0, 'get_ops_count': 0, 'del_ops_count': 0, 'head_ops_count': 0,
                                      'update_ops_count': 0, 'put_traffic': 0, 'get_traffic': 0}

    # Get Object
    if req_type == 'SGET' and r.has_key('CSIZ'):
        results[tenant_id][bucket]['get_ops_count'] += 1
        results[tenant_id][bucket]['get_traffic'] += size

    # Head Object
    if req_type == 'SHEA' and r.has_key('S3KY'):
        results[tenant_id][bucket]['head_ops_count'] += 1

    # Delete Object
    if req_type == 'SDEL' and r.has_key('CSIZ'):
        results[tenant_id][bucket]['del_ops_count'] += 1

    # Update Object
    if req_type == 'SUPD' and r.has_key('CSIZ'):
        results[tenant_id][bucket]['update_ops_count'] += 1

    # Put Object
    if req_type == 'SPUT' and r.has_key('CSIZ'):
        results[tenant_id][bucket]['put_ops_count'] += 1
        results[tenant_id][bucket]['put_traffic'] += size

def scan_line(text):
    m = p.findall(text)
    if m:
        r = {}
        for i in m:
            r[i[0]] = i[1].replace('"', '')
        process_result(r)

with open("audit.log") as f:
    for line in f:
        scan_line(line)

pprint(results)