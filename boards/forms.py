from django import forms
from boards.models import Topic, Post

class NewTopicForm(forms.ModelForm):

    class Meta():
        model = Topic
        fields = ('subject', 'message')

    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'What is in your mind?'}
            ),
        max_length=1000,
        help_text='The max length of the text is 1000.'
    )


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message', ]
