"""Builds the illustrated admin user guide (PDF).

    python tools/build_guide.py <folder with the screenshots> <output.pdf>

The screenshots come from a local copy of the site (see tests/README or the project README).
"""
import os, sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle)
from PIL import Image as PILImage

SHOTS, OUT = sys.argv[1], sys.argv[2]
LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'media', 'logo.png')
ORANGE, DEEP, INK, MUTED, SOFT, LINE = (colors.HexColor(c) for c in ('#E19F26', '#8F5B08', '#2B2824', '#6C675F', '#FFF6E5', '#EFE7D8'))
W, H = A4
MARGIN = 18 * mm
FRAME_W = W - 2 * MARGIN

base = dict(fontName='Helvetica', textColor=INK)
S = {
    'cover': ParagraphStyle('cover', fontName='Times-Roman', fontSize=44, leading=48, textColor=ORANGE, alignment=1),
    'cover2': ParagraphStyle('cover2', fontName='Helvetica-Bold', fontSize=22, leading=28, textColor=INK, alignment=1),
    'cover3': ParagraphStyle('cover3', fontName='Helvetica', fontSize=12, leading=18, textColor=MUTED, alignment=1),
    'h1': ParagraphStyle('h1', fontName='Helvetica-Bold', fontSize=19, leading=24, textColor=INK, spaceBefore=4, spaceAfter=7),
    'h2': ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=12.5, leading=16, textColor=DEEP, spaceBefore=9, spaceAfter=4),
    'p': ParagraphStyle('p', fontSize=10.5, leading=15.5, spaceAfter=6, **base),
    'step': ParagraphStyle('step', fontSize=10.5, leading=15.5, leftIndent=17, firstLineIndent=-17, spaceAfter=3.5, **base),
    'note': ParagraphStyle('note', fontSize=10, leading=14.5, **base),
    'cap': ParagraphStyle('cap', fontName='Helvetica-Oblique', fontSize=8.5, leading=11, textColor=MUTED, alignment=1, spaceAfter=8),
    'cell': ParagraphStyle('cell', fontSize=9.8, leading=13.5, **base),
    'cellb': ParagraphStyle('cellb', fontName='Helvetica-Bold', fontSize=9.8, leading=13.5, textColor=INK),
    'toc': ParagraphStyle('toc', fontSize=11, leading=19, **base),
}

def page_frame(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(ORANGE); canvas.setLineWidth(1.4); canvas.line(MARGIN, H - 13 * mm, W - MARGIN, H - 13 * mm)
        canvas.setFont('Helvetica', 8.5); canvas.setFillColor(MUTED)
        canvas.drawString(MARGIN, H - 11 * mm, 'VARTEC website admin: user guide')
        canvas.drawRightString(W - MARGIN, 10 * mm, f'Page {doc.page}')
    canvas.restoreState()

def compact(name, max_px=1500):
    """A JPEG copy of a screenshot, so the guide stays a few megabytes."""
    src, dst = os.path.join(SHOTS, name + '.png'), os.path.join(SHOTS, '_' + name + '.jpg')
    with PILImage.open(src) as im:
        im = im.convert('RGB')
        if im.width > max_px:
            im = im.resize((max_px, round(im.height * max_px / im.width)), PILImage.LANCZOS)
        im.save(dst, quality=84, optimize=True)
    return dst

def shot(name, caption=None, max_h=88, width=None):
    path = compact(name)
    with PILImage.open(path) as im:
        ratio = im.height / im.width
    w = min(width or FRAME_W, FRAME_W)
    if w * ratio > max_h * mm:
        w = max_h * mm / ratio
    img = Image(path, width=w, height=w * ratio)
    box = Table([[img]], colWidths=[w + 2], hAlign='CENTER')
    box.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.6, LINE), ('LEFTPADDING', (0, 0), (-1, -1), 1), ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                             ('TOPPADDING', (0, 0), (-1, -1), 1), ('BOTTOMPADDING', (0, 0), (-1, -1), 1)]))
    return [Spacer(1, 3), box, Paragraph(caption, S['cap']) if caption else Spacer(1, 8)]

def steps(*items):
    return [Paragraph(f'<b><font color="#8F5B08">{n}.</font></b>&nbsp;&nbsp;{text}', S['step']) for n, text in enumerate(items, 1)]

def note(text, title='Good to know'):
    t = Table([[Paragraph(f'<b>{title}.</b> {text}', S['note'])]], colWidths=[FRAME_W])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), SOFT), ('LINEBEFORE', (0, 0), (0, -1), 3, ORANGE),
                           ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 10), ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7)]))
    return [Spacer(1, 3), t, Spacer(1, 8)]

def table(rows, widths, head=True):
    data = [[Paragraph(str(c), S['cellb'] if (head and r == 0) or (not head and i == 0) else S['cell']) for i, c in enumerate(row)] for r, row in enumerate(rows)]
    t = Table(data, colWidths=[w * FRAME_W for w in widths], repeatRows=1 if head else 0)
    style = [('GRID', (0, 0), (-1, -1), 0.5, LINE), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 7), ('RIGHTPADDING', (0, 0), (-1, -1), 7),
             ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]
    if head:
        style.append(('BACKGROUND', (0, 0), (-1, 0), SOFT))
    t.setStyle(TableStyle(style))
    return [t, Spacer(1, 8)]

H1 = lambda text: Paragraph(text, S['h1'])
H2 = lambda text: Paragraph(text, S['h2'])
P = lambda text: Paragraph(text, S['p'])

story = []
# ---------------------------------------------------------------- cover
story += [Spacer(1, 42 * mm), Image(LOGO, width=46 * mm, height=46 * mm, hAlign='CENTER'), Spacer(1, 14 * mm),
          Paragraph('Website admin', S['cover2']), Spacer(1, 3 * mm), Paragraph('User guide', S['cover']), Spacer(1, 12 * mm),
          Paragraph('How to change the text and pictures on the VARTEC website,<br/>add projects, read enquiries and keep the admin secure.', S['cover3']),
          Spacer(1, 60 * mm), Paragraph('For editors of the website. No technical knowledge needed.', S['cover3']), PageBreak()]

# ---------------------------------------------------------------- contents + the one idea
contents = ['The one thing to remember', 'Signing in', 'The dashboard and the menu', 'Changing the home page', 'Preview and publish', 'Editing a service or project',
            'Adding a new project or service', 'Pictures and the licence rule', 'Other pages, such as a privacy policy', 'Wording: menu names, buttons, form labels',
            'Enquiries', 'Settings', 'Passwords, two-step sign-in and editors', 'Going back to an earlier version', 'Using the admin on a phone', 'If something goes wrong']
story += [H1('Contents'), *[Paragraph(f'<font color="#8F5B08"><b>{n}</b></font>&nbsp;&nbsp;&nbsp;{t}', S['toc']) for n, t in enumerate(contents, 1)], Spacer(1, 10)]

story += [H1('1. The one thing to remember'),
          P('Nothing you do in the admin reaches the public website until you press <b>Publish to website</b>. Every change goes through the same three steps:')]
flow = Table([[Paragraph('<b>1. Edit</b><br/>Change something and press <b>Save draft</b>. Visitors still see the old version.', S['cell']),
               Paragraph('<b>2. Preview</b><br/>Press <b>Preview</b> to see the website with your changes. Only you can see it.', S['cell']),
               Paragraph('<b>3. Publish</b><br/>Press <b>Publish to website</b>. Your changes are live at once.', S['cell'])]], colWidths=[FRAME_W / 3] * 3)
flow.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), SOFT), ('BOX', (0, 0), (-1, -1), 0.8, ORANGE), ('INNERGRID', (0, 0), (-1, -1), 0.8, ORANGE),
                          ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 10), ('TOPPADDING', (0, 0), (-1, -1), 9), ('BOTTOMPADDING', (0, 0), (-1, -1), 9), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
story += [flow, Spacer(1, 8), P('So you can try things freely. If you do not like a change, discard it. If you published something by mistake, you can go back to an earlier version (section 14).'), PageBreak()]

# ---------------------------------------------------------------- signing in
story += [H1('2. Signing in'),
          *steps('Open your website address followed by <b>/admin/</b>, for example <font face="Courier">https://vartec.global/admin/</font>.',
                 'Type your username and password and press <b>Sign in</b>.',
                 'If two-step sign-in is on for your account, type the six-digit code from the authenticator app on your phone.'),
          *shot('01-signin', 'The sign-in screen', max_h=70),
          *note('After several wrong attempts the admin locks sign-in for 15 minutes. If you have forgotten your password, press <b>Forgotten your password?</b> and use the recovery code (section 13), or ask another editor to remove your account and add you again. You are signed out automatically after two hours without activity.'),
          H2('The very first sign-in'),
          P('On a brand-new installation the admin asks you to create the first account. It asks for a <b>setup code</b>, which proves you manage the hosting. Whoever installed the website gives you this code. Choose a username and a password of at least 10 characters.'),
          PageBreak()]

# ---------------------------------------------------------------- dashboard
story += [H1('3. The dashboard and the menu'),
          P('After signing in you see the dashboard. The menu on the left is on every screen. The bar at the top always tells you whether you have changes that are not live yet.'),
          *shot('02-dashboard', 'The dashboard. The orange box warns about pictures with no licence on record.', max_h=92),
          *table([['Menu', 'What you do there'],
                  ['Home page', 'Banner text and photos, About Us, the "what we do" cards, section headings, contact block.'],
                  ['Services / Projects', 'Edit, add, hide, delete and re-order the service and project pages.'],
                  ['Other pages', 'Pages that are neither, such as a privacy policy or terms.'],
                  ['Images and video', 'The picture library: upload, describe, record the licence, remove.'],
                  ['Wording', 'Short fixed texts: menu names, button texts, form labels.'],
                  ['Enquiries', 'A copy of every message sent through the contact form.'],
                  ['Settings', 'Phone, email, footer, search-engine text, help chat, your password, editors.'],
                  ['Help', 'Short instructions, and this guide.']], [0.27, 0.73]),
          PageBreak()]

# ---------------------------------------------------------------- home page
story += [H1('4. Changing the home page'),
          *steps('Press <b>Home page</b> in the menu. The boxes are in the same order as the sections on the home page.',
                 'Change any text. The small grey notes tell you where each text appears.',
                 'Press <b>Save draft</b> at the bottom.'),
          *shot('03-home', 'Home page editor: section 1 is the banner', max_h=86),
          H2('Banner photos'),
          P('The banner at the top of the home page fades through the photos listed under <b>Banner pictures</b>. The first one is shown first.'),
          *steps('Press <b>Choose image</b> under a photo to swap it, or <b>Add banner picture</b> to add one.',
                 'Use the small arrows to change the order, and the bin to remove a photo from the banner.',
                 'Wide landscape photos work best. Avoid photos with text in them.'),
          *shot('04-home-banner-photos', 'Banner pictures: arrows change the order, the bin removes one', max_h=70),
          PageBreak()]

# ---------------------------------------------------------------- preview / publish
story += [H1('5. Preview and publish'),
          P('After you save, a green message confirms it, and the bar at the top changes to <b>You have changes that are not live yet</b>.'),
          *shot('06-topbar-draft', 'The top bar when you have unpublished changes', max_h=18),
          *steps('Press <b>Preview</b>. The website opens in a new tab with your changes and a strip at the bottom saying it is a preview. Visitors cannot see this.',
                 'Check the page on a wide window and a narrow one (drag the window narrower to imitate a phone).',
                 'Happy? Go back to the admin tab and press <b>Publish to website</b>.'),
          *shot('08-preview', 'A preview. The strip at the bottom shows that only you can see it.', max_h=80),
          H2('Changed your mind?'),
          P('On the dashboard, press <b>Discard changes</b>. Every unpublished change is thrown away and the admin matches the live website again. This cannot be undone.'),
          *shot('07-dashboard-draft', 'Dashboard with unpublished changes: Preview, Publish or Discard', max_h=62),
          PageBreak()]

# ---------------------------------------------------------------- service / project
story += [H1('6. Editing a service or project'),
          *steps('Press <b>Services</b> or <b>Projects</b>. You see the list of pages.', 'Press a page name, or <b>Edit</b>, to open it.'),
          *shot('09-projects', 'The list of projects', max_h=74),
          *table([['On the list you can', 'How'],
                  ['Change the order', 'Use the up and down arrows, then press <b>Save order and visibility</b>. The order is used in the menu and on the home page.'],
                  ['Hide a page without deleting it', 'Switch off <b>Shown on website</b>, then <b>Save order and visibility</b>.']], [0.34, 0.66]),
          H2('Inside a page'),
          P('The top box holds the <b>title</b>, the <b>introduction</b> and the <b>card picture</b> (the picture on the home page card). Below it are the <b>sections</b>.'),
          *shot('10-page-top', 'The top of a page: title, introduction, card picture', max_h=78),
          PageBreak(),
          P('A <b>section</b> is one block on the page: a heading, some text and an optional picture. Sections appear on the page in the order shown, text and picture swapping sides each time.'),
          *shot('11-page-section', 'A section, with the buttons to add bullet points, paragraphs and more sections', max_h=84),
          *table([['To', 'Do this'],
                  ['Add a list', 'Press <b>Add bullet point</b> inside the section, once for each point. Use the drop-down to turn a line into a numbered point or a small heading.'],
                  ['Add another block', 'Press <b>Add section</b> at the bottom.'],
                  ['Move a section or a point', 'Use its up and down arrows.'],
                  ['Remove a section or a point', 'Press its bin. Removing a whole section asks you to confirm.'],
                  ['Change the picture', 'Press <b>Choose image</b> (section 8).']], [0.3, 0.7]),
          H2('The wide picture behind the title'),
          P('Open the <b>Banner picture</b> box to choose it. If you leave it empty, the page uses its first section picture.'),
          *shot('13b-banner', 'Banner picture box (closed until you click it)', max_h=46),
          P('Always finish with <b>Save draft</b>, then preview and publish.'),
          PageBreak()]

# ---------------------------------------------------------------- new project
story += [H1('7. Adding a new project or service'),
          *steps('Open <b>Projects</b> (or <b>Services</b>) and press <b>Add a project</b>.',
                 'Give it a <b>title</b> and a short <b>introduction</b>. The introduction is also shown on the home page card.',
                 'Choose a <b>card picture</b>.',
                 'Press <b>Add section</b> for each thing you want to show: a heading, a few sentences and a photo.',
                 'Press <b>Save draft</b>, preview, publish. The page appears in the menu and on the home page automatically.'),
          *shot('14-new-project', 'A new, empty project', max_h=58),
          *note('Say something only you can say: where the project is, its size, the year, what VARTEC did and the result. Three to five real sentences do more for visitors and for Google than a paragraph of general claims.', 'Writing tip'),
          H2('Search engines and web address'),
          P('At the bottom of every page is a box called <b>Search engines and web address</b>. You can leave it empty: the page title and introduction are used. To write your own, keep the title to about 60 characters and the description to about 155. The counter under each box helps.'),
          *shot('13-page-search', 'Search engine text and web address for a page', max_h=44),
          *note('Do not change the web address of a page that is already published unless you must. Links from other websites and from Google would stop working.', 'Careful'),
          H2('Deleting a page'),
          P('Open the page and press <b>Delete this project</b> at the very bottom. It stays on the live website until you publish. To bring it back before publishing, discard your changes.'),
          PageBreak()]

# ---------------------------------------------------------------- pictures
story += [H1('8. Pictures and the licence rule'),
          *note('Only use pictures you took yourself or hold a licence for. Pictures copied from Google, news sites or stock libraries without paying can lead to a copyright claim and a bill. The admin marks every picture that has no licence on record.', 'The rule'),
          H2('Choosing a picture for a page'),
          *steps('Wherever a picture can go, press <b>Choose image</b>. The library opens.', 'Click a picture to use it, or upload a new one at the top of the same window.',
                 'When you upload, say <b>what it shows</b>, <b>where it is from</b> and your <b>right to use it</b>.'),
          *shot('12-picker', 'The picture chooser. Red labels mark pictures with no licence on record.', max_h=84),
          H2('The library'),
          P('<b>Images and video</b> shows everything in the library. Large pictures are made smaller automatically (1600 pixels wide), so you can upload straight from a phone or camera. Videos must be MP4.'),
          *shot('15-media', 'Images and video: upload at the top, the library below', max_h=78),
          PageBreak(),
          *table([['Tab', 'Shows'], ['All', 'Every file.'], ['No licence on record', 'Pictures to replace, or to record a licence for once you hold one.'], ['Not used on any page', 'Files you can safely remove.']], [0.3, 0.7]),
          H2('Recording where a picture came from'),
          *steps('Press <b>Details</b> under a picture.', 'Fill in <b>What does it show?</b> (this is read out by screen readers and used by Google) and <b>Where is it from?</b>.',
                 'Under <b>Right to use it</b> choose <b>Our own photo</b>, <b>Licensed</b> (only if you hold the receipt or written permission), <b>No licence</b> or <b>Not sure</b>.', 'Press <b>Save details</b>.'),
          *shot('17-media-details', 'Details of one picture, including where it is used', max_h=74),
          H2('Removing a picture'),
          *steps('First take it off every page that uses it. The details screen lists where it is used.', 'Open the <b>Not used on any page</b> tab and press <b>Remove</b>.', 'Publish.'),
          *note('Once you publish, the removed file is deleted from the server and can no longer be opened at its old address. This matters if a picture has to come down because of a copyright complaint.'),
          PageBreak()]

# ---------------------------------------------------------------- other pages
story += [H1('9. Other pages, such as a privacy policy'),
          P('Use <b>Other pages</b> for anything that is not a service or a project: a privacy policy, terms, accreditations. Each published page gets a link at the bottom of every page of the website.'),
          *steps('Press <b>Other pages</b>, then <b>Add a page</b>.', 'Type the title, for example "Privacy policy".', 'Press <b>Add section</b> for each part of the text and fill in the heading and text.', 'Save, preview and publish.'),
          *shot('19-new-page', 'A new page under Other pages', max_h=58),
          *note('The contact form collects names, email addresses and phone numbers, so the website should have a privacy policy saying who holds that information and why. The wording must come from the company; this guide cannot supply it.'),
          H1('10. Wording: menu names, buttons, form labels'),
          P('<b>Wording</b> holds the short fixed texts. Each box shows the standard text in grey. Type your own to replace it. Clear the box to go back to the standard text.'),
          *shot('20-wording', 'Wording: grey text is the standard wording currently in use', max_h=60),
          PageBreak()]

# ---------------------------------------------------------------- enquiries
story += [H1('11. Enquiries'),
          P('When a visitor sends the contact form, the message is emailed exactly as before, and a copy is kept under <b>Enquiries</b>. The number next to Enquiries in the menu counts the new ones.'),
          *shot('21-enquiries', 'An enquiry: reply by email, mark as done, or delete', max_h=62),
          *table([['Button', 'What it does'], ['Reply by email', 'Opens your email program with the visitor\'s address filled in.'], ['Mark as done', 'Clears it from the counter. It stays in the list.'],
                  ['Delete', 'Removes the copy from the admin. The email you received is not affected.']], [0.27, 0.73]),
          *note('If an entry says "the email may not have been sent", the copy was saved but the email step reported a problem. Reply from here so the visitor is not left waiting, and tell whoever looks after the website.'),

          H1('12. Settings'),
          P('The first part of <b>Settings</b> is saved as a draft like everything else: change it, press <b>Save draft</b>, preview, publish.'),
          *shot('22-settings', 'Settings: contact details and footer', max_h=76),
          *table([['Box', 'What it controls'],
                  ['Contact details', 'The phone number, email address and office hours shown on the website. Changing the email here does <b>not</b> change where contact-form messages are delivered.'],
                  ['Footer', 'The short description, the copyright line (write {year} for the current year) and the logo.'],
                  ['Search engines', 'The home page title and description shown in Google, and the optional Google Search Console code.'],
                  ['Social media links', 'Optional links shown at the bottom of every page.'],
                  ['Help chat', 'Switch the chat button on or off and edit its answers.']], [0.27, 0.73]),
          PageBreak(),
          H2('Help chat answers'),
          P('Each answer has a <b>topic</b>, the <b>words to listen for</b> (separated by commas) and the <b>answer</b>. The chat gives the first answer whose words appear in the visitor\'s question, so put the most specific answers first. The first three topics appear as quick buttons. Where an answer says "contact us" or "contact our team", the chat turns those words into a link to the contact form.'),
          *shot('23-settings-chat', 'Help chat settings', max_h=92),
          H2('Google Search Console'),
          P('Search Console is Google\'s free tool that shows how the site appears in search. When Google asks you to prove you own the site with an "HTML tag", paste that whole line into <b>Google Search Console verification code</b>, save and publish.'),
          *shot('24-settings-search', 'Search engine settings', max_h=58),
          PageBreak()]

# ---------------------------------------------------------------- security
story += [H1('13. Passwords, two-step sign-in and editors'),
          P('These three boxes are at the bottom of <b>Settings</b>. They take effect immediately; there is nothing to publish.'),
          H2('Change your password'),
          P('Type your current password and a new one of at least 10 characters. Avoid your username or the word "vartec" in it. Changing your password signs you out on every other computer and phone.'),
          *shot('25-password', None, max_h=30),
          H2('Two-step sign-in (recommended)'),
          P('With two-step sign-in, a stolen password alone cannot open the admin. You need a free authenticator app on your phone, such as Google Authenticator or Microsoft Authenticator.'),
          *steps('Press <b>Set up two-step sign-in</b>.', 'In the app choose "add account" and "enter a setup key", then type the key shown on the screen.',
                 'Type the six-digit code the app shows and press <b>Turn on</b>.', 'From now on, signing in asks for your password and then the current code from the app.'),
          *shot('26-two-step', None, max_h=26),
          *note('If you lose the phone, ask another editor to remove your account and add you again. Keep at least two editors so nobody is locked out.'),
          H2('Forgotten password and the recovery code'),
          P('Under <b>Recovery code</b>, press <b>Create a recovery code</b> and confirm with your password. The code is shown <b>once</b>: write it down and keep it somewhere private. If an editor later forgets their password, they press <b>Forgotten your password?</b> on the sign-in screen and enter their username, the recovery code and a new password. Creating a new code cancels the old one.'),
          H2('Editors'),
          P('Everyone listed can edit and publish. To add someone, type a username and a temporary password for them and press <b>Add editor</b>. Give them the details privately. The first time they sign in they must choose their own password before they can do anything else. Press <b>Remove</b> next to a name to take away their access at once.'),
          *shot('27-editors', None, max_h=40),
          P('<b>Recent activity</b>, just below, lists sign-ins, failed sign-ins and publishing, so you can see who did what.'),
          PageBreak()]

# ---------------------------------------------------------------- history, phone, problems
story += [H1('14. Going back to an earlier version'),
          P('Each time you publish, the admin keeps the version that was replaced (the last 30).'),
          *steps('Open <b>Settings</b> and, at the bottom, <b>Earlier versions</b>.', 'Press <b>Restore as draft</b> next to the version you want and confirm.',
                 'It is loaded as a draft. Preview it to be sure, then publish.'),
          *note('Restoring never changes the live website by itself; you still choose when to publish. Pictures that were removed and deleted since that version are left out.'),
          H1('15. Using the admin on a phone'),
          P('Everything works on a phone. Press <b>Menu</b> at the top to open the menu.')]
phone = Table([[Image(compact('30-phone', 700), width=52 * mm, height=104 * mm), Image(compact('31-phone-menu', 700), width=52 * mm, height=104 * mm)]],
              colWidths=[60 * mm, 60 * mm], hAlign='CENTER')
phone.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
story += [phone, Paragraph('The dashboard on a phone, and the menu opened', S['cap']), PageBreak(),
          H1('16. If something goes wrong'),
          *table([['What you see', 'What to do'],
                  ['I changed something but the website looks the same.', 'You have saved a draft but not published. Press <b>Publish to website</b>. If you did publish, reload the website page.'],
                  ['I published a mistake.', 'Fix it and publish again, or restore an earlier version (section 14).'],
                  ['"Too many attempts. Wait 15 minutes."', 'Wait, then sign in again. This protects the admin from guessing.'],
                  ['I am asked to sign in again while working.', 'You were signed out after two hours without activity, or someone changed the account\'s password. Sign in again; saved drafts are kept.'],
                  ['An upload is refused.', 'Use JPG, PNG, WebP or GIF pictures and MP4 video. The upload box shows the largest file size the server accepts.'],
                  ['A picture has a red "No licence" label.', 'Replace it with your own photo, or record the licence under Details once you hold one.'],
                  ['A picture will not remove.', 'It is still used on a page. Open Details to see where, take it off those pages, then remove it.'],
                  ['Contact-form emails stopped arriving.', 'Check Enquiries: the copies are still kept there. Then tell whoever looks after the website; email delivery is set up on the hosting, not in the admin.'],
                  ['I lost my phone with the authenticator app.', 'Ask another editor to remove your account and add you again.']], [0.4, 0.6]),
          H2('Five habits that keep the site in good shape'),
          *steps('Preview before you publish, on a wide and a narrow window.', 'Use only your own or licensed pictures, and record where each came from.',
                 'Describe every picture in a few words. It helps blind visitors and Google.', 'Keep two editors, each with two-step sign-in.', 'Sign out when you finish on a shared computer.')]

doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=18 * mm, bottomMargin=16 * mm,
                      title='VARTEC website admin: user guide', author='VARTEC', subject='How to use the website admin')
doc.addPageTemplates([PageTemplate(id='page', frames=[Frame(MARGIN, 16 * mm, FRAME_W, H - 34 * mm, id='f', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=page_frame)])
doc.build(story)
print('pages written to', OUT)
