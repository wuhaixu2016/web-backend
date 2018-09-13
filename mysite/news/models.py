from django.db import models

# Create your models here.
class New(models.Model):
    news_title = models.CharField(max_length=200)
    news_date = models.DateTimeField('date published')

class Video(models.Model):
    video_title = models.CharField(max_length=200)
    video_url = models.CharField(max_length=200)
    video_date = models.DateTimeField('date published')
    def __str__(self):
        return self.video_url