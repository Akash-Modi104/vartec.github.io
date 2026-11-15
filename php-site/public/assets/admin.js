/* VARTEC admin: small behaviours layered on ordinary forms. No framework, no build step. */
(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const csrf = ($('meta[name="csrf"]') || {}).content || '';

  // ---- mobile menu
  const menuButton = $('[data-menu]');
  const sidebar = $('#sidebar');
  if (menuButton && sidebar) {
    menuButton.addEventListener('click', () => {
      const open = sidebar.classList.toggle('open');
      menuButton.setAttribute('aria-expanded', String(open));
    });
  }

  // ---- confirmation in the page (not a browser pop-up)
  const askConfirm = (message) => new Promise((resolve) => {
    const dialog = document.createElement('dialog');
    dialog.className = 'confirm-dialog';
    const text = document.createElement('p');
    text.textContent = message;
    const row = document.createElement('div');
    row.className = 'row';
    const cancel = Object.assign(document.createElement('button'), { type: 'button', className: 'btn', textContent: 'Cancel' });
    const ok = Object.assign(document.createElement('button'), { type: 'button', className: 'btn btn-primary', textContent: 'Yes, continue' });
    row.append(cancel, ok);
    dialog.append(text, row);
    document.body.append(dialog);
    const finish = (answer) => { dialog.close(); dialog.remove(); resolve(answer); };
    cancel.addEventListener('click', () => finish(false));
    ok.addEventListener('click', () => finish(true));
    dialog.addEventListener('cancel', (event) => { event.preventDefault(); finish(false); });
    dialog.showModal();
  });
  $$('form[data-confirm]').forEach((form) => form.addEventListener('submit', async (event) => {
    if (form.dataset.confirmed) return;
    event.preventDefault();
    if (await askConfirm(form.dataset.confirm)) { form.dataset.confirmed = '1'; clean = true; form.submit(); }
  }));

  // ---- character counters
  const updateCount = (field) => {
    const out = field.parentElement.querySelector('[data-count-out]');
    if (!out) return;
    const target = Number(field.dataset.count);
    const length = field.value.trim().length;
    out.textContent = length ? length + ' characters (aim for about ' + target + ')' : 'Empty: the page title or introduction is used instead';
    out.classList.toggle('over', length > target * 1.15);
  };
  $$('[data-count]').forEach((field) => { updateCount(field); field.addEventListener('input', () => updateCount(field)); });

  // ---- warn before leaving with unsaved edits
  let clean = true;
  $$('form[data-page-form], form[data-home-form]').forEach((form) => {
    form.addEventListener('input', () => { clean = false; });
    form.addEventListener('submit', () => { clean = true; });
  });
  window.addEventListener('beforeunload', (event) => { if (!clean) { event.preventDefault(); event.returnValue = ''; } });

  // ---- image / video chooser
  const dialog = $('#media-dialog');
  let activePicker = null;
  const setPicker = (picker, tile) => {
    const input = $('input[type="hidden"]', picker);
    const preview = $('[data-picker-preview]', picker);
    const kind = picker.dataset.kind;
    input.value = tile ? tile.id : '';
    preview.textContent = '';
    if (!tile) {
      preview.append(Object.assign(document.createElement('span'), { className: 'picker-empty', textContent: 'No ' + kind + ' chosen' }));
    } else if (kind === 'image') {
      preview.append(Object.assign(document.createElement('img'), { src: tile.url, alt: tile.alt || '' }));
    } else {
      preview.append(Object.assign(document.createElement('span'), { className: 'picker-file', textContent: tile.alt || tile.url.split('/').pop() }));
    }
    $('[data-picker-warning]', picker).hidden = !(tile && tile.check);
    $('[data-picker-clear]', picker).hidden = !tile;
    clean = false;
  };
  const tileData = (tile) => ({ id: tile.dataset.id, url: tile.dataset.url, alt: tile.dataset.alt, check: tile.dataset.check === '1' });
  const openPicker = (picker) => {
    activePicker = picker;
    const kind = picker.dataset.kind;
    $('[data-dialog-title]', dialog).textContent = kind === 'video' ? 'Choose a video' : 'Choose an image';
    $$('[data-tile]', dialog).forEach((tile) => { tile.hidden = tile.dataset.kind !== kind; });
    $('[data-dialog-error]', dialog).textContent = '';
    dialog.showModal();
  };
  document.addEventListener('click', (event) => {
    const open = event.target.closest('[data-picker-open]');
    if (open && dialog) { openPicker(open.closest('[data-picker]')); return; }
    const clear = event.target.closest('[data-picker-clear]');
    if (clear) { setPicker(clear.closest('[data-picker]'), null); return; }
    const tile = event.target.closest('[data-tile]');
    if (tile && activePicker) { setPicker(activePicker, tileData(tile)); dialog.close(); return; }
    if (event.target.closest('[data-dialog-close]')) dialog.close();
  });
  const uploadForm = dialog && $('[data-dialog-upload]', dialog);
  if (uploadForm) {
    uploadForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const errorBox = $('[data-dialog-error]', dialog);
      const button = $('button[type="submit"]', uploadForm);
      errorBox.textContent = '';
      button.disabled = true;
      try {
        const response = await fetch('/admin/media/upload', { method: 'POST', headers: { Accept: 'application/json', 'X-CSRF-Token': csrf }, body: new FormData(uploadForm) });
        const result = await response.json();
        if (!result.ok) { errorBox.textContent = result.error || 'The upload did not work.'; return; }
        if (activePicker && result.kind !== activePicker.dataset.kind) { errorBox.textContent = 'Uploaded, but this spot needs ' + (activePicker.dataset.kind === 'video' ? 'a video' : 'an image') + '.'; return; }
        const tile = Object.assign(document.createElement('button'), { type: 'button', className: 'tile' });
        Object.assign(tile.dataset, { tile: '', id: result.id, kind: result.kind, url: result.url, alt: result.alt, check: result.check ? '1' : '0' });
        tile.append(result.kind === 'image' ? Object.assign(document.createElement('img'), { src: result.url, alt: '' }) : Object.assign(document.createElement('span'), { className: 'tile-video', textContent: 'VIDEO' }));
        tile.append(Object.assign(document.createElement('span'), { className: 'tile-name', textContent: result.alt }));
        $('[data-dialog-grid]', dialog).prepend(tile);
        uploadForm.reset();
        if (activePicker) { setPicker(activePicker, tileData(tile)); dialog.close(); }
      } catch (failure) {
        errorBox.textContent = 'The upload did not work. Check the file size and try again.';
      } finally { button.disabled = false; }
    });
  }

  // ---- shrink big photos in the browser before upload, so phone pictures fit any server limit
  const shrinkImage = async (file) => {
    if (!/^image\/(jpeg|png|webp)$/.test(file.type) || !window.createImageBitmap) return file;
    const bitmap = await createImageBitmap(file);
    if (bitmap.width <= 1600 && file.size <= 1500000) return file;
    const scale = Math.min(1, 1600 / bitmap.width);
    const canvas = Object.assign(document.createElement('canvas'), { width: Math.round(bitmap.width * scale), height: Math.round(bitmap.height * scale) });
    canvas.getContext('2d').drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    const type = file.type === 'image/jpeg' ? 'image/jpeg' : 'image/webp';
    const blob = await new Promise((resolve) => canvas.toBlob(resolve, type, 0.86));
    if (!blob || blob.size >= file.size) return file;
    return new File([blob], file.name.replace(/\.[^.]+$/, '') + (type === 'image/jpeg' ? '.jpg' : '.webp'), { type: blob.type });
  };
  document.addEventListener('change', async (event) => {
    const input = event.target;
    if (!input.matches('input[type="file"]') || !input.files[0] || !window.DataTransfer) return;
    try {
      const smaller = await shrinkImage(input.files[0]);
      if (smaller !== input.files[0]) { const transfer = new DataTransfer(); transfer.items.add(smaller); input.files = transfer.files; }
    } catch (failure) { /* keep the original file; the server will judge it */ }
  });

  // ---- lists: move up / down, remove, add
  const itemSelector = '[data-item], [data-section], [data-list-item], [data-sort-item]';
  document.addEventListener('click', async (event) => {
    const move = event.target.closest('[data-move]');
    if (move) {
      const row = move.closest(itemSelector);
      const siblings = Array.from(row.parentElement.children).filter((el) => el.matches(itemSelector));
      const target = siblings[siblings.indexOf(row) + Number(move.dataset.move)];
      if (target) { Number(move.dataset.move) < 0 ? target.before(row) : target.after(row); move.focus(); clean = false; renumber(); }
      return;
    }
    const remove = event.target.closest('[data-remove]');
    if (remove) {
      const row = remove.closest(itemSelector);
      if (row.matches('[data-section]') && !(await askConfirm('Remove this whole section?'))) return;
      row.remove(); clean = false; renumber();
      return;
    }
    const addItem = event.target.closest('[data-add-item]');
    if (addItem) {
      const node = $('[data-item-template]').content.firstElementChild.cloneNode(true);
      $('[data-name="type"]', node).value = addItem.dataset.addItem;
      $('[data-items]', addItem.closest('[data-section]')).append(node);
      $('[data-name="text"]', node).focus(); clean = false;
      return;
    }
    if (event.target.closest('[data-add-section]')) {
      const node = $('[data-section-template]').content.firstElementChild.cloneNode(true);
      $('[data-sections]').append(node); renumber();
      $('[data-name="heading"]', node).focus(); clean = false;
      return;
    }
    if (event.target.closest('[data-add-slide]')) {
      const node = $('[data-slide-template]').content.firstElementChild.cloneNode(true);
      $('.slides').append(node); openPicker($('[data-picker]', node));
      return;
    }
    if (event.target.closest('[data-add-card]')) {
      const node = $('[data-card-template]').content.firstElementChild.cloneNode(true);
      $('[data-cards]').append(node); $('[data-name="title"]', node).focus(); clean = false;
    }
  });
  const renumber = () => $$('[data-section]').forEach((section, index) => {
    const label = $('[data-section-label]', section);
    if (label) label.textContent = 'Section ' + (index + 1);
  });

  // ---- give every field its position-based name just before saving
  const pageForm = $('form[data-page-form]');
  if (pageForm) pageForm.addEventListener('submit', () => {
    $$('[data-section]', pageForm).forEach((section, i) => {
      $$('[data-name]', section).filter((field) => !field.closest('[data-item]')).forEach((field) => { field.name = 'sections[' + i + '][' + field.dataset.name + ']'; });
      $$('[data-item]', section).forEach((item, j) => $$('[data-name]', item).forEach((field) => { field.name = 'sections[' + i + '][items][' + j + '][' + field.dataset.name + ']'; }));
    });
  });
  const homeForm = $('form[data-home-form]');
  if (homeForm) homeForm.addEventListener('submit', () => {
    $$('[data-cards] [data-list-item]', homeForm).forEach((card, i) => $$('[data-name]', card).forEach((field) => { field.name = 'cards[' + i + '][' + field.dataset.name + ']'; }));
  });
})();
