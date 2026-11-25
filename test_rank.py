from rank import rank, score

# fresher and faster-growing beats same-size stale
assert score(1000, 100, 0) > score(1000, 0, 0) > score(1000, 0, 90)

prev = {"a/up": {"stars": 100, "rank": 3}, "a/down": {"stars": 5000, "rank": 1}}
items = [
    {"category": "mcp", "repo": "a/up", "stars": 2100, "days_since_push": 0},
    {"category": "mcp", "repo": "a/down", "stars": 5000, "days_since_push": 200},
    {"category": "mcp", "repo": "a/new", "stars": 50, "days_since_push": 0},
]
cats = rank(items, prev)
by = {it["repo"]: it for it in cats["mcp"]}
assert by["a/up"]["gain"] == 2000 and by["a/up"]["rank"] == 1 and by["a/up"]["delta"] == 2
assert by["a/down"]["delta"] < 0
assert by["a/new"]["delta"] is None and by["a/new"]["gain"] is None
print("ok")
