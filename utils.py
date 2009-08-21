import xmlrpclib

from django.conf import settings

def get_email_accounts():
    server = xmlrpclib.Server('https://api.webfaction.com/')
    session_id, account = server.login(settings.WEBFACTION_USERNAME, settings.WEBFACTION_PASSWORD)
    emails = server.list_emails(session_id)
    mailboxes = server.list_mailboxes(session_id)
    email_accounts = []
    for domain in settings.WEBFACTION_DOMAINS.keys():
        email_accounts += [x for x in emails if x['email_address'].endswith(domain)]
    valid_email_accounts = []
    for email in email_accounts:
        targets = email['targets'].split(',')
        domain = email['email_address'].split('@')[1]
        prefix = settings.WEBFACTION_DOMAINS[domain]
        if len(targets)>2:
            raise Exception, "This app currently only supports one redirect and one mailbox. Please correct via control panel."
        for target in targets:
            valid = False
            if '@' in target:
                email['redirect']=target
                valid = True
            else:
                for mailbox in mailboxes:
                    if target==mailbox['mailbox'] and target.startswith(prefix):
                        email['mailbox'] = mailbox
                        valid = True
        if valid:
            valid_email_accounts.append(email)
    return valid_email_accounts

def generate_mailbox_name(email_address):
    email_name, domain = email_address.split('@')
    return settings.WEBFACTION_DOMAINS[domain]+email_name.replace('.','_')
    
def generate_targets(mailbox, redirect):
    targets = []
    if mailbox:
        targets.append(mailbox)
    if redirect:
        targets.append(redirect)
    return ','.join(targets)