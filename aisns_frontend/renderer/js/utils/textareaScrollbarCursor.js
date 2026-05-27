/**
 * Global fix for the I-beam cursor over a textarea's native scrollbar.
 *
 * Background: In Chromium/Electron, a <textarea> applies its own `cursor: text`
 * to the entire client area, including the area occupied by the native
 * scrollbar. Styling `textarea::-webkit-scrollbar { cursor: default }` is
 * unreliable because the textarea's own cursor wins on the scrollbar region.
 *
 * Approach: Listen to mousemove globally. When the pointer is over a textarea,
 * compute the vertical/horizontal native scrollbar region using
 * (offsetWidth - clientWidth - borders) and (offsetHeight - clientHeight - borders).
 * If the pointer is inside that region, set inline `cursor: default`; otherwise
 * clear the inline override so the original `cursor: text` is restored.
 *
 * Notes:
 *  - Uses capture phase + a single passive listener for performance.
 *  - Works for dynamically-added textareas (no per-element binding needed).
 *  - Does not modify keyboard focus, selection, or any input behavior.
 */
(function () {
    if (typeof document === 'undefined') return;
    if (window.__textareaScrollbarCursorPatched) return;
    window.__textareaScrollbarCursorPatched = true;

    var SCROLLBAR_SLOP_PX = 1; // tolerance for fractional pixel rounding

    function getMetrics(el) {
        var cs = window.getComputedStyle(el);
        var bl = parseFloat(cs.borderLeftWidth) || 0;
        var br = parseFloat(cs.borderRightWidth) || 0;
        var bt = parseFloat(cs.borderTopWidth) || 0;
        var bb = parseFloat(cs.borderBottomWidth) || 0;
        var vScroll = el.offsetWidth - el.clientWidth - bl - br;
        var hScroll = el.offsetHeight - el.clientHeight - bt - bb;
        return {
            vScroll: vScroll > 0 ? vScroll : 0,
            hScroll: hScroll > 0 ? hScroll : 0,
            bl: bl,
            br: br,
            bt: bt,
            bb: bb,
        };
    }

    function isOverScrollbar(el, clientX, clientY) {
        var rect = el.getBoundingClientRect();
        var m = getMetrics(el);
        if (m.vScroll <= 0 && m.hScroll <= 0) return false;
        // Distance from right inner edge (excluding right border)
        var xFromRight = rect.right - m.br - clientX;
        // Distance from bottom inner edge (excluding bottom border)
        var yFromBottom = rect.bottom - m.bb - clientY;
        var onVertical = m.vScroll > 0
            && xFromRight >= -SCROLLBAR_SLOP_PX
            && xFromRight <= m.vScroll + SCROLLBAR_SLOP_PX;
        var onHorizontal = m.hScroll > 0
            && yFromBottom >= -SCROLLBAR_SLOP_PX
            && yFromBottom <= m.hScroll + SCROLLBAR_SLOP_PX;
        return onVertical || onHorizontal;
    }

    function applyCursor(el, overScrollbar) {
        if (overScrollbar) {
            if (el.style.cursor !== 'default') {
                el.dataset.tscPrevCursor = el.style.cursor || '';
                el.style.cursor = 'default';
            }
        } else {
            if (el.style.cursor === 'default') {
                var prev = el.dataset.tscPrevCursor || '';
                if (prev) {
                    el.style.cursor = prev;
                } else {
                    el.style.removeProperty('cursor');
                }
                delete el.dataset.tscPrevCursor;
            }
        }
    }

    function onMouseMove(e) {
        var t = e.target;
        if (!t || t.tagName !== 'TEXTAREA') return;
        try {
            applyCursor(t, isOverScrollbar(t, e.clientX, e.clientY));
        } catch (err) {
            // Fail-safe: never break user interaction due to this helper
        }
    }

    function onMouseLeave(e) {
        var t = e.target;
        if (t && t.tagName === 'TEXTAREA') {
            try {
                applyCursor(t, false);
            } catch (err) {
                /* noop */
            }
        }
    }

    document.addEventListener('mousemove', onMouseMove, true);
    document.addEventListener('mouseout', onMouseLeave, true);
})();
