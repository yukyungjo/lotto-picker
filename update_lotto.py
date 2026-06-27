import json
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

API = "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo="
OUT = Path("data/lotto_numbers.json")

def fetch_round(round_no):
    with urllib.request.urlopen(API + str(round_no), timeout=15) as res:
        data = json.loads(res.read().decode("utf-8"))
    if data.get("returnValue") != "success":
        return None
    return {
        "round": data["drwNo"],
        "date": data["drwNoDate"],
        "numbers": [data["drwtNo1"], data["drwtNo2"], data["drwtNo3"], data["drwtNo4"], data["drwtNo5"], data["drwtNo6"]],
        "bonus": data["bnusNo"]
    }

def latest_guess():
    first = datetime(2002, 12, 7, tzinfo=timezone(timedelta(hours=9)))
    now = datetime.now(timezone(timedelta(hours=9)))
    return ((now - first).days // 7) + 1

def main():
    latest = None
    guess = latest_guess()
    for n in range(guess + 3, max(1, guess - 20), -1):
        try:
            latest = fetch_round(n)
            if latest:
                break
        except Exception:
            pass
    if not latest:
        raise RuntimeError("최신 로또 회차를 찾지 못했습니다.")

    rounds = []
    for n in range(latest["round"], max(0, latest["round"] - 60), -1):
        try:
            item = fetch_round(n)
            if item:
                rounds.append(item)
        except Exception:
            continue

    payload = {
        "updated_at": datetime.now(timezone(timedelta(hours=9))).isoformat(),
        "source": "dhlottery",
        "rounds": rounds
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(rounds)} rounds. Latest: {rounds[0]['round']}")

if __name__ == "__main__":
    main()
