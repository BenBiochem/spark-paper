#!/usr/bin/env python3
"""zotero_bridge.py: read and write a local Zotero library for the spark-paper skill.

Part of the `spark-paper` skill. Talks ONLY to Zotero's built-in local API on
localhost (default http://127.0.0.1:23119/api/). Nothing leaves the machine,
no zotero.org account or API key is involved, and no paper text is sent
anywhere else.

What it does:

	find         look a paper up by DOI, title, item key, tag or collection
	pdf          print the local path of an item's PDF (so the skill can read it natively)
	annotations  dump the user's own Zotero Reader highlights and comments on an item
	add          create a library item from a DOI (metadata from Crossref), deduplicated
	push         upsert the skill's note, status tag and workbook link on an item
	uri          print zotero://select and zotero://open-pdf links for an item
	auth         one-time approval so the skill may write (a prompt appears in Zotero)
	status       is Zotero reachable, and is write access granted

How the local API works (verified against Zotero's own source, server_localAPI.js):

* Reads (GET) need no key. Zotero must be running with the local API enabled
  (Zotero Settings > Advanced > "Allow other applications on this computer to
  communicate with Zotero").
* Writes need a LOCAL API KEY, which is unrelated to zotero.org API keys. You
  get one by POSTing to /api/local/authorize; Zotero then shows a prompt with
  Allow / Always Allow / Deny. "Always Allow" stores a persistent key; "Allow"
  gives a single-use key that the first write consumes.
* Every write must also send the `Zotero-Server-ID` header (a stable id each
  response returns), or Zotero answers 428.
* Updating an existing object needs `If-Unmodified-Since-Version`.

The key and server id are stored in a 0600 file (default
~/.config/spark-paper/zotero.json; override with SPARK_PAPER_CONFIG).

Standard library only. Environment: ZOTERO_PORT (default 23119), ZOTERO_HOST
(default 127.0.0.1; only loopback addresses are accepted).

Usage:
	zotero_bridge.py status
	zotero_bridge.py auth
	zotero_bridge.py find --doi 10.1000/xyz
	zotero_bridge.py find --title "some words" | --key ABCD1234 | --tag foo | --collection NAME
	zotero_bridge.py pdf ABCD1234
	zotero_bridge.py annotations ABCD1234
	zotero_bridge.py add --doi 10.1000/xyz [--collection NAME]
	zotero_bridge.py push RECORD.json [--collection NAME] [--workbook PATH] [--write-back]
	zotero_bridge.py uri ABCD1234 [--pdf KEY --page N]
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

APP_NAME = "spark-paper"
NOTE_TAG = "spark-paper"  # marks the child note this skill owns, so push can find and update it
STATUS_TAG_PREFIX = "sp:status:"
LOOPBACK = {"127.0.0.1", "localhost", "::1"}


class ZoteroError(Exception):
	"""A readable failure from Zotero or from our own checks."""


# ---------------------------------------------------------------- configuration

def config_path():
	return os.environ.get("SPARK_PAPER_CONFIG") or os.path.expanduser(
		"~/.config/spark-paper/zotero.json")


def load_config():
	try:
		with open(config_path(), encoding="utf-8") as fh:
			return json.load(fh)
	except (OSError, ValueError):
		return {}


def save_config(cfg):
	"""Write the config 0600 from creation, never world-readable even briefly."""
	path = config_path()
	os.makedirs(os.path.dirname(path), exist_ok=True)
	fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
	with os.fdopen(fd, "w", encoding="utf-8") as fh:
		json.dump(cfg, fh, indent="\t")
	os.chmod(path, 0o600)


def base_url():
	host = os.environ.get("ZOTERO_HOST", "127.0.0.1")
	if host not in LOOPBACK:
		raise ZoteroError("ZOTERO_HOST must be a loopback address, got %r. This tool talks "
			"to a Zotero on this machine only." % host)
	port = os.environ.get("ZOTERO_PORT", "23119")
	return "http://%s:%s" % ("[::1]" if host == "::1" else host, port)


# -------------------------------------------------------------------- transport

class Client:
	"""Thin client for Zotero's local API (user library, id 0)."""

	def __init__(self):
		self.base = base_url()
		self.cfg = load_config()
		self.server_id = None

	def _request(self, method, path, body=None, headers=None, timeout=20, write=False):
		url = self.base + path
		hdrs = {"Zotero-API-Version": "3", "User-Agent": "spark-paper-skill/1.0"}
		if body is not None:
			hdrs["Content-Type"] = "application/json"
		if write:
			hdrs["Zotero-Server-ID"] = self.get_server_id()
			if self.cfg.get("key"):
				hdrs["Zotero-API-Key"] = self.cfg["key"]
		hdrs.update(headers or {})
		data = json.dumps(body).encode("utf-8") if body is not None else None
		req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
		try:
			with urllib.request.urlopen(req, timeout=timeout) as resp:
				raw = resp.read()
				self.server_id = resp.headers.get("Zotero-Server-ID") or self.server_id
				return resp.status, dict(resp.headers), raw
		except urllib.error.HTTPError as exc:
			raw = exc.read().decode("utf-8", "replace")
			raise ZoteroError(self._explain(exc.code, raw, method, path))
		except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as exc:
			raise ZoteroError("Cannot reach Zotero at %s (%s). Start Zotero and enable "
				"Settings > Advanced > 'Allow other applications on this computer to "
				"communicate with Zotero'." % (self.base, getattr(exc, "reason", exc)))

	@staticmethod
	def _explain(code, text, method, path):
		hints = {
			401: "No valid local API key. Run `zotero_bridge.py auth` and choose "
				"'Always Allow' in the Zotero prompt (a plain 'Allow' key is single-use).",
			403: "Zotero refused: the local API is off or the library is read-only. "
				"Enable Settings > Advanced > 'Allow other applications on this computer "
				"to communicate with Zotero'.",
			412: "Zotero-Server-ID changed (a different Zotero instance). Re-run `auth`.",
			428: "Zotero wanted a precondition header (server id or item version).",
			429: "Too many authorization requests; wait a minute and retry.",
		}
		hint = hints.get(code, "")
		return "%s %s -> HTTP %d: %s %s" % (method, path, code, text.strip()[:300], hint)

	def get_server_id(self):
		if not self.server_id:
			self._request("GET", "/api/")
		if not self.server_id:
			raise ZoteroError("Zotero did not return a Zotero-Server-ID header.")
		return self.server_id

	def get_json(self, path, **params):
		query = ("?" + urllib.parse.urlencode(params)) if params else ""
		_, _, raw = self._request("GET", "/api/users/0" + path + query)
		return json.loads(raw.decode("utf-8")) if raw else None

	def ping(self):
		try:
			_, _, raw = self._request("GET", "/connector/ping", timeout=4)
			return b"running" in raw
		except ZoteroError:
			return False

	def write(self, method, path, body, version=None):
		headers = {}
		if version is not None:
			headers["If-Unmodified-Since-Version"] = str(version)
		_, _, raw = self._request(method, "/api/users/0" + path, body=body,
			headers=headers, write=True)
		return json.loads(raw.decode("utf-8")) if raw else None


# ------------------------------------------------------------------- operations

def clean_doi(doi):
	doi = (doi or "").strip()
	for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "doi:"):
		if doi.lower().startswith(prefix):
			doi = doi[len(prefix):]
	return doi.strip()


def summarize(item):
	"""Flatten an item JSON to the fields the skill uses."""
	d = item.get("data", {})
	creators = "; ".join(
		(c.get("lastName", "") + ((", " + c.get("firstName", "")) if c.get("firstName") else ""))
		or c.get("name", "") for c in d.get("creators", []))
	return {
		"key": item.get("key"), "version": item.get("version"),
		"itemType": d.get("itemType"), "title": d.get("title"),
		"creators": creators, "date": d.get("date"), "doi": d.get("DOI"),
		"publication": d.get("publicationTitle"),
		"tags": [t.get("tag") for t in d.get("tags", [])],
		"collections": d.get("collections", []),
		"numChildren": item.get("meta", {}).get("numChildren", 0),
		"uri": "zotero://select/library/items/%s" % item.get("key"),
	}


def children(client, key, **params):
	"""Child items of `key`. Annotations are hidden unless itemType=annotation is asked for."""
	return client.get_json("/items/%s/children" % key, limit=100, **params) or []


def pdf_attachment(client, key):
	"""First PDF attachment of `key` (or `key` itself if it is one), else None."""
	own = client.get_json("/items/%s" % key)
	data = own.get("data", {})
	if data.get("itemType") == "attachment" and data.get("contentType") == "application/pdf":
		return own
	for child in children(client, key):
		cd = child.get("data", {})
		if cd.get("itemType") == "attachment" and cd.get("contentType") == "application/pdf" \
				and cd.get("linkMode") != "linked_url":
			return child
	return None


def find_items(client, doi=None, title=None, key=None, tag=None, collection=None, query=None):
	"""Search the library. DOI matches are filtered to exact equality client-side
	because Zotero's text search is a substring match."""
	if key:
		return [client.get_json("/items/%s" % key)]
	params = {"limit": 100}
	if doi:
		params.update(q=clean_doi(doi), qmode="everything")
	elif title or query:
		params.update(q=title or query, qmode="titleCreatorYear" if title else "everything")
	if tag:
		params["tag"] = tag
	path = "/items/top"  # top-level items only: skips attachments, child notes, annotations
	if collection:
		path = "/collections/%s/items/top" % resolve_collection(client, collection)
	items = client.get_json(path, **params) or []
	if doi:
		want = clean_doi(doi).lower()
		items = [i for i in items if (i.get("data", {}).get("DOI") or "").lower() == want]
	return items


def resolve_collection(client, name_or_key):
	"""Collection key from a name (case-insensitive) or a key."""
	cols = client.get_json("/collections", limit=100) or []
	for c in cols:
		d = c.get("data", {})
		if name_or_key in (d.get("key"), d.get("name")) or \
				(d.get("name") or "").lower() == name_or_key.lower():
			return d["key"]
	raise ZoteroError("No Zotero collection named %r. Existing: %s"
		% (name_or_key, ", ".join(c["data"]["name"] for c in cols) or "(none)"))


# --- Crossref -> Zotero item (used by `add`; a sibling script already owns Crossref)

CROSSREF_TYPES = {
	"journal-article": "journalArticle", "proceedings-article": "conferencePaper",
	"posted-content": "preprint", "book-chapter": "bookSection", "book": "book",
	"report": "report", "dissertation": "thesis", "dataset": "dataset",
}


def crossref_to_item(message, collection_key=None):
	"""Map a Crossref work record to a Zotero item. Only maps what Crossref gave."""
	itype = CROSSREF_TYPES.get(message.get("type"), "journalArticle")
	issued = (message.get("issued", {}).get("date-parts") or [[None]])[0]
	date = "-".join("%02d" % p if i else str(p) for i, p in enumerate(issued) if p)
	item = {
		"itemType": itype,
		"title": (message.get("title") or [""])[0],
		"creators": [
			{"creatorType": "author", "firstName": a.get("given", ""), "lastName": a.get("family", "")}
			if a.get("family") else {"creatorType": "author", "name": a.get("name", "")}
			for a in message.get("author", [])],
		"date": date,
		"DOI": message.get("DOI", ""),
		"url": message.get("URL", ""),
	}
	venue = (message.get("container-title") or [""])[0]
	if itype == "journalArticle":
		item.update(publicationTitle=venue, volume=message.get("volume", ""),
			issue=message.get("issue", ""), pages=message.get("page", ""),
			ISSN=(message.get("ISSN") or [""])[0])
	elif itype == "conferencePaper":
		item.update(proceedingsTitle=venue, pages=message.get("page", ""))
	elif itype == "bookSection":
		item.update(bookTitle=venue, pages=message.get("page", ""))
	abstract = re.sub(r"<[^>]+>", "", message.get("abstract", "") or "").strip()
	if abstract and itype in ("journalArticle", "conferencePaper", "preprint", "bookSection"):
		item["abstractNote"] = abstract
	if collection_key:
		item["collections"] = [collection_key]
	return {k: v for k, v in item.items() if v not in ("", None)}


def fetch_crossref(doi):
	"""Crossref record for a DOI via the sibling verify_doi.py (single source of truth)."""
	here = os.path.dirname(os.path.abspath(__file__))
	sys.path.insert(0, here)
	try:
		import verify_doi
	finally:
		sys.path.remove(here)
	try:
		return verify_doi.by_doi(doi)
	except urllib.error.HTTPError as exc:
		raise ZoteroError("Crossref has no usable record for DOI %s (HTTP %d). Check the DOI, "
			"or add the item in Zotero yourself and put its key in the record." % (doi, exc.code))
	except (urllib.error.URLError, OSError, ValueError) as exc:
		raise ZoteroError("Could not reach Crossref for DOI %s: %s" % (doi, exc))


def add_item(client, doi, collection=None):
	"""Create the item for `doi` unless it already exists. Returns (key, created)."""
	existing = find_items(client, doi=doi)
	if existing:
		return existing[0]["key"], False
	col = resolve_collection(client, collection) if collection else None
	message = fetch_crossref(doi)
	result = client.write("POST", "/items", [crossref_to_item(message, col)])
	failed = result.get("failed") or {}
	if failed:
		raise ZoteroError("Zotero rejected the new item: %s" % json.dumps(failed)[:300])
	return result["success"]["0"], True


# --- the Zotero note rendered from a spark-paper record

def esc(text):
	return html.escape(str(text or ""), quote=False)


def render_note(rec):
	"""HTML for the child note. Zotero's first line is the note title."""
	cc = rec.get("cross_check") or {}
	status = rec.get("status") or "summary"
	if status == "read" and not cc.get("done"):
		status = "summary"
	parts = ["<h1>spark-paper: %s</h1>" % esc(rec.get("short") or rec.get("citation"))]
	prov = "status: %s" % status
	if cc.get("done"):
		prov += "; draft-blind cross-check %s (%s disagreements)" % (
			esc(cc.get("date") or "run"), esc(cc.get("disagreements", "?")))
	else:
		prov += "; draft-blind cross-check not run"
	parts.append("<p><i>%s. Cross-checked against the source, not a verdict on the science.</i></p>" % prov)
	for heading, key in (("What it sets out to do", "sets_out"), ("Summary", "summary"),
			("Main takeaways", "takeaways")):
		if rec.get(key):
			parts.append("<h2>%s</h2><p>%s</p>" % (heading, esc(rec[key]).replace("\n", "<br/>")))
	if rec.get("findings"):
		parts.append("<h2>Key findings</h2><ul>")
		for f in rec["findings"][:40]:
			where = ("<i> (%s)</i>" % esc(f.get("where"))) if f.get("where") else ""
			parts.append("<li>%s%s <b>[%s]</b></li>" % (
				esc(f.get("finding")), where, esc(f.get("producer"))))
		parts.append("</ul>")
	gaps = [m for m in rec.get("methods", []) if m.get("label") == "unspecified"]
	if gaps:
		parts.append("<h2>Reproducibility gaps</h2><ul>%s</ul>" % "".join(
			"<li>%s: %s</li>" % (esc(m.get("item")), esc(m.get("detail"))) for m in gaps))
	qs = [d for d in rec.get("discussion", []) if d.get("kind") == "Question"]
	if qs:
		parts.append("<h2>Open questions</h2><ul>%s</ul>" % "".join(
			"<li>%s</li>" % esc(d.get("point")) for d in qs))
	return "\n".join(parts)


def child_note(client, key):
	"""The note this skill owns on `key` (tagged NOTE_TAG), or None."""
	for child in children(client, key):
		d = child.get("data", {})
		if d.get("itemType") == "note" and NOTE_TAG in [t.get("tag") for t in d.get("tags", [])]:
			return child
	return None


def upsert_note(client, key, html_body, status):
	"""Create or update the skill's child note. Returns ("created"|"updated"|"unchanged", key)."""
	tags = [{"tag": NOTE_TAG}, {"tag": STATUS_TAG_PREFIX + status}]
	existing = child_note(client, key)
	if existing is None:
		res = client.write("POST", "/items", [
			{"itemType": "note", "parentItem": key, "note": html_body, "tags": tags}])
		if res.get("failed"):
			raise ZoteroError("note rejected: %s" % json.dumps(res["failed"])[:300])
		return "created", res["success"]["0"]
	if existing["data"].get("note", "").strip() == html_body.strip():
		return "unchanged", existing["key"]
	client.write("PATCH", "/items/%s" % existing["key"],
		{"note": html_body, "tags": tags}, version=existing["version"])
	return "updated", existing["key"]


def set_status_tag(client, key, status):
	"""Add the skill's tags to the parent item, replacing only an older status tag."""
	item = client.get_json("/items/%s" % key)
	tags = [t for t in item["data"].get("tags", [])
		if not t.get("tag", "").startswith(STATUS_TAG_PREFIX)]
	names = {t.get("tag") for t in tags}
	for want in (NOTE_TAG, STATUS_TAG_PREFIX + status):
		if want not in names:
			tags.append({"tag": want})
	if tags != item["data"].get("tags", []):
		client.write("PATCH", "/items/%s" % key, {"tags": tags}, version=item["version"])
		return True
	return False


def link_workbook(client, key, workbook):
	"""Attach the workbook as a LINKED file (a pointer, not a copy). Idempotent."""
	path = os.path.abspath(workbook)
	for child in children(client, key):
		d = child.get("data", {})
		if d.get("itemType") == "attachment" and d.get("linkMode") == "linked_file" \
				and d.get("path") == path:
			return "unchanged"
	res = client.write("POST", "/items", [{
		"itemType": "attachment", "parentItem": key, "linkMode": "linked_file",
		"title": os.path.basename(path), "path": path,
		"contentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}])
	if res.get("failed"):
		raise ZoteroError("workbook link rejected: %s" % json.dumps(res["failed"])[:300])
	return "linked"


def local_path_from_url(file_url):
	return urllib.request.url2pathname(urllib.parse.urlparse(file_url).path)


# --------------------------------------------------------------------- commands

def cmd_status(client, args):
	up = client.ping()
	print("zotero reachable: %s (%s)" % ("yes" if up else "no", client.base))
	if not up:
		return 1
	sid = client.get_server_id()
	cfg = client.cfg
	print("server id: %s" % sid)
	if not cfg.get("key"):
		print("write access: not granted (run `auth`)")
	else:
		same = cfg.get("server_id") == sid
		kind = "persistent" if cfg.get("remember") else "SINGLE-USE (re-run auth, pick Always Allow)"
		print("write access: key stored, %s, server id %s" % (kind, "matches" if same else "DIFFERS"))
	return 0


def cmd_auth(client, args):
	if not client.ping():
		raise ZoteroError("Zotero is not reachable at %s." % client.base)
	print("A prompt is now showing in the Zotero window. Choose 'Always Allow'.", file=sys.stderr)
	sid = client.get_server_id()
	_, _, raw = client._request("POST", "/api/local/authorize", body={"appName": APP_NAME},
		headers={"Zotero-Server-ID": sid}, timeout=180)
	reply = json.loads(raw.decode("utf-8"))
	save_config({"key": reply["key"], "remember": bool(reply.get("remember")),
		"server_id": sid, "appName": APP_NAME})
	print("stored a %s key in %s" % ("persistent" if reply.get("remember") else "single-use",
		config_path()))
	if not reply.get("remember"):
		print("That key is single-use. Re-run `auth` and choose 'Always Allow'.", file=sys.stderr)
	return 0


def cmd_find(client, args):
	items = find_items(client, args.doi, args.title, args.key, args.tag, args.collection, args.query)
	out = []
	for item in items:
		row = summarize(item)
		if args.children and row["numChildren"]:
			kids = children(client, row["key"])
			row["pdf_key"] = next((k["key"] for k in kids
				if k["data"].get("contentType") == "application/pdf"), None)
			note = next((k["key"] for k in kids if k["data"].get("itemType") == "note"
				and NOTE_TAG in [t.get("tag") for t in k["data"].get("tags", [])]), None)
			row["spark_note_key"] = note
		out.append(row)
	print(json.dumps(out, indent=2))
	return 0 if out else 1


def cmd_pdf(client, args):
	att = pdf_attachment(client, args.key)
	if not att:
		raise ZoteroError("No local PDF attachment found under %s." % args.key)
	_, _, raw = client._request("GET", "/api/users/0/items/%s/file/view/url" % att["key"])
	path = local_path_from_url(raw.decode("utf-8").strip())
	if not os.path.exists(path):
		raise ZoteroError("Zotero reports %s but the file is missing on disk." % path)
	print(json.dumps({"pdf_key": att["key"], "path": path}))
	return 0


def cmd_annotations(client, args):
	"""The user's own highlights and comments, per PDF attachment."""
	out = []
	for att in children(client, args.key):
		if att["data"].get("itemType") != "attachment":
			continue
		for ann in children(client, att["key"], itemType="annotation"):
			d = ann["data"]
			if d.get("itemType") != "annotation":
				continue
			out.append({"pdf_key": att["key"], "type": d.get("annotationType"),
				"page": d.get("annotationPageLabel"), "text": d.get("annotationText"),
				"comment": d.get("annotationComment"), "colour": d.get("annotationColor"),
				"tags": [t.get("tag") for t in d.get("tags", [])]})
	print(json.dumps(out, indent=2))
	return 0


def cmd_add(client, args):
	key, created = add_item(client, args.doi, args.collection)
	print(json.dumps({"key": key, "created": created, "uri": "zotero://select/library/items/%s" % key}))
	return 0


def cmd_push(client, args):
	with open(args.record, encoding="utf-8") as fh:
		rec = json.load(fh)
	z = rec.setdefault("zotero", {})
	key = z.get("item_key")
	created = False
	if not key and rec.get("doi") and clean_doi(rec["doi"]).startswith("10."):
		key, created = add_item(client, rec["doi"], args.collection)
	if not key:
		raise ZoteroError("No Zotero item: the record has no zotero.item_key and no usable "
			"DOI to create one from.")
	z["item_key"] = key
	att = pdf_attachment(client, key)
	if att:
		z["pdf_key"] = att["key"]
	status = rec.get("status") or "summary"
	if status == "read" and not (rec.get("cross_check") or {}).get("done"):
		status = "summary"  # same gate as the workbook: no `read` without the cross-check
	note_result, note_key = upsert_note(client, key, render_note(rec), status)
	tag_changed = set_status_tag(client, key, status)
	link = link_workbook(client, key, args.workbook) if args.workbook else "skipped"
	if args.write_back:
		with open(args.record, "w", encoding="utf-8") as fh:
			json.dump(rec, fh, indent="\t", ensure_ascii=False)
	print(json.dumps({"item_key": key, "item_created": created, "pdf_key": z.get("pdf_key"),
		"note": note_result, "note_key": note_key, "tags_changed": tag_changed,
		"workbook_link": link, "status": status}))
	return 0


def cmd_uri(client, args):
	print("zotero://select/library/items/%s" % args.key)
	if args.pdf:
		uri = "zotero://open-pdf/library/items/%s" % args.pdf
		print(uri + ("?page=%d" % args.page if args.page else ""))
	return 0


def main(argv=None):
	ap = argparse.ArgumentParser(description="Local Zotero bridge for the spark-paper skill.")
	sub = ap.add_subparsers(dest="cmd", required=True)
	sub.add_parser("status").set_defaults(fn=cmd_status)
	sub.add_parser("auth").set_defaults(fn=cmd_auth)
	p = sub.add_parser("find")
	p.add_argument("--doi")
	p.add_argument("--title")
	p.add_argument("--key")
	p.add_argument("--tag")
	p.add_argument("--collection")
	p.add_argument("--query", help="free-text search over all fields")
	p.add_argument("--children", action="store_true", help="also report pdf_key and spark note key")
	p.set_defaults(fn=cmd_find)
	p = sub.add_parser("pdf")
	p.add_argument("key")
	p.set_defaults(fn=cmd_pdf)
	p = sub.add_parser("annotations")
	p.add_argument("key")
	p.set_defaults(fn=cmd_annotations)
	p = sub.add_parser("add")
	p.add_argument("--doi", required=True)
	p.add_argument("--collection")
	p.set_defaults(fn=cmd_add)
	p = sub.add_parser("push")
	p.add_argument("record")
	p.add_argument("--collection", help="collection for a newly created item")
	p.add_argument("--workbook", help="attach this workbook to the item as a linked file")
	p.add_argument("--write-back", action="store_true",
		help="write item_key and pdf_key back into the record JSON")
	p.set_defaults(fn=cmd_push)
	p = sub.add_parser("uri")
	p.add_argument("key")
	p.add_argument("--pdf")
	p.add_argument("--page", type=int)
	p.set_defaults(fn=cmd_uri)

	args = ap.parse_args(argv)
	try:
		return args.fn(Client(), args)
	except ZoteroError as exc:
		print("error: %s" % exc, file=sys.stderr)
		return 2


if __name__ == "__main__":
	sys.exit(main())
