#!/usr/bin/env python3
"""Install or remove CoachProxy dark mode through the Node-RED admin API.

Only the global "Custom CSS" template node is changed (it is the one CoachProxyOS loads on every
dashboard tab); everything else in your flow is left alone and nothing else is restarted.

  deploy.py --url http://HOST:1880              dry run: show what would change
  deploy.py --url http://HOST:1880 --apply      back up the flows to backups/, then install
  deploy.py --url http://HOST:1880 --rollback   remove the dark-mode block again

If Node-RED's admin API requires a login, pass --token <access token>.
"""
import argparse, datetime, difflib, json, sys, urllib.request

from build import ROOT, install, strip

DEFAULT_NODE_ID = "165202ff.dbfd0d"  # "Custom CSS" in the stock CoachProxyOS flow


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", required=True, help="Node-RED admin URL, e.g. http://coachproxy.local:1880")
    ap.add_argument("--token", help="Node-RED admin access token, if adminAuth is enabled")
    ap.add_argument("--node-id", help=f"template node to patch (default: {DEFAULT_NODE_ID}, else the only global 'Custom CSS' template)")
    ap.add_argument("--apply", action="store_true", help="install the dark-mode block")
    ap.add_argument("--rollback", action="store_true", help="remove the dark-mode block")
    a = ap.parse_args()
    base = a.url.rstrip("/")
    headers = {"Node-RED-API-Version": "v2", "Content-Type": "application/json"}
    if a.token:
        headers["Authorization"] = "Bearer " + a.token

    def call(data=None, extra=None):
        req = urllib.request.Request(base + "/flows", headers={**headers, **(extra or {})},
                                     data=json.dumps(data).encode() if data is not None else None)
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)

    cur = call()
    nodes = cur["flows"]
    wanted = a.node_id or DEFAULT_NODE_ID
    node = next((n for n in nodes if n["id"] == wanted), None)
    if node is None and not a.node_id:
        guess = [n for n in nodes if n.get("type") == "ui_template" and n.get("templateScope") == "global"
                 and n.get("name") == "Custom CSS"]
        node = guess[0] if len(guess) == 1 else None
    if node is None:
        sys.exit("Could not find the global 'Custom CSS' template node. Pass --node-id <id> "
                 "(any global ui_template works; it is loaded on every tab).")

    target = strip(node["format"]) if a.rollback else install(node["format"])
    if node["format"] == target:
        print("Already up to date; nothing to do.")
        return
    sys.stdout.writelines(difflib.unified_diff(node["format"].splitlines(True), target.splitlines(True),
                                               "live", "new", n=1))
    if not (a.apply or a.rollback):
        print("\nDry run only. Re-run with --apply.")
        return

    backups = ROOT / "backups"
    backups.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    (backups / f"flows-{stamp}.json").write_text(json.dumps(nodes))
    print(f"\nBackup: backups/flows-{stamp}.json")

    node["format"] = target
    # 'nodes' deploys only the modified node, so the rest of the flow keeps running untouched.
    res = call({"rev": cur["rev"], "flows": nodes}, {"Node-RED-Deployment-Type": "nodes"})
    print("Deployed, new rev:", res.get("rev"))


if __name__ == "__main__":
    main()
