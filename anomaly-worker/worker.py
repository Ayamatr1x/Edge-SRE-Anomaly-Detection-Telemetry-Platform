import time, requests, pandas as pd
from sklearn.ensemble import IsolationForest

VM_URL = "http://victoriametrics:8428"
QUERY = 'avg_over_time(host_cpu_seconds_total[5m])'
PUSH_URL = f"{VM_URL}/api/v1/import/prometheus"

def fetch_recent():
    resp = requests.get(f"{VM_URL}/api/v1/query_range", params={
        "query": QUERY,
        "start": int(time.time()) - 3600,
        "end": int(time.time()),
        "step": "60s"
    })
    result = resp.json()["data"]["result"]
    if not result:
        return None
    values = [float(v[1]) for v in result[0]["values"]]
    return pd.DataFrame(values, columns=["value"])

def detect_and_push():
    df = fetch_recent()
    if df is None or len(df) < 10:
        return
    model = IsolationForest(contamination=0.05)
    df["anomaly"] = model.fit_predict(df[["value"]])
    latest_anomaly = 1 if df["anomaly"].iloc[-1] == -1 else 0
    ts = int(time.time() * 1000)
    metric_line = f'anomaly_score {latest_anomaly} {ts}\n'
    requests.post(PUSH_URL, data=metric_line)
    print(f"pushed anomaly_score={latest_anomaly}")

if __name__ == "__main__":
    while True:
        try:
            detect_and_push()
        except Exception as e:
            print("error:", e)
        time.sleep(300)  # run every 5 minutes
