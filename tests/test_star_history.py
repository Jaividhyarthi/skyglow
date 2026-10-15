from backend.engine import summarize_star_history


def test_valid_history():
    rows = [
        {'week': 1791072000, 'total': 7, 'days': [1, 1, 1, 1, 1, 1, 1]},
        {'week': 1790467200, 'total': 14, 'days': [2, 2, 2, 2, 2, 2, 2]}
    ]
    result = summarize_star_history(rows)
    assert result['status'] == 'available'
    assert len(result['weekly']) == 2
    assert len(result['daily']) == 14
    assert result['weekly'][0]['stars'] == 14


def test_invalid_history():
    result = summarize_star_history([
        {'week': 1791072000, 'total': 100, 'days': [1, 2]}
    ])
    assert result['status'] == 'unavailable'


def test_empty_history():
    assert summarize_star_history(None)['status'] == 'unavailable'
