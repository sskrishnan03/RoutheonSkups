import os
import base64
import mimetypes


_NOTIFICATION_TYPE_META = {
    'trip': {
        'icon': '&#9992;&#65039;',
        'label': 'Trip Alert',
    },
    'success': {
        'icon': '&#10004;&#65039;',
        'label': 'Update',
    },
    'warning': {
        'icon': '&#9888;&#65039;',
        'label': 'Notice',
    },
    'info': {
        'icon': '&#128161;',
        'label': 'Suggestion',
    },
}


def _get_logo_cid():
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img', 'logo.png')
    if os.path.exists(logo_path):
        mime_type = mimetypes.guess_type(logo_path)[0] or 'image/png'
        with open(logo_path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
        return mime_type, encoded
    return None, None


def _escape(text):
    return (text or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _build_detail_row(label, value):
    if not value:
        return ''
    return (
        f'<tr>'
        f'<td style="padding:7px 0;font-size:13px;font-weight:600;color:rgba(255,255,255,0.4);width:140px;vertical-align:top;">{_escape(label)}</td>'
        f'<td style="padding:7px 0;font-size:13px;color:rgba(255,255,255,0.85);">{_escape(str(value))}</td>'
        f'</tr>'
    )


def build_notification_email(display_name, subject, message, notif_type='info',
                             link_url=None, link_label=None, base_url='',
                             created_at=None, manage_url=None,
                             details=None, hero_title=None):
    meta = _NOTIFICATION_TYPE_META.get(notif_type, _NOTIFICATION_TYPE_META['info'])
    icon = meta['icon']
    label = meta['label']

    time_str = ''
    if created_at:
        time_str = created_at.strftime('%d %b %Y, %I:%M %p UTC')

    logo_mime, logo_b64 = _get_logo_cid()
    if logo_mime and logo_b64:
        logo_html = f'<img src="data:{logo_mime};base64,{logo_b64}" alt="RoutheonSkups" style="height:40px;width:auto;display:block;margin:0 auto;">'
    else:
        logo_html = '<h1 style="margin:0;font-size:24px;font-weight:800;color:#FFFFFF;letter-spacing:-0.03em;">RoutheonSkups</h1>'

    title = _escape(hero_title or subject or 'Notification')
    safe_name = _escape(display_name or 'Traveler')
    safe_message = _escape(message)

    details_html = ''
    if details:
        rows = ''
        for key, val in details.items():
            rows += _build_detail_row(key, val)
        if rows:
            details_html = f'''
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:16px;background:rgba(255,255,255,0.03);border-radius:10px;border:1px solid rgba(255,255,255,0.05);padding:4px;">
              <tr><td style="padding:12px 16px;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                  {rows}
                </table>
              </td></tr>
            </table>'''

    safe_url = _escape(link_url) if link_url else ''
    safe_label = _escape(link_label or 'View on RoutheonSkups')
    link_html = ''
    if safe_url:
        link_html = f'''
        <tr><td style="padding:20px 0 0;">
          <a href="{safe_url}" target="_blank" style="display:inline-block;padding:11px 28px;background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.9);font-size:13px;font-weight:600;text-decoration:none;border-radius:8px;border:1px solid rgba(255,255,255,0.1);">{safe_label} &rarr;</a>
        </td></tr>'''

    manage_link = manage_url or f'{base_url}/profile'
    safe_manage = _escape(manage_link)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#000000;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;-webkit-font-smoothing:antialiased;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#000000;padding:32px 16px;">
<tr><td align="center">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

  <!-- Logo -->
  <tr><td style="padding:0 0 8px;text-align:center;">
    {logo_html}
  </td></tr>
  <tr><td style="padding:0 0 28px;text-align:center;">
    <p style="margin:0;font-size:12px;color:rgba(255,255,255,0.3);font-style:italic;">Your gateway to smarter travel planning</p>
  </td></tr>

  <!-- Card -->
  <tr><td style="background:#0A0A0A;border-radius:14px;border:1px solid rgba(255,255,255,0.06);overflow:hidden;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">

      <!-- Content -->
      <tr><td style="padding:28px 28px 8px;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0">

          <!-- Type badge -->
          <tr><td style="padding-bottom:14px;">
            <span style="display:inline-block;padding:4px 12px;background:rgba(255,255,255,0.05);border-radius:20px;font-size:11px;font-weight:600;color:rgba(255,255,255,0.4);letter-spacing:0.04em;text-transform:uppercase;">{icon} {_escape(label)}</span>
          </td></tr>

          <!-- Greeting -->
          <tr><td style="padding-bottom:6px;font-size:17px;font-weight:700;color:#FFFFFF;line-height:1.4;">
            Hi {safe_name},
          </td></tr>

          <!-- Title -->
          <tr><td style="padding-bottom:12px;font-size:15px;font-weight:700;color:rgba(255,255,255,0.9);line-height:1.4;">
            {title}
          </td></tr>

          <!-- Message -->
          <tr><td style="padding-bottom:8px;font-size:14px;color:rgba(255,255,255,0.65);line-height:1.7;">
            {safe_message}
          </td></tr>

          <!-- Details table -->
          {details_html}

          <!-- Link -->
          {link_html}

          <!-- Time -->
          <tr><td style="padding:20px 0 0;font-size:11px;color:rgba(255,255,255,0.2);">
            {time_str}
          </td></tr>
        </table>
      </td></tr>
    </table>
  </td></tr>

  <!-- Footer -->
  <tr><td style="padding:24px 0 0;text-align:center;">
    <p style="margin:0 0 6px;font-size:11px;color:rgba(255,255,255,0.2);">
      <a href="{safe_manage}" target="_blank" style="color:rgba(255,255,255,0.3);text-decoration:underline;">Manage notification settings</a>
    </p>
    <p style="margin:0;font-size:11px;color:rgba(255,255,255,0.15);">
      &copy; 2026 RoutheonSkups &middot; AI Travel Planning
    </p>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>'''

    plain = f"Hi {safe_name},\n\n{message}\n\n{'Details: ' + str(details) if details else ''}\n{'Link: ' + link_url if link_url else ''}\n\nRoutheonSkups Team"

    return plain, html
