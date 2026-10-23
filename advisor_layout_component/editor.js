(function () {
  'use strict';

  // These pure helpers are shared by pointer, button, and keyboard movement.
  function normalizeOrder(order, availableIds) {
    const available = new Set(availableIds);
    return [...new Set([...(Array.isArray(order) ? order : []), ...availableIds])]
      .filter((id) => available.has(id));
  }

  // A gap is an insertion point in the original list, before removal of the card.
  function moveToGap(order, id, gap) {
    const from = order.indexOf(id);
    if (from < 0 || !Number.isInteger(gap)) return [...order];
    const boundedGap = Math.max(0, Math.min(order.length, gap));
    const next = order.filter((item) => item !== id);
    next.splice(boundedGap > from ? boundedGap - 1 : boundedGap, 0, id);
    return next;
  }

  function dragScrollSpeed(x, y, pane) {
    if (x < pane.left || x > pane.right || y < pane.top || y > pane.bottom) return 0;
    const edge = Math.min(52, pane.height / 3);
    if (y < pane.top + edge) return -540 * (1 - (y - pane.top) / edge);
    if (y > pane.bottom - edge) return 540 * (1 - (pane.bottom - y) / edge);
    return 0;
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { normalizeOrder, moveToGap, dragScrollSpeed };
  }
  if (typeof document === 'undefined') return;

  const editor = document.getElementById('layout-editor');
  const sections = document.getElementById('placement-sections');
  const collapsedGrid = document.getElementById('collapsed-grid');
  const expandedGrid = document.getElementById('expanded-grid');
  const marker = document.getElementById('drop-marker');
  const announcement = document.getElementById('announcement');
  const saveButton = document.getElementById('save-button');
  const cancelButton = document.getElementById('cancel-button');
  const resetButton = document.getElementById('reset-button');
  let sessionId;
  let hasSession = false;
  let metrics = new Map();
  let order = [];
  let initialOrder = [];
  let defaultOrder = [];
  let collapsedCount = 4;
  let drag = null;
  let resizeFrame = 0;
  let lastHeight = 0;
  let dragScrollFrame = 0;
  let lastDragScrollTime = 0;
  let submitSequence = 0;
  const pageId = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;

  function send(type, payload) {
    window.parent.postMessage({ isStreamlitMessage: true, type, ...payload }, '*');
  }

  function updateHeight() {
    cancelAnimationFrame(resizeFrame);
    resizeFrame = requestAnimationFrame(() => {
      const height = Math.ceil(editor.getBoundingClientRect().height) + 4;
      if (height !== lastHeight) {
        lastHeight = height;
        send('streamlit:setFrameHeight', { height });
      }
    });
  }

  function announce(message) {
    announcement.textContent = '';
    requestAnimationFrame(() => { announcement.textContent = message; });
  }

  function changed() {
    return order.some((id, index) => initialOrder[index] !== id);
  }

  function updateDraftNote() {
    document.getElementById('draft-note').textContent = changed()
      ? 'Unsaved changes · applies to all advisors'
      : 'Preview only · no changes saved';
  }

  function makeButton(className, text, label) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = className;
    button.textContent = text;
    button.setAttribute('aria-label', label);
    return button;
  }

  function makeCard(id, index) {
    const metric = metrics.get(id);
    const card = document.createElement('div');
    card.className = 'metric-card';
    card.dataset.metricId = id;
    card.setAttribute('role', 'listitem');
    card.setAttribute('aria-label', `${metric.label}, position ${index + 1} of ${order.length}`);

    const top = document.createElement('div');
    top.className = 'card-top';
    const label = document.createElement('p');
    label.className = 'metric-label';
    label.textContent = metric.label;
    const handle = makeButton('drag-handle', '', `Move ${metric.label}. Hold Alt and use arrow keys.`);
    handle.dataset.control = 'handle';
    handle.setAttribute('aria-describedby', 'keyboard-help');
    const dots = document.createElement('span');
    dots.className = 'drag-dots';
    dots.setAttribute('aria-hidden', 'true');
    handle.append(dots);
    top.append(label, handle);

    const value = document.createElement('div');
    value.className = 'metric-value';
    // This value is render_cell() HTML escaped by the Python wrapper. All other
    // supplied strings are assigned with textContent, including names and labels.
    value.innerHTML = typeof metric.html === 'string' ? metric.html : '';

    const footer = document.createElement('div');
    footer.className = 'card-footer';
    const position = document.createElement('span');
    position.className = 'card-position';
    position.textContent = `${index + 1} of ${order.length}`;
    position.setAttribute('aria-hidden', 'true');
    const controls = document.createElement('div');
    controls.className = 'move-controls';
    const earlier = makeButton('move-button', '←', `Move ${metric.label} earlier`);
    earlier.title = 'Move earlier';
    earlier.dataset.control = 'earlier';
    earlier.disabled = index === 0;
    const later = makeButton('move-button', '→', `Move ${metric.label} later`);
    later.title = 'Move later';
    later.dataset.control = 'later';
    later.disabled = index === order.length - 1;
    controls.append(earlier, later);
    footer.append(position, controls);
    card.append(top, value, footer);
    return card;
  }

  function focusControl(id, control) {
    const card = [...sections.querySelectorAll('.metric-card')]
      .find((item) => item.dataset.metricId === id);
    if (!card) return;
    const target = card.querySelector(`[data-control="${control}"]`);
    (target && !target.disabled ? target : card.querySelector('.drag-handle')).focus({ preventScroll: true });
    card.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  }

  function renderCards(focus) {
    const collapsed = document.createDocumentFragment();
    const expanded = document.createDocumentFragment();
    order.forEach((id, index) => {
      (index < collapsedCount ? collapsed : expanded).append(makeCard(id, index));
    });
    collapsedGrid.replaceChildren(collapsed);
    expandedGrid.replaceChildren(expanded);
    document.getElementById('expanded-empty').hidden = order.length > collapsedCount;
    document.getElementById('collapsed-note').textContent = `First ${Math.min(collapsedCount, order.length)} cards · always visible`;
    updateDraftNote();
    if (focus) focusControl(focus.id, focus.control);
    updateHeight();
  }

  function move(id, gap, control) {
    const next = moveToGap(order, id, gap);
    if (next.every((item, index) => item === order[index])) return false;
    order = next;
    renderCards({ id, control });
    const position = order.indexOf(id);
    announce(`${metrics.get(id).label} moved to position ${position + 1} of ${order.length}, ${position < collapsedCount ? 'collapsed view' : 'expanded details'}.`);
    return true;
  }

  sections.addEventListener('click', (event) => {
    const button = event.target.closest('.move-button');
    if (!button || button.disabled) return;
    const id = button.closest('.metric-card').dataset.metricId;
    const index = order.indexOf(id);
    move(id, button.dataset.control === 'earlier' ? index - 1 : index + 2, button.dataset.control);
  });

  sections.addEventListener('keydown', (event) => {
    const handle = event.target.closest('.drag-handle');
    if (!handle || !event.altKey || !['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) return;
    event.preventDefault();
    const id = handle.closest('.metric-card').dataset.metricId;
    const index = order.indexOf(id);
    move(id, ['ArrowLeft', 'ArrowUp'].includes(event.key) ? index - 1 : index + 2, 'handle');
  });

  function clearDrag(cancelled) {
    cancelAnimationFrame(dragScrollFrame);
    dragScrollFrame = 0;
    lastDragScrollTime = 0;
    if (!drag) return;
    const previous = drag;
    drag = null;
    previous.card.classList.remove('is-dragging');
    if (previous.card.hasPointerCapture(previous.pointerId)) previous.card.releasePointerCapture(previous.pointerId);
    previous.ghost?.remove();
    marker.hidden = true;
    document.body.classList.remove('is-dragging');
    if (cancelled && previous.active) announce('Move cancelled. Card placement is unchanged.');
    return previous;
  }

  function showMarker(rect, after) {
    const pane = sections.getBoundingClientRect();
    const top = Math.max(rect.top + 3, pane.top + 3);
    const bottom = Math.min(rect.top + rect.height - 3, pane.bottom - 3);
    marker.hidden = false;
    marker.classList.remove('is-horizontal');
    marker.style.left = `${(after ? rect.right : rect.left) - 2}px`;
    marker.style.top = `${top}px`;
    marker.style.width = '3px';
    marker.style.height = `${Math.max(3, bottom - top)}px`;
  }

  function updateTarget(x, y) {
    const hit = document.elementFromPoint(x, y);
    const zone = hit?.closest('.placement-section');
    drag.gap = null;
    marker.hidden = true;
    if (!zone || !sections.contains(zone)) return;
    const grid = zone.querySelector('.metric-grid');
    const cards = [...grid.querySelectorAll('.metric-card')];
    if (!cards.length) {
      const rect = grid.getBoundingClientRect();
      drag.gap = zone.dataset.zone === 'collapsed' ? 0 : order.length;
      showMarker({ left: rect.left + 2, right: rect.right, top: rect.top, height: 28 }, false);
      return;
    }
    let card = hit.closest('.metric-card');
    if (!card) {
      // Whitespace between cards selects the nearest card in this section.
      card = cards.reduce((nearest, candidate) => {
        const rect = candidate.getBoundingClientRect();
        const distance = Math.hypot(Math.max(rect.left - x, 0, x - rect.right), Math.max(rect.top - y, 0, y - rect.bottom));
        return !nearest || distance < nearest.distance ? { element: candidate, distance } : nearest;
      }, null).element;
    }
    const rect = card.getBoundingClientRect();
    const index = order.indexOf(card.dataset.metricId);
    // One-column layouts use the vertical midpoint; grids use the horizontal one.
    const columns = getComputedStyle(grid).gridTemplateColumns.split(' ').length;
    const after = columns === 1 ? y > rect.top + rect.height / 2 : x > rect.left + rect.width / 2;
    drag.gap = index + (after ? 1 : 0);
    if (columns === 1) {
      const pane = sections.getBoundingClientRect();
      marker.hidden = false;
      marker.classList.add('is-horizontal');
      marker.style.left = `${rect.left + 3}px`;
      marker.style.top = `${Math.max(pane.top + 2, Math.min(pane.bottom - 4, (after ? rect.bottom : rect.top) - 2))}px`;
      marker.style.width = `${rect.width - 6}px`;
      marker.style.height = '3px';
    } else showMarker(rect, after);
  }

  function scrollDrag(timestamp) {
    dragScrollFrame = 0;
    if (!drag?.active) return;
    const speed = dragScrollSpeed(drag.clientX, drag.clientY, sections.getBoundingClientRect());
    if (!speed) { lastDragScrollTime = 0; return; }
    const elapsed = lastDragScrollTime ? Math.min(32, timestamp - lastDragScrollTime) : 16;
    lastDragScrollTime = timestamp;
    const previousTop = sections.scrollTop;
    sections.scrollTop += speed * elapsed / 1000;
    updateTarget(drag.clientX, drag.clientY);
    if (sections.scrollTop !== previousTop) dragScrollFrame = requestAnimationFrame(scrollDrag);
    else lastDragScrollTime = 0;
  }

  function scheduleDragScroll() {
    if (!dragScrollFrame) dragScrollFrame = requestAnimationFrame(scrollDrag);
  }

  sections.addEventListener('scroll', () => {
    if (drag?.active) updateTarget(drag.clientX, drag.clientY);
  }, { passive: true });

  sections.addEventListener('pointerdown', (event) => {
    const card = event.target.closest('.metric-card');
    if (!card || !event.isPrimary || event.button !== 0 || (event.target.closest('button') && !event.target.closest('.drag-handle'))) return;
    // Preserve vertical page scrolling over cards on touchscreens. Their handle
    // has touch-action:none and provides the explicit touch drag target.
    if (event.pointerType === 'touch' && !event.target.closest('.drag-handle')) return;
    clearDrag(true);
    drag = { id: card.dataset.metricId, card, pointerId: event.pointerId, startX: event.clientX, startY: event.clientY, active: false, gap: null };
    card.setPointerCapture(event.pointerId);
  });

  sections.addEventListener('pointermove', (event) => {
    if (!drag || event.pointerId !== drag.pointerId) return;
    drag.clientX = event.clientX;
    drag.clientY = event.clientY;
    if (!drag.active) {
      if (Math.hypot(event.clientX - drag.startX, event.clientY - drag.startY) < 6) return;
      const rect = drag.card.getBoundingClientRect();
      drag.active = true;
      drag.offsetX = Math.min(rect.width - 10, Math.max(10, drag.startX - rect.left));
      drag.offsetY = Math.min(rect.height - 10, Math.max(10, drag.startY - rect.top));
      drag.ghost = drag.card.cloneNode(true);
      drag.ghost.classList.add('drag-ghost');
      drag.ghost.style.width = `${rect.width}px`;
      drag.ghost.setAttribute('aria-hidden', 'true');
      drag.ghost.inert = true;
      document.body.append(drag.ghost);
      drag.card.classList.add('is-dragging');
      document.body.classList.add('is-dragging');
      announce(`Moving ${metrics.get(drag.id).label}. Drop at a blue marker, or press Escape to cancel.`);
    }
    event.preventDefault();
    drag.ghost.style.left = `${event.clientX - drag.offsetX}px`;
    drag.ghost.style.top = `${event.clientY - drag.offsetY}px`;
    updateTarget(event.clientX, event.clientY);
    scheduleDragScroll();
  });

  sections.addEventListener('pointerup', (event) => {
    if (!drag || event.pointerId !== drag.pointerId) return;
    if (drag.active) updateTarget(event.clientX, event.clientY);
    const previous = clearDrag(false);
    if (previous.active && previous.gap !== null) {
      if (!move(previous.id, previous.gap, 'handle')) announce(`${metrics.get(previous.id).label} kept at position ${order.indexOf(previous.id) + 1}.`);
    }
    else if (previous.active) announce('Move cancelled. Drop inside a card section to change placement.');
  });
  sections.addEventListener('pointercancel', (event) => {
    if (drag?.pointerId === event.pointerId) clearDrag(true);
  });
  sections.addEventListener('lostpointercapture', () => clearDrag(true));
  window.addEventListener('blur', () => clearDrag(true));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && drag) { event.preventDefault(); clearDrag(true); }
  });

  resetButton.addEventListener('click', () => {
    clearDrag(true);
    order = [...defaultOrder];
    renderCards();
    announce('Default card placement restored in the preview. Save to apply it to all advisors.');
  });

  function submit(action) {
    clearDrag(true);
    const eventId = typeof window.crypto?.randomUUID === 'function'
      ? window.crypto.randomUUID()
      : `${pageId}:${++submitSequence}`;
    send('streamlit:setComponentValue', { value: { action, order: [...order], session_id: sessionId, event_id: eventId }, dataType: 'json' });
    // Keep actions available: Python may keep this editing session open if saving fails.
    if (action === 'save') announce('Saving card placement for all advisors.');
  }
  saveButton.addEventListener('click', () => submit('save'));
  cancelButton.addEventListener('click', () => submit('cancel'));

  window.addEventListener('message', (event) => {
    if (event.source !== window.parent || event.data?.type !== 'streamlit:render') return;
    const args = event.data.args || {};
    const nextMetrics = new Map();
    (Array.isArray(args.metrics) ? args.metrics : []).forEach((metric) => {
      if (metric && typeof metric.id === 'string' && !nextMetrics.has(metric.id)) {
        nextMetrics.set(metric.id, { ...metric, label: String(metric.label ?? metric.id) });
      }
    });
    const ids = [...nextMetrics.keys()];
    const newSession = !hasSession || args.session_id !== sessionId;
    const focused = document.activeElement.closest?.('[data-control]');
    const focus = focused ? { id: focused.closest('.metric-card').dataset.metricId, control: focused.dataset.control } : null;
    clearDrag(true);
    metrics = nextMetrics;
    defaultOrder = normalizeOrder(args.default_order, ids);
    if (newSession) {
      sessionId = args.session_id;
      hasSession = true;
      order = normalizeOrder(args.order, ids);
      initialOrder = [...order];
    } else {
      order = normalizeOrder(order, ids);
      initialOrder = normalizeOrder(initialOrder, ids);
    }
    collapsedCount = Number.isInteger(args.collapsed_count) ? Math.max(0, Math.min(args.collapsed_count, ids.length)) : Math.min(4, ids.length);
    document.getElementById('advisor-name').textContent = String(args.advisor_name ?? '');
    document.getElementById('advisor-rank').textContent = args.advisor_rank == null ? '' : `#${args.advisor_rank}`;
    editor.setAttribute('aria-busy', 'false');
    saveButton.disabled = ids.length === 0;
    resetButton.disabled = ids.length === 0;
    cancelButton.disabled = false;
    renderCards(newSession ? null : focus);
  });

  if (typeof ResizeObserver !== 'undefined') new ResizeObserver(updateHeight).observe(editor);
  window.addEventListener('resize', updateHeight);
  send('streamlit:componentReady', { apiVersion: 1 });
  updateHeight();
})();
