Feature: Editing Text 
User has UI to edit the text

Scenario: user can see correct words
Given user is on the page containing incrorrect words
When user click on incorrect word
Then button "this is correct" appears



Scenario: user tries to correct an incorrect word
Given user is on the page containing incrorrect words
When user click on an incorrect word 
Then right pane is populated with correction suggestions
And option "none of the above"
And option ""
And disabled "Save" button

Scenario: user selects a suggestion for correcting a word
Given That right pane contains suggestions
When User clicks on the suggestion
Then Save button is enabled
And user can click on Save button
And word is corrected
And it appears as correct
And right pane is emptied 

Scenario: user cannot find correct version of a word
Given user is on the page containing incrorrect words
and uder clicked an incorrect word
option "none of the above"
When User clicks on the option
Then input field appears with greek aplhabet below
And user can type a word clicking on greek alphabet letters
And when lenght of the input >2 Save button is enabled
And user clicks on save button 
# and in  
And right pane is emptied 


Scenario: user tries to correct a correct word
Given user is on the page containing incrorrect words
When user click on a correct word
Then option in the right pane appears "this is incorrect"
And user can click on that option
And word is changed from correct to incorrect  


Scenario: user corrected frequent incorrect word
Given user 
When
Then 

Scenario: user mark word as continued in the next line


Scenario: user can divide a word
Given user is on the page containing incrorrect words
