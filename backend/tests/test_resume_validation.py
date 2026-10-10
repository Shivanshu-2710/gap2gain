from app.services.resume import rule_based_draft, validate_tailored


def test_invented_numbers_rejected():
    ok, w = validate_tailored("Built a tool in 2023.", "Built a tool in 2023 for 50 clients.")
    assert not ok and any("50" in x for x in w)


def test_same_facts_pass():
    ok, _ = validate_tailored("Led 3 projects in 2022.", "In 2022 I led 3 projects.")
    assert ok


def test_rule_based_only_reuses_lines():
    orig = "Tutored math\nWorked at cafe"
    out = rule_based_draft(orig, ["Math"])["tailored_text"]
    assert set(out.splitlines()) - {"RELEVANT TO THIS ROLE", ""} <= set(orig.splitlines())