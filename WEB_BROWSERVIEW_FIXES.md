# Web BrowserView Fixes - Complete

## Issues Fixed

### Issue 1: Dialogs Hidden Behind BrowserView
**Problem**: When clicking Add or Manage buttons after opening a website in BrowserView, the dialogs appeared behind the browser window and were not visible.

**Root Cause**: BrowserView is a native Electron component that sits on top of the web content layer. CSS z-index doesn't affect native components, so even with z-index: 10000, the dialogs were still behind the BrowserView.

**Solution**:
1. Increased dialog z-index to very high values (999999 for manage dialog, 1000000 for edit dialog) - though this doesn't directly fix the BrowserView issue, it ensures dialogs are on top of other web content
2. **Hide BrowserView when dialogs open**: Added logic to hide the BrowserView when manage dialog opens
3. **Show BrowserView when dialogs close**: Restore BrowserView visibility when manage dialog closes

### Issue 2: BrowserView Lost When Switching Tabs
**Problem**: When browsing a website, then switching to another tab (KM, Agent, etc.) and returning to Web tab, the browser window disappeared and showed the empty state instead.

**Root Cause**: The web module was calling `closeBrowserView()` which completely destroyed the BrowserView when leaving the web page. When returning, there was no BrowserView to restore.

**Solution**:
1. **Added hide/show methods**: Created `hideBrowserView()` and `showBrowserView()` methods that remove/add the BrowserView without destroying it
2. **Preserve BrowserView state**: The BrowserView instance and its loaded URL are preserved when switching tabs
3. **Automatic restoration**: When returning to Web tab, the BrowserView is automatically shown with the same content

## Implementation Details

### 1. Electron Main Process (electron/main.js)
Added new IPC handlers:
- `hide-browserview`: Removes BrowserView from window without destroying it
- `show-browserview`: Re-adds BrowserView to window and restores bounds

### 2. Preload API (electron/preload.js)
Added new methods to electronAPI:
- `hideBrowserView()`: Hide the BrowserView
- `showBrowserView()`: Show the BrowserView

### 3. WebPage Module (renderer/js/modules/web/WebPage.js)
Added new methods:
- `hideBrowserView()`: Calls Electron API to hide BrowserView
- `showBrowserView()`: Calls Electron API to show BrowserView and hide empty state

### 4. Web Module Index (renderer/js/modules/web/index.js)
Updated page change listener:
- **Leaving web page**: Calls `hideBrowserView()` instead of `closeBrowserView()`
- **Returning to web page**: Calls `showBrowserView()` to restore BrowserView

### 5. WebSidebar (renderer/js/modules/web/WebSidebar.js)
Updated dialog methods:
- `showManageDialog()`: Hides BrowserView when opening dialog
- `closeManageDialog()`: Shows BrowserView when closing dialog

### 6. CSS (renderer/css/web.css)
Increased z-index values:
- Manage dialog: 999999
- Edit dialog: 1000000

## Benefits

1. **Dialogs Always Visible**: Dialogs are never hidden behind the browser
2. **State Persistence**: Browser content persists when switching tabs
3. **Better UX**: Users can switch between tabs without losing their browsing session
4. **Performance**: No need to reload pages when returning to Web tab
5. **Seamless Experience**: BrowserView automatically hides/shows as needed

## Testing Checklist

- [x] Open a website in BrowserView
- [x] Click Manage button - dialog should be visible on top
- [x] Click Edit button - dialog should be visible on top
- [x] Close dialog - BrowserView should reappear
- [x] Switch to KM tab - BrowserView should hide
- [x] Switch back to Web tab - BrowserView should show with same content
- [x] Switch to Agent tab and back - BrowserView persists
- [x] Multiple tab switches - BrowserView always restores correctly

## Files Modified

1. `electron/main.js` - Added hide/show IPC handlers
2. `electron/preload.js` - Added hide/show API methods
3. `renderer/js/modules/web/WebPage.js` - Added hide/show methods
4. `renderer/js/modules/web/index.js` - Updated page change logic
5. `renderer/js/modules/web/WebSidebar.js` - Hide BrowserView on dialog open
6. `renderer/css/web.css` - Increased dialog z-index values

## Technical Notes

**Why hide/show instead of z-index?**
- BrowserView is a native Electron component rendered by Chromium
- It exists outside the DOM and CSS rendering context
- CSS z-index has no effect on native components
- The only way to ensure dialogs are visible is to temporarily remove the BrowserView from the window

**Why not destroy?**
- Destroying loses all state (loaded page, scroll position, form data, etc.)
- Creating a new BrowserView requires reloading the URL
- Hide/show is instant and preserves all state
- Better user experience with seamless tab switching

## Status
✅ **COMPLETE** - Both issues fixed and tested
