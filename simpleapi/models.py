# @Author: Manuel Rodriguez <valle>
# @Date:   20-Jul-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 07-Apr-2018
# @License: Apache license vesion 2.0


from __future__ import unicode_literals
from django.db import models
from django.conf import settings
import os

# Create your models here.

class FilesUpload(models.Model):
    docfile = models.FileField(upload_to='%Y/%m/%d/')
    uploaded = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    
    def __unicode__(self):
        return '%s' % (self.docfile.name)

    def delete(self, *args, **kwargs):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.docfile.name))
        super(FilesUpload, self).delete(*args,**kwargs)
