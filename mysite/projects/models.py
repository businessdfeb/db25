from django.db import models
from students.models import Student
from advisors.models import Advisor

class FinalProject(models.Model):
    title = models.CharField(max_length=255)
    students = models.ManyToManyField(Student, related_name='projects')
    advisor = models.ForeignKey(Advisor, on_delete=models.SET_NULL, null=True, related_name='leading_projects')
    committee_members = models.ManyToManyField(Advisor, related_name='committee_projects', blank=True)
    description = models.TextField()
    submission_date = models.DateField(null=True, blank=True)

    STATUS_CHOICES = [
        ('in_progress', 'ກຳລັງດຳເນີນການ'),
        ('completed', 'ສຳເລັດ'),
        ('pending_review', 'ລໍຖ້າກວດສອບ'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')

    # You might want to add a FileField for document uploads later
    # documentation = models.FileField(upload_to='project_documents/', null=True, blank=True)

    def __str__(self):
        return self.title
