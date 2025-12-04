#!/bin/bash

echo "🎮 Verificando Playroom Installation..."
echo ""

# Check backend files
echo "📦 Backend Files:"
if [ -f "backend/app/api/v1/endpoints/settings/playroom.py" ]; then
    echo "  ✅ playroom.py exists"
else
    echo "  ❌ playroom.py NOT FOUND"
    exit 1
fi

# Check frontend files
echo ""
echo "🎨 Frontend Files:"
if [ -f "frontend/src/components/settings/playroom/PlayroomMode.vue" ]; then
    echo "  ✅ PlayroomMode.vue exists"
else
    echo "  ❌ PlayroomMode.vue NOT FOUND"
    exit 1
fi

if [ -f "frontend/src/components/settings/playroom/composables/usePlayroomMode.ts" ]; then
    echo "  ✅ usePlayroomMode.ts exists"
else
    echo "  ❌ usePlayroomMode.ts NOT FOUND"
    exit 1
fi

# Check components
component_count=$(ls -1 frontend/src/components/settings/playroom/components/*.vue 2>/dev/null | wc -l)
if [ "$component_count" -eq 5 ]; then
    echo "  ✅ All 5 components copied"
else
    echo "  ⚠️  Expected 5 components, found $component_count"
fi

# Check router
echo ""
echo "🛣️  Router Configuration:"
if grep -q "playroom" frontend/src/router/index.ts; then
    echo "  ✅ Playroom route registered"
else
    echo "  ❌ Playroom route NOT registered"
    exit 1
fi

# Check navigation
echo ""
echo "🧭 Navigation:"
if grep -q "BeakerIcon" frontend/src/components/settings/SettingsNav.vue; then
    echo "  ✅ Playroom link in navigation"
else
    echo "  ❌ Playroom link NOT in navigation"
    exit 1
fi

# Check settings router
echo ""
echo "⚙️  Settings Router:"
if grep -q "playroom_router" backend/app/api/v1/endpoints/settings/__init__.py; then
    echo "  ✅ Playroom router included in settings"
else
    echo "  ❌ Playroom router NOT included"
    exit 1
fi

echo ""
echo "🎉 ALL CHECKS PASSED!"
echo ""
echo "📍 Access Playroom at: http://localhost:5173/settings/playroom"
echo "📍 API Endpoints:"
echo "   - GET  /api/v1/settings/playroom/config"
echo "   - POST /api/v1/settings/playroom/generate"
echo ""
echo "📚 Documentation: docs/PLAYROOM.md"
echo ""
