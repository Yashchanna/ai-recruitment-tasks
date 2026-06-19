import re
from typing import Dict, Any, List

KEYWORDS = {
    'user': ['user','users','account','accounts','profile'],
    'product': ['product','products','item','items','sku'],
    'order': ['order','orders','checkout','cart'],
    'payment': ['payment','payments','checkout','stripe','paypal'],
    'auth': ['auth','authentication','login','signup','oauth','jwt','authorize','authorization'],
    'image': ['image','images','photo','photos','picture','thumbnail','avatar'],
    'video': ['video','videos','mp4','movie'],
    'search': ['search','query','filter','filtering'],
    'notification': ['notify','notification','notifications','email','sms'],
    'review': ['review','rating','ratings'],
    'comment': ['comment','comments']
}

CONSTRAINT_KEYWORDS = {
    'high_availability': ['high availability','ha','uptime','redundant'],
    'realtime': ['real[- ]?time','low latency','streaming'],
    'scalable': ['scale','scalable','scaling','elastic'],
    'secure': ['secure','encryption','secure','tls','https']
}


def extract_entities(req: str) -> List[str]:
    req = req.lower()
    found = []
    for ent, toks in KEYWORDS.items():
        for t in toks:
            if re.search(r"\b" + re.escape(t) + r"\b", req):
                found.append(ent)
                break
    return found


def extract_constraints(req: str) -> List[str]:
    req = req.lower()
    found = []
    for c, toks in CONSTRAINT_KEYWORDS.items():
        for t in toks:
            if re.search(t, req):
                found.append(c)
                break
    return found


def analyze_requirements(req: str) -> Dict[str, Any]:
    """Return a structured plan with entities, constraints, modules, schemas, pseudocode and confidence."""
    entities = extract_entities(req)
    constraints = extract_constraints(req)

    # confidence heuristic: fraction of recognized tokens
    tokens = re.findall(r"\w+", req.lower())
    matched = 0
    for e in entities:
        matched += 1
    confidence = min(0.95, 0.1 + 0.2 * len(entities))

    # modules mapping
    modules = [
        {"name":"frontend","purpose":"User interface","tech":"React (Vercel)"},
        {"name":"api","purpose":"Business logic & API","tech":"FastAPI"},
        {"name":"database","purpose":"Primary relational data store","tech":"Postgres"}
    ]
    if 'auth' in entities or 'auth' in req.lower():
        modules.append({"name":"auth","purpose":"Authentication/Authorization","tech":"JWT / OAuth2"})
    if 'image' in entities or 'video' in entities:
        modules.append({"name":"storage","purpose":"Blob storage for media","tech":"S3-compatible"})
    if 'order' in entities or 'payment' in entities:
        modules.append({"name":"payments","purpose":"Payment processing","tech":"Stripe / Payment gateway"})

    # basic schemas
    schemas = {}
    for e in set(entities):
        if e=='user':
            schemas['user'] = {"id":"uuid","email":"string","name":"string","password_hash":"string","created_at":"timestamp"}
        elif e=='product':
            schemas['product'] = {"id":"uuid","name":"string","description":"text","price":"decimal","created_at":"timestamp"}
        elif e=='order':
            schemas['order'] = {"id":"uuid","user_id":"uuid","total":"decimal","status":"string","created_at":"timestamp"}
        elif e=='payment':
            schemas['payment'] = {"id":"uuid","order_id":"uuid","amount":"decimal","provider":"string","status":"string","created_at":"timestamp"}
        elif e=='image':
            schemas['image'] = {"id":"uuid","url":"string","owner_id":"uuid","metadata":"json","created_at":"timestamp"}
        elif e=='video':
            schemas['video'] = {"id":"uuid","url":"string","title":"string","duration_seconds":"int","created_at":"timestamp"}
        elif e=='comment':
            schemas['comment'] = {"id":"uuid","user_id":"uuid","content":"text","created_at":"timestamp","parent_id":"uuid?"}
        elif e=='review':
            schemas['review'] = {"id":"uuid","product_id":"uuid","user_id":"uuid","rating":"int","content":"text","created_at":"timestamp"}
        else:
            schemas[e] = {"id":"uuid","name":"string","created_at":"timestamp"}

    pseudocode = {
        "signup_flow": [
            "POST /api/signup -> validate payload",
            "hash password and store user",
            "return JWT access token"
        ],
        "create_product": [
            "POST /api/products -> auth required",
            "validate product payload",
            "insert into products table",
            "return product id"
        ]
    }

    plan = {
        "requirements": req,
        "entities": entities,
        "constraints": constraints,
        "modules": modules,
        "schemas": schemas,
        "pseudocode": pseudocode,
        "confidence": round(confidence,2)
    }
    return plan
