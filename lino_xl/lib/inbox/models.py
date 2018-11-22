# -*- coding: UTF-8 -*-
# Copyright 2011-2016 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)

"""
The :xfile:`models.py` module for `lino_xl.lib.inbox`.
"""


import logging
logger = logging.getLogger(__name__)


from lino.api import dd, rt

import mailbox
import email.errors
from django.core.exceptions import ObjectDoesNotExist

class comment_email():

    @classmethod
    def gen_subject(cls, comment,user):
        s = "{comment_id}:{user}"
        f = s.format(comment_id=comment.id, user=user.username)
        print f
        return f
    @classmethod
    def parse_subject(self, subject_str):
        try:
            comment, user = subject_str.split(":")
        except ValueError:
            return None, None
        #would like to return rows
        try:
            comment = rt.models.comments.Comment.objects.get(pk=comment)
        except ObjectDoesNotExist:
            comment = None
        try:
            user = rt.models.users.User.objects.get(username=user)
        except ObjectDoesNotExist:
            user = None
        return comment, user

    @classmethod
    def gen_href(cls,comment,user):
        # mailto:ADDR@HOST.com?subject=SUBJECT&body=Filling%20in%20the%20Body!%0D%0Afoo%0D%0Abar
        href = "mailto:{addr}?subject={subject}".format(addr=dd.plugins.inbox.comment_reply_addr,
                                                        subject=cls.gen_subject(comment,user))
        return href

    @classmethod
    def read_comment_emails(cls, mbox):
        """
        reads mbox for emails and adds valid comment-reply emails into the database
        if fails to add, adds to fail-box.

        For email replys to comments only,

        use the subject:
        :param mbox:
        :return:
        """
        if mbox is None:
            return
        m = mailbox.mbox(mbox)
        m.lock()
        fail = mailbox.mbox(mbox + ".failed")
        fail.lock()
        processed = mailbox.mbox(mbox + ".processed")
        processed.lock()
        try:
            for key in m.iterkeys():
                try:
                    message = m[key]
                    comment, user = cls.parse_subject(message.get("subject"))
                    if comment is None or user is None:
                        key = fail.add(message)
                        fail.flush()
                        m.discard(key)
                        m.flush()
                        logger.info("Failed to add comment-reply-email {subject} key:{key} added to ".format(subject=message.get("subject"), key=key) + fail._file.name)
                        continue
                    new_comment = rt.models.comments.Comment()
                    new_comment.owner = comment.owner
                    new_comment.reply_to = comment
                    new_comment.user = user
                    new_comment.short_text = message.get_payload()
                    new_comment.full_clean()
                    new_comment.save()
                    key = processed.add(message)
                    logger.info("New comment {} via email key: {}".format(new_comment.id,key))
                    processed.flush()
                    m.discard(key)
                    m.flush()
                except Exception as e:
                    key = fail.add(message)
                    fail.flush()
                    logger.exception("Failed to add comment-reply-email {subject} key:{key} added to ".format(subject=message.get("subject"), key=key) + fail._file.name)
                    m.discard(key)
                    m.flush()
        except Exception as e:
            raise e
        finally:
            for b in (m, fail, processed):
                b.flush()
                b.unlock()
                b.close()


@dd.schedule_often(10)
def check_mail_boxes():
    comment_email.read_comment_emails(dd.plugins.inbox.mbox_path)

