# Test Guide: BrowserView Fixes

## Test 1: Dialog Visibility Over BrowserView

### Steps:
1. Start the application
2. Go to Web tab
3. Click on any LLM or Tool icon to open a website
4. Wait for the website to load in BrowserView
5. Click the "Manage" button (for either LLM or Tool section)

**Expected Result**: 
- ✅ Manage dialog appears on top of the browser
- ✅ Dialog is fully visible and interactive
- ✅ Browser content is hidden behind the dialog overlay

6. Click "Edit" button on any item in the manage dialog

**Expected Result**:
- ✅ Edit dialog appears on top
- ✅ Edit dialog is fully visible and interactive

7. Click "Cancel" or "Save" to close edit dialog
8. Click the X button to close manage dialog

**Expected Result**:
- ✅ BrowserView reappears with the same website
- ✅ Website is in the same state (scroll position, etc.)

## Test 2: BrowserView Persistence Across Tab Switches

### Steps:
1. Go to Web tab
2. Click on any website icon (e.g., ChatGPT, Claude)
3. Wait for website to load
4. Scroll down on the website (to verify state preservation)
5. Switch to KM tab

**Expected Result**:
- ✅ BrowserView disappears (hidden)
- ✅ KM content is visible

6. Switch back to Web tab

**Expected Result**:
- ✅ BrowserView reappears immediately
- ✅ Same website is still loaded
- ✅ Scroll position is preserved
- ✅ No reload or flicker

7. Switch to Agent tab

**Expected Result**:
- ✅ BrowserView disappears
- ✅ Agent content is visible

8. Switch back to Web tab

**Expected Result**:
- ✅ BrowserView reappears with same content
- ✅ Everything is preserved

## Test 3: Multiple Operations

### Steps:
1. Open a website in Web tab
2. Switch to KM tab
3. Switch to Agent tab
4. Switch back to Web tab
5. Click "Manage" button
6. Edit an item
7. Close dialogs
8. Switch to another tab
9. Switch back to Web tab

**Expected Result**:
- ✅ BrowserView persists through all tab switches
- ✅ Dialogs work correctly every time
- ✅ No errors in console
- ✅ Smooth user experience

## Test 4: Edge Cases

### Test 4a: Dialog Operations While BrowserView Hidden
1. Open website in Web tab
2. Switch to KM tab (BrowserView hidden)
3. Switch back to Web tab
4. Immediately click "Manage"

**Expected Result**:
- ✅ Dialog appears correctly
- ✅ No visual glitches

### Test 4b: Multiple Dialog Opens
1. Open website in Web tab
2. Click "Manage"
3. Close dialog
4. Click "Manage" again
5. Close dialog
6. Repeat 2-3 times

**Expected Result**:
- ✅ BrowserView hides/shows correctly each time
- ✅ No memory leaks or performance issues

### Test 4c: Window Resize
1. Open website in Web tab
2. Resize the application window
3. Switch to another tab
4. Switch back to Web tab

**Expected Result**:
- ✅ BrowserView bounds are correct after resize
- ✅ Content fits properly in the window

## Console Verification

Check browser console for these logs:

**When opening manage dialog:**
```
[BrowserView] Hidden (not destroyed)
```

**When closing manage dialog:**
```
[BrowserView] Shown (restored)
[WebSidebar] Dialog closed, sidebar refreshed
```

**When switching away from Web tab:**
```
[Web Module] Leaving web page, hiding BrowserView
[BrowserView] Hidden (not destroyed)
```

**When switching back to Web tab:**
```
[Web Module] Returning to web page, showing BrowserView
[BrowserView] Shown (restored)
[WebPage] BrowserView shown
```

## What NOT to See

❌ No "BrowserView destroyed" messages during tab switches
❌ No website reloads when returning to Web tab
❌ No dialogs hidden behind browser
❌ No empty state showing when BrowserView should be visible
❌ No errors about missing BrowserView

## Success Criteria

✅ Dialogs always visible on top of BrowserView
✅ BrowserView persists across tab switches
✅ Website state (scroll, forms, etc.) preserved
✅ Smooth hide/show transitions
✅ No performance issues or memory leaks
✅ Console logs show correct hide/show behavior
