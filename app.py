from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is running ✅"

@app.route('/snmp')
def snmp_get():
    target = request.args.get('target', 'demo.snmplabs.com')
    oid = request.args.get('oid', '1.3.6.1.2.1.1.1.0')

    try:
        # Import INSIDE function (important fix)
        from pysnmp.hlapi import (
            SnmpEngine,
            CommunityData,
            UdpTransportTarget,
            ContextData,
            ObjectType,
            ObjectIdentity,
            getCmd
        )

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
        return jsonify({
            "error": "SNMP failed",
            "details": str(e)
        })

# Required for local fallback (Render ignores this)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
