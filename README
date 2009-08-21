django-webfaction is intended to provide a simple control panel for creating and modifying email addresses and mailboxes for sites that use Webfaction shared hosting. It seamlessly integrates into the Django admin and emails are listed and edited as if they were Django models (although no model is stored apart from the logging of changes).

It was developed the match my specific requirements and therefore currently imposes the following constraints:

  * The distinction between email addresses and mailboxes is partly hidden from users to keep things simple. They create an email address with either a redirect address, a mailbox or both
  * Therefore users can have only one mailbox and/or one redirect address per email address
  * No support for deleting email accounts or mailboxes
  * No support for adding a mailbox except when an email address is first created (redirects can be added afterwards)
  * Certain naming conventions are imposed to allow automatically naming mailboxes. Specifically each domain that users are allowed to create addresses for has a prefix defined. The mailbox is created from the prefix and (kind of) 'slugified' version of the email address

Requirements
============

`django-webfaction` requires Django 1.1 or later.  However the requirement for 1.1 is only to support a convenient way integrate a non-model based entity into the standard Django admin without creating a dummy SQL table. If you change the line that says 'managed=False' in models.py to 'pass' then everything should work in Django 1.0

Installation
============

1.  Download from the repository and place in your Python path then add 'django-webfaction' to your list of `INSTALLED_APPS` in 'settings.py'. 

2.  Add the line following line to your nail urls.py *before* the line that loads the django admin urls:
url(r'^admin/django-webfaction/', include('django-webfaction.urls')),

3.  Finally run manage.py syncdb to create the logging table.

Before running django-webfaction you should define the following in your `settings.py` file.

  WEBFACTION_USERNAME and WEBFACTION_PASSWORD: your Webfaction control panel login details
  WEBFACTION_DOMAINS: A dict where the keys are valid domain names for this project's email accounts and the values are the prefix to use to distinguish mailboxes for each domain. For example: {'mysite1.org': 'my1_',} would only allow email address to be created for mysite1.org and would create mailbox names in the form 'my1_andrew' etc
  WEBFACTION_LOG_PASSWORD: True if you want the logging to include generated mailbox passwords 
  WEBFACTION_TEST: If True then no changes will actually be made to emails or mailboxes but logging will happen as if it did

Issues
======

  * The Webfaction API is a little slow
  * Currently not much error checking for duplicates etc. I would have to do another call to list_emails (which is slow) or pass the list around in hidden form fields (which is dodgy if multiple users are working on the same site) 
  * It would be nice if 'enable_spam_protection' was hidden if the email address was redirect-only
  * many more things ;-)

Potential areas for improvement
===============================

These are the obvious areas that could be improved. I don't have any pressing need to work on any of these at the moment but contributions will be gratefully received!

  * Some attempt could be made to generate valid email addresses even if the combination of prefix+email name is longer than 32 characters
  * replace the email address TextField with a combination of a TextField and a ChoiceField populated with the available domains.
  * Make logging optional or log to standard Django admin-log
  * Allow Multiple aliases per email address
  * Allow domain creation
  * Allow deletion based on user permissions
  * Allow mailboxes to be created for existing addresses
  * Password changing
  * Allow editing of remaining spam protection settings
