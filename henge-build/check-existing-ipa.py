#!/usr/bin/env python3
"""Keep retries available for failed compilations and preserve published IPAs."""
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def check(payload, name):
    if any(item["name"] == name and not item["expired"] for item in payload["artifacts"]):
        raise SystemExit("An IPA already exists for this source commit. Existing artifact preserved.")


if __name__ == "__main__":
    name = "Henge-IPA-" + os.environ["GITHUB_SHA"]
    api = os.environ["GITHUB_API_URL"]
    repo = os.environ["GITHUB_REPOSITORY"]
    query = urlencode({"name": name, "per_page": "100"})
    request = Request(f"{api}/repos/{repo}/actions/artifacts?{query}", headers={
        "Authorization": "Bearer " + os.environ["HENGE_ACTIONS_TOKEN"],
        "Accept": "application/vnd.github+json",
    })
    with urlopen(request, timeout=20) as response:
        check(json.load(response), name)
