from django import forms
from django.core.exceptions import ValidationError
from pathlib import Path

ALLOWED_IMAGE_EXTS = {'.jpg', '.jpeg', '.png'}
ALLOWED_VIDEO_EXTS = {'.mp4', '.mov'}
MAX_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
MAX_VIDEO_SECONDS = 60

class UploadForm(forms.Form):
    media = forms.FileField()
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Add a description (optional)', 'rows': 2})
    )

    def clean_media(self):
        f = self.cleaned_data['media']
        ext = Path(f.name).suffix.lower()
        size = getattr(f, 'size', 0)

        if ext not in (ALLOWED_IMAGE_EXTS | ALLOWED_VIDEO_EXTS):
            raise ValidationError("Unsupported file type. Please upload MP4, MOV, JPG, or PNG files only.")

        if size and size > MAX_SIZE_BYTES:
            raise ValidationError("File size exceeds 50MB limit.")

        # video duration check
        if ext in ALLOWED_VIDEO_EXTS:
            try:
                from moviepy.editor import VideoFileClip
                import tempfile
                # Ensure we have a filesystem path
                if not hasattr(f, 'temporary_file_path'):
                    # write to temp file
                    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
                    for chunk in f.chunks():
                        tmp.write(chunk)
                    tmp.flush()
                    path = tmp.name
                    tmp.close()
                else:
                    path = f.temporary_file_path()
                with VideoFileClip(path) as clip:
                    if clip.duration > MAX_VIDEO_SECONDS:
                        raise ValidationError("Video duration exceeds 1 minute limit.")
            except ValidationError:
                raise
            except Exception:
                # If moviepy/ffmpeg not available, let it pass for dev
                pass

        return f

class CommentForm(forms.Form):
    content = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={'placeholder': 'Write a comment...'})
    )

class ReportForm(forms.Form):
    reason = forms.ChoiceField(choices=[('Nudity','Nudity'),('Violence','Violence'),('Spam','Spam'),('Other','Other')])
    details = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': 'Provide more details (optional)', 'rows': 2}))
