from ats import calculate_ats_score

candidate = [
    "Python",
    "SQL",
    "Machine Learning",
    "Power BI"
]

required = [
    "Python",
    "SQL",
    "Machine Learning",
    "Docker",
    "AWS"
]

score, matched, missing = calculate_ats_score(
    candidate,
    required
)

print(score)
print(matched)
print(missing)