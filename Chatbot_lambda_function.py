import json
import os
import re
import urllib.request
import urllib.error
import boto3
from datetime import datetime, timezone, timedelta

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table    = dynamodb.Table('Visitors')


def get_all_visitors():
    response = table.scan()
    return response.get('Items', [])

def get_ist_now():
    return datetime.now(timezone(timedelta(hours=5, minutes=30)))

def get_today_ist():
    return get_ist_now().strftime('%Y-%m-%d')

def get_yesterday_ist():
    return (get_ist_now() - timedelta(days=1)).strftime('%Y-%m-%d')


def fmt_full(v):
    return (
        f"----------------------\n"
        f"{v.get('name','?')}\n"
        f"----------------------\n"
        f"ID       : {v.get('visitor_id','?')}\n"
        f"Purpose  : {v.get('purpose','?')}\n"
        f"Status   : {v.get('status','?').capitalize()}\n"
        f"Employee : {v.get('emp_name','?')}\n"
        f"Date     : {v.get('date','?')}\n"
        f"Mobile   : {v.get('mobile','N/A') or 'N/A'}\n"
        f"Email    : {v.get('email','N/A') or 'N/A'}\n"
        f"In Time  : {v.get('in_time','-') or '-'}\n"
        f"Out Time : {v.get('out_time','-') or '-'}\n"
        f"----------------------"
    )

def fmt_line(i, v):
    return (
        f"{i+1}) {v.get('name','?')}\n"
        f"   {v.get('status','?').capitalize()} | {v.get('purpose','?')}\n"
        f"   {v.get('emp_name','?')} | {v.get('date','?')}"
    )


TYPO_MAP = {
    'vistors':'visitors','visotrs':'visitors','vistor':'visitor',
    'visiors':'visitors','vsitors':'visitors','vistiors':'visitors',
    'appoved':'approved','approvd':'approved','aprroved':'approved',
    'rejectd':'rejected','rejecteed':'rejected',
    'pendig':'pending','penidng':'pending','pneding':'pending',
    'resheduled':'rescheduled','reshuled':'rescheduled',
    'reshedueld':'rescheduled','resceduled':'rescheduled',
    'toady':'today','tday':'today','todya':'today',
    'yesturday':'yesterday','yestrday':'yesterday','ysterday':'yesterday',
    'naems':'names','nmae':'name','nmames':'names',
    'detials':'details','dteails':'details',
    'purpse':'purpose','porpose':'purpose',
    'employe':'employee','empoylee':'employee',
    'mobilr':'mobile','moblie':'mobile',
    'eamil':'email','emial':'email',
    'entha':'how many','enta':'how many',
    'numbrs':'numbers','numbr':'number',
    'hw':'how','r':'are','u':'you','ur':'your',
    'wats':'whats','wat':'what','wht':'what',
    'hlo':'hello','helo':'hello','hii':'hi','hiii':'hi',
    'metting':'meeting','meetng':'meeting','meeing':'meeting',
    'intervw':'interview','intervew':'interview',
}

def normalise(text):
    words = text.lower().strip().split()
    return " ".join(TYPO_MAP.get(w, w) for w in words)


MONTH_MAP = {
    'jan':'01','january':'01','feb':'02','february':'02',
    'mar':'03','march':'03','apr':'04','april':'04',
    'may':'05','jun':'06','june':'06','jul':'07','july':'07',
    'aug':'08','august':'08','sep':'09','sept':'09','september':'09',
    'oct':'10','october':'10','nov':'11','november':'11',
    'dec':'12','december':'12',
}

def extract_date(text):
    t = text.lower()
    m = re.search(r'\b(20\d{2})[-/](0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])\b', t)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.search(r'\b(0?[1-9]|[12]\d|3[01])[-/](0?[1-9]|1[0-2])[-/](20\d{2})\b', t)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    for word, num in MONTH_MAP.items():
        m = re.search(rf'\b{word}\s+(0?[1-9]|[12]\d|3[01])(?:\s+(20\d{{2}}))?\b', t)
        if m:
            day  = int(m.group(1))
            year = m.group(2) if m.group(2) else str(get_ist_now().year)
            return f"{year}-{num}-{day:02d}"
        m = re.search(rf'\b(0?[1-9]|[12]\d|3[01])\s+{word}(?:\s+(20\d{{2}}))?\b', t)
        if m:
            day  = int(m.group(1))
            year = m.group(2) if m.group(2) else str(get_ist_now().year)
            return f"{year}-{num}-{day:02d}"
    return None


# Known purpose keywords — extend this list as needed
PURPOSE_KEYWORDS = [
    'meeting', 'interview', 'official work', 'new joining',
    'delivery', 'vendor', 'personal', 'training', 'audit',
    'testing', 'meet'
]

def extract_purpose_filter(m):
    """Return the purpose keyword found in the message, or None."""
    for p in sorted(PURPOSE_KEYWORDS, key=len, reverse=True):
        if p in m:
            return p
    return None


def handle_query(msg, visitors, today):
    m         = normalise(msg)
    yesterday = get_yesterday_ist()

    # ── How are you ──
    howareyou_phrases = ['how are you', 'how are u', 'how r you', 'how r u', 'how are', 'hows u', 'hows you']
    if any(phrase in m for phrase in howareyou_phrases):
        return "I'm doing well, thank you! How can I help you?"

    # ── Greetings ──
    greeting_phrases = [
        'hello', 'hi', 'hey', 'hii', 'helo', 'hlo',
        'good morning', 'good afternoon', 'good evening',
        'whats up', "what's up", 'sup'
    ]
    if any(phrase in m for phrase in greeting_phrases):
        return "Hello! How can I help you?"

    # ── Small talk ──
    if len(m.split()) <= 4 and any(w in m for w in [
        'thanks', 'thank you', 'thank u', 'ok thanks', 'okay thanks',
        'bye', 'goodbye', 'see you', 'take care', 'good night',
        'cool', 'great', 'nice', 'awesome'
    ]):
        return "You're welcome! Let me know if you need anything else."

    # ── Email address search (fires before scope/filter logic) ──
    email_in_msg = re.search(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', msg)
    if email_in_msg:
        search_email = email_in_msg.group(0).lower()
        matches = [v for v in visitors if (v.get('email') or '').lower() == search_email]
        if matches:
            if len(matches) == 1:
                return f"Visitor Found:\n\n{fmt_full(matches[0])}"
            lines = [f"{len(matches)} visitor(s) with email '{search_email}':\n"]
            for i, v in enumerate(matches):
                lines.append(fmt_line(i, v))
            return "\n\n".join(lines)
        return f"No visitor found with email '{search_email}'."

    # ── Mobile number lookup (10-digit number) ──
    phone_match = re.search(r'\b(\d{10})\b', msg)
    if phone_match:
        phone = phone_match.group(1)
        matches = [v for v in visitors if (v.get('mobile') or '').replace(' ','') == phone]
        if matches:
            if len(matches) == 1:
                return f"Visitor Found:\n\n{fmt_full(matches[0])}"
            lines = [f"{len(matches)} visitor(s) with mobile {phone}:\n"]
            for i, v in enumerate(matches):
                lines.append(fmt_line(i, v))
            return "\n\n".join(lines)
        return f"No visitor found with mobile number {phone}."

    # ── Scope detection ──
    specific_date = extract_date(msg)
    is_today      = 'today'     in m and not specific_date
    is_yesterday  = 'yesterday' in m and not specific_date

    if specific_date:
        scope = [v for v in visitors if v.get('date','') == specific_date]
        label = f"on {specific_date}"
    elif is_today:
        scope = [v for v in visitors if v.get('date','') == today]
        label = "today"
    elif is_yesterday:
        scope = [v for v in visitors if v.get('date','') == yesterday]
        label = "yesterday"
    else:
        scope = visitors
        label = "in total"

    # ── Status filter ──
    status_filter = None
    if   'pending'     in m: status_filter = 'pending'
    elif 'approved'    in m: status_filter = 'approved'
    elif 'rejected'    in m: status_filter = 'rejected'
    elif 'rescheduled' in m: status_filter = 'rescheduled'

    filtered = (
        [v for v in scope if v.get('status','').lower() == status_filter]
        if status_filter else scope
    )
    slabel = f"{status_filter} " if status_filter else ""

    # ── Purpose filter ──
    # Runs before name search so "meeting" / "interview" etc. are not treated as names
    purpose_filter = extract_purpose_filter(m)
    # Only apply if no other specific field keyword is present
    field_words = ['name','email','mobile','phone','status','in time','out time','count','how many','total','summary','stats']
    if purpose_filter and not any(w in m for w in field_words):
        purpose_scope = [
            v for v in filtered
            if purpose_filter in v.get('purpose','').lower()
        ]
        count = len(purpose_scope)
        if count == 0:
            return f"No visitors with purpose '{purpose_filter.title()}' {label}."
        noun = "visitor" if count == 1 else "visitors"
        # If message is just the keyword or "only X" or "X visitors" — list them
        header = f"Visitors with purpose '{purpose_filter.title()}' {label} ({count} {noun}):\n\n"
        lines  = [fmt_line(i, v) for i, v in enumerate(purpose_scope)]
        return header + "\n\n".join(lines)

    # ── Visitor ID lookup ──
    raw_upper = msg.strip().upper()
    id_exact  = [v for v in visitors if v.get('visitor_id','').upper() == raw_upper]
    if id_exact:
        return f"Visitor Found:\n\n{fmt_full(id_exact[0])}"

    id_token = re.search(r'\b([A-Z]{1,4}\d{2,6})\b', msg.upper())
    if id_token:
        vid   = id_token.group(1)
        match = [v for v in visitors if v.get('visitor_id','').upper() == vid]
        if match:
            return f"Details for {vid}:\n\n{fmt_full(match[0])}"
        if any(w in m for w in ['id','visitor id','find','search','details']):
            return f"No visitor found with ID '{vid}'."

    # ── Employee filter ──
    emp_names_in_db = list({v.get('emp_name','').lower() for v in visitors if v.get('emp_name')})
    matched_emp = None
    for emp in emp_names_in_db:
        first = emp.split()[0]
        if first in m.split() or emp in m:
            matched_emp = emp
            break

    if matched_emp:
        emp_scope = [v for v in scope if v.get('emp_name','').lower() == matched_emp]
        if status_filter:
            emp_scope = [v for v in emp_scope if v.get('status','').lower() == status_filter]
        if not emp_scope:
            return f"No {slabel}visitors for '{matched_emp.title()}' {label}."
        header = f"{matched_emp.title()}'s visitors {label} ({len(emp_scope)} total):\n\n"
        lines  = [fmt_line(i, v) for i, v in enumerate(emp_scope)]
        return header + "\n\n".join(lines)

    # ── Name search ──
    name_triggers = ['find','search','look up','lookup','details of','info of','about','who is']
    has_name_trigger = any(t in m for t in name_triggers)

    intent_words = [
        'show','list','display','how many','count','total','summary','stats',
        'email','mobile','phone','name','purpose','today','yesterday','pending',
        'approved','rejected','employee','number','id','in time','out time',
        'visitors','all','visitor','status','numbers','host'
    ]
    is_plain_name = (
        not specific_date
        and not any(w in m for w in intent_words)
        and not purpose_filter
        and re.match(r'^[a-z\s]+$', m.strip())
        and len(m.strip()) >= 3
    )

    if has_name_trigger or is_plain_name:
        query_name = m
        for t in sorted(name_triggers, key=len, reverse=True):
            query_name = query_name.replace(t,'').strip()
        for noise in ['visitor','the','a','an','me','please','details','info','of','about']:
            query_name = re.sub(rf'\b{noise}\b','',query_name).strip()
        if query_name:
            matches = [v for v in visitors if query_name in v.get('name','').lower()]
            if matches:
                if len(matches) == 1:
                    return f"Visitor Found:\n\n{fmt_full(matches[0])}"
                lines = [f"{len(matches)} match(es) for '{query_name.title()}':\n"]
                for i, v in enumerate(matches):
                    lines.append(fmt_line(i, v))
                return "\n\n".join(lines)
            return f"No visitor found matching '{query_name.title()}'."

    # ── EMAIL ──
    if any(w in m for w in ['email','mail id','e-mail','emails']):
        if not filtered:
            return f"No {slabel}visitors {label}."
        header = f"Emails - {slabel}visitors {label} ({len(filtered)}):\n\n"
        lines  = [f"{i+1}) {v.get('name','?')}\n   {v.get('email','N/A') or 'N/A'}"
                  for i, v in enumerate(filtered)]
        return header + "\n\n".join(lines)

    # ── MOBILE ──
    if any(w in m for w in ['mobile','phone','contact number','number','numbers']):
        if not filtered:
            return f"No {slabel}visitors {label}."
        header = f"Mobiles - {slabel}visitors {label} ({len(filtered)}):\n\n"
        lines  = [f"{i+1}) {v.get('name','?')}\n   {v.get('mobile','N/A') or 'N/A'}"
                  for i, v in enumerate(filtered)]
        return header + "\n\n".join(lines)

    # ── NAMES ──
    if 'name' in m and not any(w in m for w in ['how many','count','total','number']):
        if not filtered:
            return f"No {slabel}visitors {label}."
        header = f"Names - {slabel}visitors {label} ({len(filtered)}):\n"
        lines  = [f"{i+1}) {v.get('name','?')}" for i, v in enumerate(filtered)]
        return header + "\n".join(lines)

    # ── IN TIME ──
    if any(w in m for w in ['in time','check in','entry time','intime']):
        if not filtered:
            return f"No {slabel}visitors {label}."
        header = f"In Times - {slabel}visitors {label} ({len(filtered)}):\n\n"
        lines  = [f"{i+1}) {v.get('name','?')}\n   {v.get('in_time','-') or '-'}"
                  for i, v in enumerate(filtered)]
        return header + "\n\n".join(lines)

    # ── OUT TIME ──
    if any(w in m for w in ['out time','check out','exit time','outtime']):
        if not filtered:
            return f"No {slabel}visitors {label}."
        header = f"Out Times - {slabel}visitors {label} ({len(filtered)}):\n\n"
        lines  = [f"{i+1}) {v.get('name','?')}\n   {v.get('out_time','-') or '-'}"
                  for i, v in enumerate(filtered)]
        return header + "\n\n".join(lines)

    # ── PURPOSE ──
    if 'purpose' in m:
        if not filtered:
            return f"No {slabel}visitors {label}."
        header = f"Purposes - {slabel}visitors {label} ({len(filtered)}):\n\n"
        lines  = [f"{i+1}) {v.get('name','?')}\n   {v.get('purpose','?')}"
                  for i, v in enumerate(filtered)]
        return header + "\n\n".join(lines)

    # ── STATUS ──
    if 'status' in m:
        if not filtered:
            return f"No {slabel}visitors {label}."
        header = f"Status - {slabel}visitors {label} ({len(filtered)}):\n\n"
        lines  = [f"{i+1}) {v.get('name','?')}\n   {v.get('status','?').capitalize()}"
                  for i, v in enumerate(filtered)]
        return header + "\n\n".join(lines)

    # ── COUNT ──
    if any(w in m for w in ['how many','count','total','number of']):
        count = len(filtered)
        noun  = "visitor" if count == 1 else "visitors"
        return f"{count} {slabel}{noun} {label}."

    # ── SUMMARY ──
    if any(w in m for w in ['summary','stats','statistics','overview','report']):
        def cnt(lst, s): return len([v for v in lst if v.get('status','').lower() == s])
        tv = [v for v in visitors if v.get('date','') == today]
        yv = [v for v in visitors if v.get('date','') == yesterday]
        av = visitors
        return (
            f"Visitor Summary\n"
            f"{'-'*26}\n"
            f"Today ({today})\n"
            f"  Total       : {len(tv)}\n"
            f"  Approved    : {cnt(tv,'approved')}\n"
            f"  Pending     : {cnt(tv,'pending')}\n"
            f"  Rejected    : {cnt(tv,'rejected')}\n"
            f"  Rescheduled : {cnt(tv,'rescheduled')}\n"
            f"{'-'*26}\n"
            f"Yesterday ({yesterday})\n"
            f"  Total       : {len(yv)}\n"
            f"  Approved    : {cnt(yv,'approved')}\n"
            f"  Pending     : {cnt(yv,'pending')}\n"
            f"  Rejected    : {cnt(yv,'rejected')}\n"
            f"  Rescheduled : {cnt(yv,'rescheduled')}\n"
            f"{'-'*26}\n"
            f"All-Time    : {len(av)}\n"
            f"  Approved    : {cnt(av,'approved')}\n"
            f"  Pending     : {cnt(av,'pending')}\n"
            f"  Rejected    : {cnt(av,'rejected')}\n"
            f"  Rescheduled : {cnt(av,'rescheduled')}"
        )

    # ── LIST / SHOW (catch-all) ──
    show_words = ['show','list','display','tell','give','all','who','visitors','details','visitor']
    if any(w in m for w in show_words) or status_filter or specific_date:
        if not filtered:
            if specific_date:
                return f"No {slabel}visitors found on {specific_date}."
            return f"No {slabel}visitors {label}."
        header = f"{slabel.capitalize()}Visitors {label} ({len(filtered)} total):\n\n"
        lines  = [fmt_line(i, v) for i, v in enumerate(filtered)]
        return header + "\n\n".join(lines)

    return None


def call_ai(user_message, today):
    HF_API_KEY = os.environ.get('HF_API_KEY', '')
    if not HF_API_KEY:
        return "I can help with visitor data. Try: show today visitors, names, email, summary, or visitor ID."

    API_URL = "https://router.huggingface.co/v1/chat/completions"
    system_prompt = (
        f"You are an admin assistant for Quadrant Technologies visitor management. "
        f"Today is {today}. Be brief and clear. "
        f"NEVER invent visitor names, emails, IDs, or any visitor data. "
        f"If asked for visitor data say: "
        f"'I could not find that. Try: show today visitors | names | email | summary | visitor ID QTxxx'"
    )
    payload = json.dumps({
        "model": "meta-llama/Llama-3.1-8B-Instruct:novita",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        "max_tokens": 150,
        "temperature": 0.1
    }).encode('utf-8')

    req = urllib.request.Request(
        API_URL, data=payload,
        headers={'Authorization': f'Bearer {HF_API_KEY}', 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result['choices'][0]['message']['content']


def lambda_handler(event, context):
    CORS = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS, 'body': ''}

    try:
        body         = json.loads(event['body'])
        user_message = body.get('message', '').strip()

        if not user_message:
            return {'statusCode': 400, 'headers': CORS,
                    'body': json.dumps({'reply': 'Please send a message.'})}

        today    = get_today_ist()
        visitors = get_all_visitors()

        reply = handle_query(user_message, visitors, today)
        if reply is None:
            try:
                reply = call_ai(user_message, today)
            except Exception:
                reply = "I can help with visitor data. Try: show today visitors, names, email, summary, or visitor ID."

        return {'statusCode': 200, 'headers': CORS, 'body': json.dumps({'reply': reply})}

    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8')
        return {'statusCode': 500, 'headers': CORS,
                'body': json.dumps({'error_code': e.code, 'error_reason': e.reason, 'error_detail': err})}
    except Exception as e:
        return {'statusCode': 500, 'headers': CORS, 'body': json.dumps({'error': str(e)})}