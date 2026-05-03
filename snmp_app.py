from flask import Flask, request, jsonify
from pysnmp.hlapi import *

app = Flask(__name__)

@app.route('/snmp')
def snmp_get():
    target = request.args.get('target')
    oid = request.args.get('oid')

    iterator = getCmd(
        SnmpEngine(),
        CommunityData('public'),
        UdpTransportTarget((target, 161), timeout=3, retries=2),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:
        return jsonify({"error": str(errorIndication)})
    elif errorStatus:
        return jsonify({"error": errorStatus.prettyPrint()})
    else:
        result = []
        for varBind in varBinds:
            result.append(' = '.join([x.prettyPrint() for x in varBind]))

        return jsonify({"result": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)