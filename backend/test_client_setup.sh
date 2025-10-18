#!/bin/bash

echo "🧪 Testing One-Click Client Setup..."
echo ""

# Check backend is running
if ! curl -s http://localhost:8000/api/health > /dev/null; then
    echo "❌ Backend not running!"
    exit 1
fi
echo "✅ Backend is running"

# Check client-setup endpoint exists
if curl -s http://localhost:8000/docs | grep -q "client-setup"; then
    echo "✅ Client setup endpoint registered"
else
    echo "❌ Client setup endpoint not found"
    exit 1
fi

# Check if CAs exist
CA_COUNT=$(python3 << PYEOF
from core.database import SessionLocal, Certificate
db = SessionLocal()
count = db.query(Certificate).filter(Certificate.is_ca == True).count()
print(count)
db.close()
PYEOF
)

if [ "$CA_COUNT" -gt 0 ]; then
    echo "✅ Found $CA_COUNT CA certificate(s)"
else
    echo "⚠️  No CA certificates found - create one first"
fi

# Check client certificates
CLIENT_COUNT=$(python3 << PYEOF
from core.database import SessionLocal, Certificate
db = SessionLocal()
count = db.query(Certificate).filter(Certificate.is_ca == False).count()
print(count)
db.close()
PYEOF
)

echo "✅ Found $CLIENT_COUNT client certificate(s)"

# Check token directory
if [ -d "/tmp/nebula-tokens" ]; then
    TOKEN_COUNT=$(ls /tmp/nebula-tokens/*.json 2>/dev/null | wc -l)
    echo "✅ Token directory exists ($TOKEN_COUNT active tokens)"
else
    echo "⚠️  Token directory doesn't exist yet"
fi

echo ""
echo "📊 Summary:"
echo "  - Backend: ✅ Running"
echo "  - Endpoint: ✅ Registered"
echo "  - CA Certs: $CA_COUNT"
echo "  - Client Certs: $CLIENT_COUNT"
echo "  - Active Tokens: ${TOKEN_COUNT:-0}"
echo ""
echo "🎯 Next: Test in browser at http://localhost:5173"
