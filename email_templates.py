import os
import base64
import mimetypes


_NOTIFICATION_TYPE_META = {
    'trip': {
        'icon': '&#9992;&#65039;',
        'label': 'Trip Alert',
        'accent': '#3B82F6',
    },
    'success': {
        'icon': '&#10004;&#65039;',
        'label': 'Update',
        'accent': '#22C55E',
    },
    'warning': {
        'icon': '&#9888;&#65039;',
        'label': 'System Notice',
        'accent': '#F59E0B',
    },
    'info': {
        'icon': '&#128161;',
        'label': 'Suggestion',
        'accent': '#8B5CF6',
    },
}


def _get_logo_cid():
    logo_path = os.path.join('static', 'img', 'logo.png')
    if os.path.exists(logo_path):
        mime_type = mimetypes.guess_type(logo_path)[0] or 'image/png'
        with open(logo_path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
        return mime_type, encoded
    return None, None


def _escape(text):
    return (text or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def build_notification_email(display_name, subject, message, notif_type='info',
                             link_url=None, link_label=None, base_url='',
                             created_at=None, manage_url=None):
    meta = _NOTIFICATION_TYPE_META.get(notif_type, _NOTIFICATION_TYPE_META['info'])
    accent = meta['accent']
    icon = meta['icon']
    label = meta['label']

    time_str = ''
    if created_at:
        time_str = created_at.strftime('%d %b %Y, %I:%M %p UTC')

    link_section = ''
    if link_url:
        safe_url = _escape(link_url)
        safe_label = _escape(link_label or 'View Details')
        link_section = f'''
        <tr><td align="center" style="padding:24px 0 8px;">
          <a href="{safe_url}" target="_blank" style="display:inline-block;padding:13px 36px;background:#FFFFFF;color:#0A0A0A;font-size:14px;font-weight:700;text-decoration:none;border-radius:8px;letter-spacing:0.02em;">{safe_label}</a>
        </td></tr>'''

    manage_link = manage_url or f'{base_url}/profile'
    safe_manage = _escape(manage_link)
    safe_name = _escape(display_name or 'Traveler')
    safe_message = _escape(message)
    safe_subject = _escape(subject)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#0A0A0A;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;-webkit-font-smoothing:antialiased;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0A0A0A;padding:32px 16px;">
<tr><td align="center">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

  <!-- Header -->
  <tr><td style="padding:0 0 28px;text-align:center;">
    <h1 style="margin:0 0 6px;font-size:24px;font-weight:800;color:#FFFFFF;letter-spacing:-0.03em;">RoutheonSkups</h1>
    <p style="margin:0;font-size:12px;color:rgba(255,255,255,0.35);font-style:italic;">Your gateway to smarter travel planning</p>
  </td></tr>

  <!-- Card -->
  <tr><td style="background:#141414;border-radius:14px;border:1px solid rgba(255,255,255,0.06);overflow:hidden;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      <!-- Accent bar -->
      <tr><td style="height:3px;background:{accent};font-size:0;line-height:0;">&nbsp;</td></tr>

      <!-- Content -->
      <tr><td style="padding:32px 32px 8px;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
          <!-- Type badge -->
          <tr><td style="padding-bottom:18px;">
            <span style="display:inline-block;padding:5px 14px;background:rgba(255,255,255,0.06);border-radius:20px;font-size:12px;font-weight:600;color:{accent};letter-spacing:0.04em;text-transform:uppercase;">{icon} {label}</span>
          </td></tr>

          <!-- Greeting -->
          <tr><td style="padding-bottom:16px;font-size:18px;font-weight:700;color:#FFFFFF;line-height:1.4;">
            Hi {safe_name},
          </td></tr>

          <!-- Message -->
          <tr><td style="padding-bottom:8px;font-size:15px;color:rgba(255,255,255,0.8);line-height:1.7;">
            {safe_message}
          </td></tr>

          {link_section}

          <!-- Time -->
          <tr><td style="padding:20px 0 0;font-size:12px;color:rgba(255,255,255,0.3);">
            {time_str}
          </td></tr>
        </table>
      </td></tr>
    </table>
  </td></tr>

  <!-- Footer -->
  <tr><td style="padding:28px 0 0;text-align:center;">
    <p style="margin:0 0 8px;font-size:11px;color:rgba(255,255,255,0.25);">
      <a href="{safe_manage}" target="_blank" style="color:rgba(255,255,255,0.35);text-decoration:underline;">Manage notification settings</a>
    </p>
    <p style="margin:0;font-size:11px;color:rgba(255,255,255,0.2);">
      &copy; 2026 RoutheonSkups &middot; AI Travel Planning
    </p>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>'''

    plain = (
        f"Hi {safe_name},\n\n"
        f"{message}\n\n"
        f"{'Link: ' + link_url if link_url else ''}\n\n"
        f"RoutheonSkups Team"
    )

    return plain, html
