from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from pathlib import Path
from PIL import Image
import os

class Post(models.Model):
    MEDIA_IMAGE = 'image'
    MEDIA_VIDEO = 'video'
    MEDIA_CHOICES = [(MEDIA_IMAGE, 'Image'), (MEDIA_VIDEO, 'Video')]

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    media = models.FileField(upload_to='uploads/')
    media_type = models.CharField(max_length=10, choices=MEDIA_CHOICES)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.creator.username} - {self.media.name}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Generate thumbnail
        try:
            ext = Path(self.media.name).suffix.lower()
            thumb_path = None
            if self.media_type == self.MEDIA_IMAGE and ext in {'.jpg', '.jpeg', '.png'}:
                thumb_path = self._create_image_thumb()
            elif self.media_type == self.MEDIA_VIDEO and ext in {'.mp4', '.mov'}:
                thumb_path = self._create_video_thumb()
            if thumb_path and (not self.thumbnail or self.thumbnail.name != thumb_path):
                self.thumbnail.name = thumb_path
                super().save(update_fields=['thumbnail'])
        except Exception:
            # For Phase-1, silently ignore thumbnail errors
            pass

    def _create_image_thumb(self):
        src = self.media.path
        base = Path(src).stem
        out_dir = Path(self.media.storage.location) / 'thumbnails'
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f'{base}_thumb.jpg'
        with Image.open(src) as im:
            im.thumbnail((640, 640))
            im.convert('RGB').save(out_path, format='JPEG', quality=85)
        rel = os.path.relpath(out_path, self.media.storage.location)
        return rel.replace('\\', '/')

    def _create_video_thumb(self):
        # try to use moviepy if available
        try:
            from moviepy.editor import VideoFileClip
        except Exception:
            return None
        src = self.media.path
        base = Path(src).stem
        out_dir = Path(self.media.storage.location) / 'thumbnails'
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f'{base}_thumb.jpg'
        with VideoFileClip(src) as clip:
            frame = clip.get_frame(min(0.5, clip.duration / 2))
            img = Image.fromarray(frame)
            img.thumbnail((640, 640))
            img.convert('RGB').save(out_path, format='JPEG', quality=85)
        rel = os.path.relpath(out_path, self.media.storage.location)
        return rel.replace('\\', '/')

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

class Report(models.Model):
    REASONS = [
        ('Nudity', 'Nudity'),
        ('Violence', 'Violence'),
        ('Spam', 'Spam'),
        ('Other', 'Other'),
    ]
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REASONS)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AdminActionLog(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
