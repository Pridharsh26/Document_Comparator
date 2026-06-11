ANALYZER_PROMPT = """
You are a compliance document comparison expert.

Analyze the old rule and new rule.

Determine:

1. ADDED
2. REMOVED
3. MODIFIED
4. NO_CHANGE

Return ONLY valid JSON.

Format:

{
  "change_type":"",
  "rule_name":"",
  "summary":"",
  "old_text":"",
  "new_text":""
}

OLD RULE:
{old_text}

NEW RULE:
{new_text}
"""