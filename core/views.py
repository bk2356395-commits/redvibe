from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Post, Like, Comment, Follow, Report, AdminActionLog
from .forms import UploadForm, CommentForm, ReportForm

def home(request):
    posts = Post.objects.select_related('creator').prefetch_related('comments','likes_set').all()
    return render(request, 'core/home.html', {'posts': posts})

@login_required
def upload_view(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['media']
            ext = f.name.lower()
            media_type = 'image' if ext.endswith(('.jpg','.jpeg','.png')) else 'video'
            post = Post.objects.create(
                creator=request.user,
                media=f,
                media_type=media_type,
                description=form.cleaned_data.get('description','').strip()
            )
            messages.success(request, "Upload successful!")
            return redirect('home')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = UploadForm()
    return render(request, 'core/upload.html', {'form': form})

def profile_view(request, user_id=None):
    if user_id:
        user = get_object_or_404(User, pk=user_id)
    else:
        if not request.user.is_authenticated:
            return redirect('login')
        user = request.user
    posts = Post.objects.filter(creator=user)
    following = False
    if request.user.is_authenticated and user != request.user:
        following = Follow.objects.filter(follower=request.user, following=user).exists()
    stats = {
        'followers': user.followers.count(),
        'following': user.following.count(),
        'posts': posts.count(),
        'is_self': user == request.user,
        'is_following': following
    }
    return render(request, 'core/profile.html', {'profile_user': user, 'posts': posts, 'stats': stats})

@login_required
def toggle_like(request, post_id):
    if request.method != 'POST':
        return HttpResponseForbidden()
    post = get_object_or_404(Post, pk=post_id)
    obj, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        obj.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': post.likes_set.count()})

@login_required
def add_comment(request, post_id):
    if request.method != 'POST':
        return HttpResponseForbidden()
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        Comment.objects.create(user=request.user, post=post, content=form.cleaned_data['content'])
        return JsonResponse({'ok': True, 'count': post.comments.count()})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)

@login_required
def toggle_follow(request, user_id):
    if request.method != 'POST':
        return HttpResponseForbidden()
    target = get_object_or_404(User, pk=user_id)
    if target == request.user:
        return JsonResponse({'ok': False, 'error': 'Cannot follow yourself'}, status=400)
    obj, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        obj.delete()
        following = False
    else:
        following = True
    return JsonResponse({'ok': True, 'following': following})

@login_required
def report_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            Report.objects.create(
                post=post,
                reporter=request.user,
                reason=form.cleaned_data['reason'],
                details=form.cleaned_data.get('details','').strip()
            )
            return JsonResponse({'ok': True, 'message': "Thank you for your report. Our team will review it shortly."})
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
    return HttpResponseForbidden()

def staff_required(view):
    return user_passes_test(lambda u: u.is_staff)(view)

@staff_required
def admin_dashboard(request):
    reports = Report.objects.select_related('post','reporter','post__creator').order_by('-created_at')
    logs = AdminActionLog.objects.select_related('admin').order_by('-created_at')[:50]

    if request.method == 'POST':
        action = request.POST.get('action')
        post_id = request.POST.get('post_id')
        if action and post_id:
            post = get_object_or_404(Post, pk=post_id)
            if action == 'delete_post':
                AdminActionLog.objects.create(admin=request.user, action=f"Deleted post #{post.id} by {post.creator.username}")
                post.delete()
                messages.success(request, "Post deleted.")
            elif action == 'suspend_user':
                user = post.creator
                user.is_active = False
                user.save(update_fields=['is_active'])
                AdminActionLog.objects.create(admin=request.user, action=f"Suspended user {user.username}")
                messages.success(request, "User suspended.")
            elif action == 'view_post':
                return redirect('home')
        return redirect('admin_dashboard')

    return render(request, 'core/admin_dashboard.html', {'reports': reports, 'logs': logs})

@login_required
def confirm_age(request):
    request.session['show_age_modal'] = False
    return JsonResponse({'ok': True})
