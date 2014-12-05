letsemailstudents
=================

A simple tool which helps you email your CMU students easily.

Steps to use:

1. Create a new python message file using the message template in the 'messages' folder.
2. Edit the emailList list to contain tuples of relevant information for each recipient, with the first three elements of the tuple being andrewID, full name, and first name of the recipient, and the rest being anything you want. Ensure that the order of information is the same for all recipients.
3. Edit the subjectBase to contain your email subject title.
4. Edit the messageBase to contain your email message (plaintext), with string formatting symbols if you'd like.
5. Edit the msgVars to contain the indexes of the information from the recipient tuple which are necessary for string formatting messageBase. The indexes must be in order in which the information they appears in messageBase.
6. Run letsemailstudents.py and follow the instructions and you are done!

Note: Advanced uses includes using functions to create variable messages for different recipients based on their information.
