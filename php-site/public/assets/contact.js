/* Contact form: sends through the existing send_mail.php exactly as the previous site did
   (same address, same field names), then stores a copy for the admin inbox. */
(() => {
  const form = document.querySelector('[data-contact-form]');
  if (!form) return;
  const status = document.querySelector('[data-contact-status]');
  const error = form.querySelector('[data-contact-error]');
  const button = form.querySelector('button[type="submit"]');
  const encode = (data) => Object.keys(data).map((key) => encodeURIComponent(key) + '=' + encodeURIComponent(data[key])).join('&');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (form.elements.website.value) return; // filled only by bots
    const data = {};
    ['firstName', 'lastName', 'email', 'phone', 'message'].forEach((name) => { data[name] = form.elements[name].value.trim(); });
    button.disabled = true;
    error.hidden = true;
    let result = 'Error';
    try {
      const response = await fetch('/send_mail.php', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: encode(data) });
      result = (await response.text()).trim();
    } catch (failure) { result = 'Error'; }
    // Best effort only: the inbox copy must never affect whether the email went out.
    fetch('/enquiry', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: encode(Object.assign({ mailResult: result, page: form.dataset.page || '' }, data)) }).catch(() => {});
    button.disabled = false;
    if (result === 'Success') {
      form.reset();
      if (status) {
        status.querySelector('p').textContent = 'Thank you. Your message has been received.';
        status.hidden = false;
        status.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    } else {
      error.hidden = false;
    }
  });
})();
