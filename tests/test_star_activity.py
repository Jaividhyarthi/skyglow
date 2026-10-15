from backend.engine import summarize_star_sample

def test_star_sample_daily_counts():
    records = [
        {'starred_at': '2026-10-10T10:00:00Z'},
        {'starred_at': '2026-10-10T11:00:00Z'},
        {'starred_at': '2026-10-11T11:00:00Z'}
    ]
    result = summarize_star_sample(records, 1000)
    assert result['sample_size'] == 3
    assert result['peak_sample_day']['stars'] == 2
    assert result['full_history'] is False

def test_empty_sample():
    result = summarize_star_sample([], 0)
    assert result['sample_size'] == 0
    assert result['coverage_percent'] == 0
