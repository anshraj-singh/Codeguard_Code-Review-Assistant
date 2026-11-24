from app.analyzer import analyze_code


def test_detect_eval():
    code = "result = eval(user_input)"

    result = analyze_code(code)

    assert result["summary"]["high"] == 1
    assert result["findings"][0]["rule"] == "unsafe_eval"


def test_detect_exec():
    code = "exec(user_code)"

    result = analyze_code(code)

    assert result["summary"]["high"] == 1


def test_detect_bare_except():
    code = "try:\n    pass\nexcept:\n    pass"

    result = analyze_code(code)

    assert result["summary"]["medium"] == 1


def test_detect_print():
    code = "print('debug')"

    result = analyze_code(code)

    assert result["summary"]["low"] == 1


def test_clean_code():
    code = "name = 'Ansh'\nresult = name.upper()"

    result = analyze_code(code)

    assert result["summary"]["total_issues"] == 0
    assert result["findings"] == []


def test_multiple_issues():
    code = "eval(user_input)\nprint('debug')"

    result = analyze_code(code)

    assert result["summary"]["total_issues"] == 2
    assert result["summary"]["high"] == 1
    assert result["summary"]["low"] == 1