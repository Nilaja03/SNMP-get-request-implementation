from flask import Flask, request, jsonify
import os

DUMMY_SNMP = {
    "1.3.6.1.2.1.1.1.0": "Linux Demo System",
    "1.3.6.1.2.1.1.5.0": "My-Test-Device",
    "1.3.6.1.2.1.1.3.0": "123456 uptime",
}

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is running ✅"

@app.route('/snmp')
def snmp_get():
    target = request.args.get('target', 'demo.snmplabs.com')
    oid = request.args.get('oid', '1.3.6.1.2.1.1.1.0')

    try:
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

        # 🔥 If SNMP fails → fallback to dummy
        if errorIndication or errorStatus:
            value = DUMMY_SNMP.get(oid, "Unknown OID (simulated)")
            return jsonify({
                "result": [f"{oid} = {value}"],
                "source": "mock"
            })

        # ✅ Real SNMP success
        result = []
        for varBind in varBinds:
            result.append(' = '.join([x.prettyPrint() for x in varBind]))

        return jsonify({
            "result": result,
            "source": "real"
        })

    except Exception:
        # 🔥 Hard fallback (if pysnmp crashes)
        value = DUMMY_SNMP.get(oid, "Unknown OID (simulated)")
        return jsonify({
            "result": [f"{oid} = {value}"],
            "source": "mock"
        })

# Required for local fallback (Render ignores this)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
