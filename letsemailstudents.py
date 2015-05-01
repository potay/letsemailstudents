import getpass, string
import smtplib
import sys, time, os
import contextlib
import urllib
from settings import *

def readWebPage(url):
    assert(url.startswith("http://"))
    with contextlib.closing(urllib.urlopen(url)) as fin:
        return fin.read()

def getPersonData(andrewid):
    import json
    data = json.loads(readWebPage(PERSON_DATA_API+andrewid))
    if data:
        return data
    else:
        import random
        firstname = random.choice(['John', 'Jack', 'Harry', 'Jane', 'Jasline', 'Hermione'])
        lastname = random.choice(['Doe', 'Jadock', 'Dood', 'Purdle', 'Johnson', 'Granger'])
        return {'first_name': firstname,
                'name': firstname+" "+lastname}

def getMsgFileImportPath(msgFolder):
    filenameList = []
    filenamesStr = ""
    i = 1
    for filepath in os.listdir(msgFolder):
        filename, fileExt = os.path.splitext(filepath)
        if ((filename != "__init__") and
            (fileExt == ".py")):
            filenamesStr += "%d. %s\n" % (i, filename)
            filenameList += [filename]
            i += 1

    print "Message Files"
    print "###################################"
    print
    print filenamesStr
    msgFileIndex = raw_input("Enter the number of the message file you want to use: ")
    print

    try:
        chosenFilename = filenameList[int(msgFileIndex)-1]
        return string.replace(msgFolder, "/", ".")+"."+chosenFilename
    except:
        print "Sorry, no such file found. Please try again"
        return getMsgFileImportPath(msgFolder)

def printEmailPreview(testList, CAFullName, CAName,
                     coCAName, coCAEmail, fromaddr, passwd,
                     msgBase, msgVars, subjectBase):
    andrewid = testList[0][0]
    if USE_PERSON_API:
        personData = getPersonData(andrewid)
        firstname = personData['first_name']
        fullname = personData['name']
    else:
        firstname = testList[0][2]
        fullname = testList[0][1]
    toaddr = "%s@%s" % (andrewid, EMAIL_DOMAIN)
    toaddrList = [toaddr, toaddr]
    subject  = '[%s] %s' % (andrewid, subjectBase)
    msgStudentBase = msgSub(msgBase, testList[0], msgVars)
    if (coCAEmail == None):
        coCAEmail = ""
    else:
        toaddrList += [coCAEmail]
        coCAEmail = (", %s <%s>" % (coCAName, coCAEmail))
    msg = ("""From: %s <%s>
To: %s <%s>
CC: %s <%s>""" + coCAEmail + """
Subject: %s

""" + GREETING + """

%s

""" + SIGNATURE) % (CAFullName, fromaddr, fullname, toaddr, CAFullName,
                    fromaddr, subject, firstname, msgStudentBase, CAName)

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
                    coCAName, coCAEmail, fromaddr, passwd,
                    msgBase, msgVars, subjectBase):
    for studentDetails in studentList:
        andrewid = studentDetails[0]
        if USE_PERSON_API:
            personData = getPersonData(andrewid)
            firstname = personData['first_name']
            fullname = personData['name']
        else:
            firstname = studentDetails[2]
            fullname = studentDetails[1]
        toaddr = "%s@%s" % (andrewid, EMAIL_DOMAIN)
        toaddrList = [toaddr, toaddr]
        subject  = '[%s] %s' % (andrewid, subjectBase)
        msgStudentBase = msgSub(msgBase, studentDetails, msgVars)
        if (coCAEmail == None):
            coCAEmail = ""
        else:
            toaddrList += [coCAEmail]
            coCAEmail = (", %s <%s>" % (coCAName, coCAEmail))
        msg = ("""From: %s <%s>
To: %s <%s>
CC: %s <%s>""" + coCAEmail + """
Subject: %s

""" + GREETING + """

%s

""" + SIGNATURE) % (CAFullName, fromaddr, fullname, toaddr, CAFullName,
                    fromaddr, subject, firstname, msgStudentBase, CAName)

        # The actual mail send
        try:
            server.sendmail(fromaddr, toaddrList, msg)
            print "%s: Sent!" % andrewid
        except smtplib.Exception:
            print "%s: Sending failed ):"
    print

def msgSub(msgBase, details, indexList):
    detailSubs = tuple([details[i] for i in indexList])
    return msgBase % detailSubs

def loginGmail(andrewID=None):
    print "Gmail Login"
    print "###################################"

    if not andrewID:
        CAAndrewID = raw_input("What's your andrew id?: ")
        print
    else:
        CAAndrewID = andrewID

    if REQUIRE_GMAIL_LOGIN_DOMAIN:
        username = "%s@%s" % (CAAndrewID, EMAIL_DOMAIN)
    else:
        username = CAAndrewID

    print "Email User: %s" % username
    print

    password = getpass.getpass("CMU Google Apps Password? (Not Andrew Password): ")

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()

    try:
        server.login(username,password)
        print
        print "** Login success! **"
        print
        return (server, CAAndrewID, username, password)
    except smtplib.SMTPAuthenticationError:
        print
        answer = raw_input("Oops! Login failed ): Try again? (Y/N): ")
        print
        if (answer == "Y"):
            server.quit()
            return loginGmail(andrewID)
        else:
            return (None, None, None, None)

def getCoCAEmailFromPicturesPage(name):
    staffPicturesURL = readWebPage(COURSE_WEBSITE_URL+"/"+SYLLABUS_PAGE).\
                        split("staff pictures")[0].\
                        split("href=\"")[-1].\
                        split("\">")[0]
    pageSource = readWebPage(COURSE_WEBSITE_URL+"/"+staffPicturesURL)
    return getCoCAEmailFromPageSource(name, pageSource)

def getCoCAEmailFromSyllabus(name):
    pageSource = readWebPage(COURSE_WEBSITE_URL+"/"+SYLLABUS_PAGE).\
                        replace("\n", "").\
                        split("Schedule<br>of Classes:")[1].\
                        split("</table>")[0]
    return getCoCAEmailFromPageSource(name, pageSource)

def getCoCAEmailFromPageSource(name, pageSource):
    nameCount = pageSource.count(name)

    if nameCount < 1:
        return []
    elif nameCount == 1:
        CAAndrewID = pageSource[pageSource.find(name)+len(name):].\
                        split("(")[1].\
                        split(")")[0]
        name = pageSource[pageSource.find(name):].\
                        split(" ")[0]
        CAEmail = ("%s@%s" % (CAAndrewID, EMAIL_DOMAIN))
        return [(name, CAEmail)]
    else:
        CAList = []
        for i in xrange(nameCount):
            namePos = pageSource[pageSource.find(name):]
            pageSource = namePos[len(name):]
            nameSplit = namePos.split("(")
            CAName = nameSplit[0][:-1]
            andrewID = nameSplit[1].split(")")[0]
            CAEmail = ("%s@%s" % (andrewID, EMAIL_DOMAIN))
            CAList += [(CAName, CAEmail)]
        return CAList

def getCoCAEmail(name):
    name = name.capitalize()

    try:
        return getCoCAEmailFromSyllabus(name)
    except:
        pass

    try:
        return getCoCAEmailFromPicturesPage(name)
    except:
        pass

    return []

def main():
    msgSent = False
    msgFileImportPath = getMsgFileImportPath(MESSAGE_FOLDER)

    try:
        print "Loading message file '%s'..." % msgFileImportPath,
        _temp = __import__(msgFileImportPath, globals(), locals(),
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

    if PROMPT_FOR_DEFAULT_USER:
        useDefaultUser = raw_input("Use default user details? (Y/N): ") == "Y"
    else:
        useDefaultUser = False
    print

    if not useDefaultUser:
        CAFullName = raw_input("What is your full name?: ")
        CAName = raw_input("What is your preferred name?: ")
        print

        (server, CAAndrewID, fromaddr, passwd) = loginGmail()
    else:
        CAFullName = USER_FULL_NAME
        CAName = USER_PREFERRED_NAME
        print "Full Name: %s\nPreferred Name: %s" % (CAFullName, CAName)
        print

        (server, CAAndrewID, fromaddr, passwd) = loginGmail(USER_ANDREW_ID)

    if (server == None):
        print "Unable to login to Gmail. Message not sent."
        return False

    if USE_PERSON_API:
        # List of test contacts (andrew ID, ...)
        testList = [tuple([CAAndrewID] + \
                          list(emailList[0][1:]))]
        if (len(emailList) > 1):
            testList += [tuple([CAAndrewID] + \
                               list(emailList[1][1:]))]
        else:
            testList += [tuple([CAAndrewID] + \
                               list(emailList[0][1:]))]
    else:
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
    sendToCoCA = raw_input("What's your co-CA's first name? Enter 'N' if you do not wish to CC your co-CA: ")
    if sendToCoCA == "N":
        coCAName = None
        coCAEmail = None
        print "Not sending to your Co-CA."
        print
    else:
        coCAName = sendToCoCA
        while True:
            coCAEmailList = getCoCAEmail(coCAName)
            numOfCAs = len(coCAEmailList)
            if numOfCAs > 0:
                if numOfCAs > 1:
                    nameListStr = ""
                    for i in xrange(numOfCAs):
                        nameListStr += "%d. %s\n" % (i+1,
                                                     coCAEmailList[i][0])
                    while True:
                        print "Multiple CAs with that name were found."
                        print
                        print nameListStr
                        number = raw_input("Enter the number of the CA you are referring to: ")
                        try:
                            coCAName, coCAEmail = coCAEmailList[int(number)-1]
                            break
                        except:
                            print "Sorry, we don't understand that number. Please try again."
                else:
                    coCAName, coCAEmail = coCAEmailList[0]

                print "CC-ing email to %s (%s)" % (coCAName, coCAEmail)
                print
                break
            else:
                coCAName = raw_input("CA not found. Please enter your co-CA's first name again, or enter 'N' to not CC your co-CA: ")
                if coCAName == 'N':
                    coCAName = None
                    coCAEmail = None
                    print "Not sending to your Co-CA."
                    print
                    break

    sys.stdout.write("Cooking up your email for you")
    sys.stdout.flush()
    #time.sleep(1)
    sys.stdout.write(".")
    sys.stdout.flush()
    #time.sleep(1)
    sys.stdout.write(".")
    sys.stdout.flush()
    #time.sleep(1)
    sys.stdout.write(".\n")
    sys.stdout.flush()
    #time.sleep(1)

    printEmailPreview(testList, CAFullName, CAName, coCAName, coCAEmail,
                      fromaddr, passwd, msgBase, msgVars, subjectBase)

    continueSendingTest = raw_input("Is the sample email alright? Shall we test it by sending it to the test list? (Y/N): ")
    print

    if (continueSendingTest == "Y"):
        sendEmailToList(server, testList, CAFullName, CAName,
                        coCAName, coCAEmail,
                        fromaddr, passwd, msgBase, msgVars, subjectBase)

        continueSending = raw_input("Is the email alright? Shall we send it to \
the actual list? (Y/N): ")
        print

        if (continueSending == "Y"):
            sendEmailToList(server, emailList, CAFullName, CAName,
                            coCAName, coCAEmail,
                            fromaddr, passwd, msgBase, msgVars, subjectBase)
            msgSent = True

    server.quit()

    if (msgSent == False):
        print "Message not sent!"
    else:
        print "Email is a success! Good-bye!"
    print

if __name__ == "__main__":
    main()

