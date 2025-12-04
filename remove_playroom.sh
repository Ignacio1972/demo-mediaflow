#!/bin/bash

echo "🗑️  Removing Playroom..."
echo ""
echo "⚠️  WARNING: This will delete all Playroom files!"
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted"
    exit 1
fi

echo ""
echo "🧹 Cleaning up..."

# 1. Remove backend files
echo "  🗑️  Removing backend/app/api/v1/endpoints/settings/playroom.py"
rm -f backend/app/api/v1/endpoints/settings/playroom.py

# 2. Remove from settings router
echo "  ✏️  Removing playroom router from settings/__init__.py"
sed -i '/playroom_router/d' backend/app/api/v1/endpoints/settings/__init__.py

# 3. Remove frontend directory
echo "  🗑️  Removing frontend/src/components/settings/playroom/"
rm -rf frontend/src/components/settings/playroom/

# 4. Remove from router
echo "  ✏️  Removing playroom route from router/index.ts"
# This is a bit complex, so we'll just note it
echo "     ⚠️  Manual step needed: Remove playroom route from frontend/src/router/index.ts"

# 5. Remove from navigation
echo "  ✏️  Removing playroom from navigation"
echo "     ⚠️  Manual step needed: Remove playroom link from frontend/src/components/settings/SettingsNav.vue"

# 6. Optional: Remove generated audio files
echo ""
read -p "Do you want to delete Playroom-generated audio files? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  🗑️  Removing playroom_*.mp3 files"
    rm -f backend/storage/audio/playroom_*.mp3
    echo "     ✅ Deleted $(ls -1 backend/storage/audio/playroom_*.mp3 2>/dev/null | wc -l) files"
fi

echo ""
echo "✅ Playroom removal complete!"
echo ""
echo "📝 Manual cleanup needed:"
echo "   1. Edit frontend/src/router/index.ts"
echo "      Remove the playroom route (lines ~55-59)"
echo ""
echo "   2. Edit frontend/src/components/settings/SettingsNav.vue"
echo "      - Remove BeakerIcon import"
echo "      - Remove playroom router-link"
echo "      - Remove .playroom-link styles"
echo ""
echo "   3. Rebuild frontend:"
echo "      cd frontend && npm run build"
echo ""
echo "   4. Restart backend if running"
echo ""
