from flask import Flask, request, jsonify
from pysnmp.hlapi import *
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "SNMP Proxy is running ✅"

@app.route('/snmp')
def snmp_get():
    target = request.args.get('target', 'demo.snmplabs.com')
    oid = request.args.get('oid', '1.3.6.1.2.1.1.1.0')

    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData('public'),
            UdpTransportTarget((target, 161), timeout=5, retries=2),
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

    except Exception as e:
        return jsonify({"error": str(e)})

# DO NOT remove this
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))