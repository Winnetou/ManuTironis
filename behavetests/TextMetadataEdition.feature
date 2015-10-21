Scenario: user can correct pagination

Scenario: user can correct side pagination
Given page contains side pagination
When user click on side pagination
Then suggestion to correct appears
And user can click on suggestion
And window appears

Scenario: user can set delimitation of greek and latin text
Given delimitation of greek and latin text is set
When user click on
Then suggestion to correct appears

Scenario: user can set delimitation of apparatus criticus
Given delimitation of apparatus criticus is set
When user click on
Then suggestion to correct appears
And


Scneario: user can mark a part of text as pagination
When
Then in the right pane option appears to treat this as pagination