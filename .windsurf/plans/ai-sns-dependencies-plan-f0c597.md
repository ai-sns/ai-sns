# AI-SNS Dependencies Management Plan

Create requirements.txt for a2aserver and adapters/openclaw, then optimize aisns_frontend/package.json.

## Tasks

### 1. Create a2aserver/requirements.txt
- **Purpose**: A2A protocol server for business card exchange (port 8789)
- **Dependencies**: fastapi, uvicorn (only 2 packages)
- **File**: `c:\dev\agi-ev\ai-sns-el\a2aserver\requirements.txt`

### 2. Create adapters/openclaw/requirements.txt  
- **Purpose**: OpenClaw gateway clients (HTTP/WebSocket/A2A/wiki chat)
- **Dependencies**: requests, fastapi, uvicorn, websockets
- **File**: `c:\dev\agi-ev\ai-sns-el\adapters\openclaw\requirements.txt`

### 3. Optimize aisns_frontend/package.json
- **Current Issues**:
  - Hardcoded relative paths for Python venv
  - Missing directories in build.files (runtime, agent don't exist)
  - Outdated dependencies (electron ^28.3.3, should be ^31.x)
  - No postinstall script for electron-builder
- **Changes**:
  - Update electron to ^31.0.0
  - Update electron-builder to ^25.0.0
  - Update wait-on to ^8.0.0
  - Update axios to ^1.7.0
  - Fix files/extraResources to use correct backend paths
  - Add postinstall script
  - Correct start:api script path
- **File**: `c:\dev\agi-ev\ai-sns-el\aisns_frontend\package.json`

## Notes
- All code comments and UI text must be in English
- Final summary to user will be in Chinese
