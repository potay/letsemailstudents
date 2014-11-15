import getpass
import smtplib
import sys, time

def printEmailPreview(testList, CAFullName, CAName,
                     coCAEmail, fromaddr, passwd,
                     msgBase, msgVars, subjectBase):
    andrewid = testList[0][0]
    firstname = testList[0][2]
    fullname = testList[0][1]
    toaddr = "%s@andrew.cmu.edu" % andrewid
    toaddrList = [toaddr, toaddr]
    subject  = '[%s] %s' % (andrewid, subjectBase)
    msgStudentBase = msgSub(msgBase, testList[0], msgVars)
    if (coCAEmail == None):
        coCAEmail = ""
    else:
        toaddrList += [coCAEmail]
        coCAEmail = (", %s" % coCAEmail)
    msg = ("""From: %s <%s>
To: %s <%s>
CC: %s <%s>""" + coCAEmail + """
Subject: %s

Hey %s!

%s

Best,
%s""") % (CAFullName, fromaddr, fullname, toaddr, CAFullName, fromaddr,
          subject, firstname, msgStudentBase, CAName)

    # Print sample email
    print
    print "EMAIL PREVIEW"
    print "##################################################################"
    print
    print msg
    print
    print "##################################################################"
    print

def sendEmailToList(server, studentList, CAFullName, CAName,
                    coCAEmail, fromaddr, passwd,
                    msgBase, msgVars, subjectBase):
    for studentDetails in studentList:
        andrewid = studentDetails[0]
        firstname = studentDetails[2]
        fullname = studentDetails[1]
        toaddr = "%s@andrew.cmu.edu" % andrewid
        toaddrList = [toaddr, toaddr]
        subject  = '[%s] %s' % (andrewid, subjectBase)
        msgStudentBase = msgSub(msgBase, studentDetails, msgVars)
        if (coCAEmail == None):
            coCAEmail = ""
        else:
            toaddrList += [coCAEmail]
            coCAEmail = (", %s" % coCAEmail)
        msg = ("""From: %s <%s>
To: %s <%s>
CC: %s <%s>""" + coCAEmail + """
Subject: %s

Hey %s!

%s

Best,
%s""") % (CAFullName, fromaddr, fullname, toaddr, CAFullName, fromaddr,
          subject, firstname, msgStudentBase, CAName)

        # The actual mail send
        try:
            server.sendmail(fromaddr, toaddrList, msg)
            print "%s: Sent!" % andrewid
        except smtplib.Exception:
            print "%s: Sending failed ):"

def msgSub(msgBase, details, indexList):
    detailSubs = tuple([details[i] for i in indexList])
    return msgBase % detailSubs

def loginGmail():
    print "Gmail Login"
    print "###################################"
    CAAndrewID = raw_input("What's your andrew id?: ")
    fromaddr = "%s@andrew.cmu.edu" % CAAndrewID
    passwd = getpass.getpass("CMU Google Apps Password? (Not Andrew Password): ")

    username = fromaddr
    password = passwd

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()

    try:
        server.login(username,password)
        print "** Login success! **"
        print
        return (server, CAAndrewID, username, password)
    except smtplib.SMTPAuthenticationError:
        answer = raw_input("Oops! Login failed ): Try again? (Y/N): ")
        if (answer == "Y"):
            server.quit()
            loginGmail()
        else:
            return (None, None, None, None)

def main():
    msgSent = False
    msgfilename = raw_input("What is the filename of your message file (w/o extension .py)?: ")

    try:
        print
        print "Loading message file...",
        _temp = __import__("messages.%s" % msgfilename, globals(), locals(),
                       ['emaiList', 'msgBase', 'msgVars', 'subjectBase'],
                       -1)
        emailList = _temp.emailList
        msgBase = _temp.msgBase
        msgVars = _temp.msgVars
        subjectBase = _temp.subjectBase

        print "Loaded!"
        print

    except:
        print "\nMessage file could not be loaded. Either no such message file was found or there is an error with your file."
        print sys.exc_info()[0]

        return False

    print "Your Details"
    print "###################################"
    CAFullName = raw_input("What is your full name?: ")
    CAName = raw_input("What is your preferred name?: ")
    print

    (server, CAAndrewID, fromaddr, passwd) = loginGmail()

    if (server == None):
        print "Unable to login to Gmail. Message not sent."
        return False

    # List of test contacts (andrew ID, fullname, firstname, ...)
    testList = [tuple([CAAndrewID, CAFullName, CAName] + \
                      list(emailList[0][3:]))]
    if (len(emailList) > 1):
        testList += [tuple([CAAndrewID, CAFullName+"2", CAName+"2"] + \
                           list(emailList[1][3:]))]
    else:
        testList += [tuple([CAAndrewID, CAFullName, CAName] + \
                           list(emailList[0][3:]))]

    print "Co-CA Details"
    print "###################################"
    sendToCoCA = raw_input("What's your co-CA's andrew id? Enter 'N' if you do not wish to CC your co-CA: ")
    if sendToCoCA == "N":
        coCAEmail = None
        print "Not sending to your Co-CA."
        print
    else:
        coCAName = raw_input("What's your co-CA's name?: ")
        coCAEmail = ("%s@andrew.cmu.edu"%sendToCoCA)
        print "CC-ing email to %s (%s)" % (coCAName, coCAEmail)
        print

    sys.stdout.write("Cooking up your email for you")
    sys.stdout.flush()
    time.sleep(1)
    sys.stdout.write(".")
    sys.stdout.flush()
    time.sleep(1)
    sys.stdout.write(".")
    sys.stdout.flush()
    time.sleep(1)
    sys.stdout.write(".\n")
    sys.stdout.flush()

    printEmailPreview(testList, CAFullName, CAName, coCAEmail,
                      fromaddr, passwd, msgBase, msgVars, subjectBase)

    continueSendingTest = raw_input("Is the sample email alright? Shall we test it by sending it to the test list? (Y/N): ")
    print

    if (continueSendingTest == "Y"):
        sendEmailToList(server, testList, CAFullName, CAName, coCAEmail,
                    fromaddr, passwd, msgBase, msgVars, subjectBase)

        continueSending = raw_input("Is the email alright? Shall we send it to \
the actual list? (Y/N): ")
        print

        if (continueSending == "Y"):
            sendEmailToList(server, emailList, CAFullName, CAName, coCAEmail,
                             fromaddr, passwd, msgBase, msgVars, subjectBase)
            msgSent = True

    server.quit()

    if (msgSent == False):
        print "Message not sent!"

if __name__ == "__main__":
    main()

