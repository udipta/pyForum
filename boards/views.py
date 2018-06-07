from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from .models import Board, Post, Topic
from django.contrib.auth.models import User
from .forms import NewTopicForm, PostForm
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView
from django.utils import timezone


def home(request):
    boards = Board.objects.all()
    context = {
        'boards': boards,
    }
    return render(request, 'home.html', context)

def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    topics = board.topics.order_by('-last_updated').annotate(replies=Count('posts')-1)
    context = {
        'board': board,
        'topics': topics,
    }
    return render(request, 'topics.html', context)

@login_required
def new_topic(request, pk):
    board= get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            post = Post.objects.create(
                message= form.cleaned_data.get('message'),
                topic= topic,
                created_by= request.user
            )
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    topic.views+=1
    topic.save()
    return render(request, 'topic_posts.html', {'topic': topic})

@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form=PostForm(request.POST)
        if form.is_valid():
            post=form.save(commit=False)
            post.topic=topic
            post.created_by=request.user
            post.save()
            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form=PostForm()
    return render(request, 'reply_topic.html', {'topic':topic, 'form':form})

class PostUpdateView(UpdateView):
    model=Post
    fields=('message', )
    template_name='edit_post.html'
    pk_url_kwarg='post_pk'
    context_object_name='post'

    def form_valid(self, form):
        post=form.save(commit=False)
        post.updated_by=self.request.user
        post.update_at=timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)

