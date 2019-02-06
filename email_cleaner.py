import mailbox
from sys import argv
import re
from langdetect import detect


print("entering mailbox")
# Enter the location of the mailbox you want to clean.
mbox = mailbox.mbox('YourMailbox.mbox')
print("exiting mailbox")



# Get the charset of the message.
def getcharsets(msg):
    charsets = set({})
    for c in msg.get_charsets():
        if c is not None:
            charsets.update([c])
    return charsets



# Get the body ofthe email; i.e: only the text.

def getBody(msg):
    t = None
    while msg.is_multipart():

        msg = msg.get_payload()[0]

    if (msg.get_content_type() == 'text/plain'):
        t = msg.get_payload(decode=True)
        t = t.decode("ascii", "ignore")

    return str(t)



# The following two functions removes URLs and links from the body.
# Also, they remove any salutations like: dear, Hello, Good Morning, Have a Good Day, etc...
# They also remove any quoted emails, which occurs when replying to an email or a thread.
# Both functions use RegEx (Regular Expressions) to match the unwanted text and remove it.

def remove_urls(vTEXT):
    vTEXT = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b',
                   '<URL>', vTEXT, flags=re.MULTILINE)
    return(vTEXT)


def cleanbody(body):
    cleaned = ""
    splittedbody = body.splitlines()
    for line in splittedbody:

        if line.startswith('-----Original Message-----'):
            break
        elif line.startswith('---------- Forwarded message ----------'):
            break
        elif re.match(r'^--\s*', line):
            break

        elif re.match(r'^Sent\s*from\s*', line):
            break
        elif not line.startswith('>'):
            try:
                if detect(line) == 'en':
                    cleaned += "\n" + line + " "
            except Exception as e:
                cleaned = cleaned

    cleaned = cleaned.replace('\n', '')
    cleaned = cleaned.replace('\"', '\'')
    cleaned = re.sub(r'\s*[Best]?\s*Regards(.*)',
                     '', cleaned, flags=re.MULTILINE)

    cleaned = re.sub(
        r'\s*On(.*)wrote[:]?(.*)', '', cleaned, flags=re.MULTILINE)

    cleaned = re.sub(
        r'\s*Sincerely\s*[yours]?(.*)', '', cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r'\s*From:(.*)Sent(.*)', '', cleaned, flags=re.MULTILINE)

    cleaned = re.sub(r'\s*Sent(.*)Subject:?(.*)',
                     '', cleaned, flags=re.MULTILINE)

    cleaned = re.sub(r'\s*From:(.*)To(.*)', '', cleaned, flags=re.MULTILINE)

    cleaned = re.sub(r'\s*<div(.*)', '', cleaned, flags=re.MULTILINE)

    cleaned = re.sub(r'\w+\d*@(.*)wrote:(.*)',
                     '', cleaned, flags=re.MULTILINE)

    cleaned = re.sub(r'\w+\d*\s*\w*\d*@(.*)sent:?(.*)',
                     '', cleaned, flags=re.MULTILINE)

    cleaned = re.sub(r'\s*Date:(.*)Subject(.*)', '',
                     cleaned, flags=re.MULTILINE)

    cleaned = re.sub(r'\s*In(.*)message(.*)dated(.*)',
                     '', cleaned, flags=re.MULTILINE)

    cleaned = re.sub(r'\s*Cheers(.*)', '', cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r'\s*Hi\s+\w{1,10}', '', cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r'\s*Hello\s+\w{1,10}', '', cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(
        r'\s*Good\s+Morning\s+', '', cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r'___________________(.*)', '',
                     cleaned, flags=re.IGNORECASE)

    cleaned = remove_urls(cleaned)

    cleaned = re.sub(
        r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '<URL>', cleaned)

    cleaned = re.sub(r'^https?:\/\/.*[\r\n]*',
                     '<URL>', cleaned, flags=re.MULTILINE)

    cleaned = re.sub(r'^hhttp?:\/\/.*[\r\n]*',
                     '<URL>', cleaned, flags=re.MULTILINE)

    cleaned = re.sub(r'hhttp?:\/\/.*[\r\n]*',
                     '<URL>', cleaned, flags=re.MULTILINE)

    cleaned = re.sub(r'\w{1,10}\.com?(.*)\.\w{1,4}',
                     '<URL>', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'\s+', ' ', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'<br>', ' ', cleaned, flags=re.MULTILINE)
    return cleaned


    
# Text file to store the received emails.
recieved_file = open("recieved.txt", "w")
# Text file to store the sent emails
repliedmssg_file = open("repliedmssg.txt", "w")
# Text file to store the received email with its reply
messageandreply_file = open("messageandreply_4.txt", "w")


messages = {}
recieved = []
replied = []
i = 1
j = 0


# iterate through the mailbox
for message in mbox:
    body = cleanbody(getBody(message))
    #check if there is content in the body
    if body.split():
        try:
           # check first if the email is spam or an ad.
            if message['List-Unsubscribe'] == None:  # if you cant unsubscribe
                    # if this is not in the email, meaning you cant reply
                if ("DO NOT REPLY TO THIS EMAIL" not in body):
                    # get email featurtes
                    # Enter the owner of the mailbox email address here to check if this particular email was received to him or he sent it.
                    if "Owner@MailboxOwner.com" not in message['from']:
                        recieved.append(message)
                    elif message['In-Reply-To'] != None:
                        replied.append(message)
                   
                    i += 1
        except Exception as e:
            print("empty body")
    j += 1
    


# Go throgh the cleaned emails and match each email with it's reply and put them both in a set.
dic_replies = {}
for rec_message in recieved[:]:
    n = cleanbody(getBody(rec_message))
    recieved_file.write(n)
    for sent_message in replied[:]:
        if (str)(rec_message['Message-Id']) in (str)(sent_message['In-Reply-To']):
            r = cleanbody(getBody(sent_message))
            dic_replies[n] = (r)
            replied.remove(sent_message)
            break


# Iterate the set of emails and print them as threads, each email with it;s corresponding reply
for keys, values in dic_replies.items():

    messageandreply_file.write(keys + "\n")
    messageandreply_file.write(values + "\n")

print("DONE!!!")