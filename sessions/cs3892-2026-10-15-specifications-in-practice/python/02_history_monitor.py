# FIGURE: figures/monitor_formerly.svg   (the monitor, drawn -- scripts/draw_models.py)
"""Session 15 -- a policy over the HISTORY of an agent's tool calls, checked at run time.

Dogwood (AWS, open source, August 2026) extends Cedar with `when temporal { ... }`
conditions over the events that came BEFORE the request being decided. Its
language guide defines exactly three temporal operators, all past-time, each
with a mandatory window W. At decision timepoint i, over the history 0..i:

    formerly within W p      p held at SOME j <= i with  ts(i) - ts(j) <= W
    previous within W p      i > 0, ts(i) - ts(i-1) <= W, and p held at i-1
    p since within W q       q held at some j in the window, and p held at
                             every step k in [j+1, i]

In the past-time LTL of this course these are the bounded forms of
O ("once"), Y ("yesterday") and S ("since"). (That reading is ours.)

THIS FILE IS A TOY: about forty lines that implement those three definitions
and a gateway loop. It is not Dogwood. Its job is to let you replay a trace by
hand and see why each request is allowed or denied.

Part A replays the trace AWS published with its first example policy, and
gets the same three decisions. Part B is the course's agent: one approval, and
three ways to write "delete only if approved", which decide differently. Part C is a rate limit that
counts the wrong kind of event.

Expected: the assertions at the bottom hold.
"""

HOUR = 3600


class Event:
    def __init__(self, ts, action, kind, **fields):
        self.ts, self.action, self.kind, self.fields = ts, action, kind, fields

    def __repr__(self):
        body = ", ".join("%s: %r" % kv for kv in self.fields.items())
        return "@%-5d %s::%s { %s }" % (self.ts, self.action, self.kind, body)


def is_(action, kind, **want):
    """An event predicate: this action, this kind, and these field values."""
    return lambda e: e.action == action and e.kind == kind and all(e.fields.get(k) == v for k, v in want.items())


# --- the three operators, as the language guide defines them -------------------
def in_window(h, i, j, W):
    return 0 <= h[i].ts - h[j].ts <= W


def formerly(h, i, W, p):
    return any(p(h[j]) for j in range(i + 1) if in_window(h, i, j, W))


def previous(h, i, W, p):
    return i > 0 and in_window(h, i, i - 1, W) and p(h[i - 1])


def since(h, i, W, p, q):
    return any(q(h[j]) and all(p(h[k]) for k in range(j + 1, i + 1))
               for j in range(i + 1) if in_window(h, i, j, W))


# --- the gateway: every request is decided against the history so far ----------
def gateway(offered, allow, respond=True):
    """Feed `offered` events through a gateway. A request is decided by
    allow(history, i, request). An allowed request is recorded, and (if
    `respond`) its response one second later; a denied one is recorded as an
    `error` event. Events that are not requests are recorded as they are."""
    h, decisions = [], []
    for e in offered:
        if e.kind != "request":
            h.append(e)
            continue
        h.append(e)
        ok = allow(h, len(h) - 1, e)
        decisions.append("ALLOW" if ok else "DENY")
        if not ok:
            h[-1] = Event(e.ts, e.action, "error", **e.fields)
        elif respond:
            h.append(Event(e.ts + 1, e.action, "response", **e.fields))
    return decisions, h


# ------------------------------------------------------------------------------
print("A. The trace published with Dogwood's first example")
print("   permit SellShares when temporal { formerly within 1h ApproveSale::response{")
print("       same stock, same shares, approved: true } }\n")


def sell_policy(h, i, req):
    return formerly(h, i, HOUR, is_("ApproveSale", "response", approved=True,
                                    stock=req.fields["stock"], shares=req.fields["shares"]))


AWS_TRACE = [
    Event(0, "SellShares", "request", stock="AMZN", shares=100),
    Event(1700, "ApproveSale", "response", stock="AMZN", shares=100, approved=True),
    Event(1800, "SellShares", "request", stock="AMZN", shares=100),
    Event(7200, "SellShares", "request", stock="AMZN", shares=100),
]
a, _ = gateway(AWS_TRACE, sell_policy, respond=False)
reqs = [e for e in AWS_TRACE if e.kind == "request"]
for e, d in zip(reqs, a):
    print("   %-62s -> %s" % (e, d))
assert a == ["DENY", "ALLOW", "DENY"], a          # the three decisions in the AWS post
print("   no approval yet / approved 100 s ago / the approval is 5500 s old\n")

# ------------------------------------------------------------------------------
print("B. The agent: one approval for file a (@10), an unrelated event (@15), five delete requests")
OFFERED = [
    Event(0, "Delete", "request", file="a"),
    Event(10, "Approve", "response", file="a", approved=True),
    Event(15, "Search", "response", query="old logs"),     # an unrelated tool call returns
    Event(20, "Delete", "request", file="a"),
    Event(30, "Delete", "request", file="a"),       # the same approval, used again
    Event(40, "Delete", "request", file="b"),       # nobody approved b
    Event(5000, "Delete", "request", file="a"),     # the approval is 4990 s old
]


def approved(req):
    return is_("Approve", "response", approved=True, file=req.fields["file"])


POLICIES = {
    "formerly within 1h": lambda h, i, r: formerly(h, i, HOUR, approved(r)),
    "previous within 1h": lambda h, i, r: previous(h, i, HOUR, approved(r)),
    # one-time use: no delete of this file has COMPLETED since it was approved
    "not-used since within 1h": lambda h, i, r: since(
        h, i, HOUR, lambda e: not is_("Delete", "response", file=r.fields["file"])(e), approved(r)),
}
table = {name: gateway(OFFERED, pol)[0] for name, pol in POLICIES.items()}
print("   %-26s %s" % ("request at", "  ".join("@%-5d" % e.ts for e in OFFERED if e.kind == "request")))
print("   %-26s %s" % ("file", "  ".join("%-6s" % e.fields["file"] for e in OFFERED if e.kind == "request")))
for name, ds in table.items():
    print("   %-26s %s" % (name, "  ".join("%-6s" % d for d in ds)))
assert table["formerly within 1h"] == ["DENY", "ALLOW", "ALLOW", "DENY", "DENY"]
assert table["previous within 1h"] == ["DENY", "DENY", "DENY", "DENY", "DENY"]
assert table["not-used since within 1h"] == ["DENY", "ALLOW", "DENY", "DENY", "DENY"]
print("   formerly: ONE approval covers the second delete too.")
print("   previous: an unrelated event at @15 sits between the approval and the delete.")
print("   since:    allowed once; the completed delete at @21 uses the approval up.")
print("   Nobody approved b: the policy matches on the file, not just on 'an approval'.\n")

# ------------------------------------------------------------------------------
print("C. A spending limit of 5000 per hour -- and which events to count")
TRANSFERS = [
    Event(0, "Transfer", "request", amount=2000),
    Event(1, "Transfer", "request", amount=2000),
    Event(2, "Transfer", "request", amount=2000),
    Event(3, "Transfer", "response", amount=2000),
    Event(4, "Transfer", "response", amount=2000),
    Event(5, "Transfer", "request", amount=2000),
]


def under_limit(kind):
    """forbid Transfer when the sum over `kind` events in the last hour exceeds 5000."""
    def allow(h, i, req):
        total = sum(h[j].fields["amount"] for j in range(i + 1)
                    if in_window(h, i, j, HOUR) and h[j].action == "Transfer" and h[j].kind == kind)
        return not total > 5000
    return allow


by_response, _ = gateway(TRANSFERS, under_limit("response"), respond=False)
by_request, _ = gateway(TRANSFERS, under_limit("request"), respond=False)
print("   %-40s %-11s %s" % ("policy counts", "::response", "::request"))
for e, r1, r2 in zip([e for e in TRANSFERS if e.kind == "request"], by_response, by_request):
    print("   %-40s %-11s %s" % (e, r1, r2))
assert by_response == ["ALLOW", "ALLOW", "ALLOW", "ALLOW"]     # 8000 goes out: the limit is defeated
assert by_request == ["ALLOW", "ALLOW", "DENY", "DENY"]        # the two columns of the AWS post
print("   Three requests arrive before any response does. Counting responses, the")
print("   gateway sees a total of 0 each time and lets all of them through.")
