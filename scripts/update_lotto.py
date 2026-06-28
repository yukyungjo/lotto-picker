import json
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

OUT = Path("data/lotto_numbers.json")

LATEST_URL = "https://smok95.github.io/lotto/results/latest.json"
ROUND_URL = "https://smok95.github.io/lotto/results/{}.json"

def get_json(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json,text/plain,*/*"
        }
    )
    with urllib.request.urlopen(req, timeout=12) as res:
        return json.loads(res.read().decode("utf-8"))

def normalize(item):
    return {
        "round": item["draw_no"],
        "date": item["date"][:10],
        "numbers": item["numbers"],
        "bonus": item["bonus_no"]
    }

def main():
    latest = normalize(get_json(LATEST_URL))
    latest_round = latest["round"]

    rounds = [latest]

    for n in range(latest_round - 1, max(0, latest_round - 60), -1):
        try:
            item = normalize(get_json(ROUND_URL.format(n)))
            rounds.append(item)
            print("saved", n)
        except Exception as e:
            print("skip", n, e)

    payload = {
        "updated_at": datetime.now(timezone(timedelta(hours=9))).isoformat(),
        "source": "smok95.github.io/lotto",
        "rounds": rounds
    }

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"Saved {len(rounds)} rounds. Latest: {latest_round}")

if __name__ == "__main__":
    main()
