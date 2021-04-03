from rest_framework.decorators import api_view
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.validators import RegexValidator
from django import forms
from django.urls import reverse
from . import util
import mistune
from random import choice
import os

# entries = util.list_entries()
title_validator = RegexValidator(r"^[a-zA-Z0-9_\- ]+$", "Entry name can not have any special characters.") 

class NewTaskForm(forms.Form):
    title = forms.CharField(label="Title", required=True, validators=[title_validator],widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    content=forms.CharField(label="Content", widget=forms.Textarea)


def index(request):
    if 'entries' not in request.session:
        request.session["entries"] = []
    request.session["entries"] = util.list_entries()
    return render(request, "encyclopedia/index.html", {
        "entries": request.session["entries"]
    })

def entry_page(request,entry):

    content = util.get_entry(entry)

    if content is None:
        content = "# Requested Page was not Found!\n Go back to the [Home](/) page"


    return render(request, 'encyclopedia/entry.html', {
        'entry':entry,
        'content':mistune.markdown(content)
        })

@api_view(["GET","POST"])
def search_page(request):
    #print(entries)
    search_term = request.data.get("q")
    content = util.get_entry(search_term)


    if content is None:
        request.session["entries"] = util.list_entries()
        search_matches = [entry for entry in request.session["entries"] if search_term in entry]
        return render(request, 'encyclopedia/search-results.html',{
            "search_matches":search_matches,
        })


    return render(request, 'encyclopedia/entry.html', {
        'entry':search_term,
        'content':mistune.markdown(content)
        })

@api_view(["GET","POST"])
def new_page(request):
    if request.method=='POST':
        form = NewTaskForm(request.POST)
        if form.is_valid():

            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            
            if os.path.exists(f'entries/{title}.md'):
                return render(request, 'encyclopedia/new-page.html',{
                    'error':'This entry already exists! Please give a new title.',
                    'form': form,
                })
            else:
                with open(f'entries/{title}.md',"w") as f:
                    f.writelines(content)
                return HttpResponseRedirect(
                    reverse('entry_page', kwargs={'entry':title})
                )

        
        else:
            new_form = NewTaskForm(auto_id="wiki_%s")
            return render(request, 'encyclopedia/new-page.html',{
                'error':form.errors,
                'form': new_form,
            })
   
    new_form = NewTaskForm(auto_id="wiki_%s")
    return render(request, 'encyclopedia/new-page.html', {
        'form':new_form,
    })


@api_view(["GET"])
def edit_page(request, id):
    if request.method == 'GET':
        with open(f'entries/{id}.md') as f:
            content = f.read()
        data = {'title':id, 'content':content}
        form = NewTaskForm(data,auto_id="wiki_%s")
        form.fields['title'].widget.attrs['readonly'] = True
        
        if form.is_valid():   
            return render(request, 'encyclopedia/edit-page.html', {
                'form': form,
            })
        else:
            #print(form.errors)
            new_form = NewTaskForm()
            return render(request, 'encyclopedia/edit-page.html', {
                'form': new_form,
                'error': 'error while fetching the entry for edit.',
            })
@api_view(["POST"])
def post_edit_page(request):           
    if request.method == 'POST':
        form = NewTaskForm(request.POST)
        if form.is_valid():

            title = form.cleaned_data['title']
            content = form.cleaned_data['content']

            with open(f'entries/{title}.md',"w") as f:
                f.writelines(content)
            return HttpResponseRedirect(
                reverse('entry_page', kwargs={'entry':title})
            )        
        else:
            return render(request, 'encyclopedia/edit-page.html',{
                'error':'Invalid Form Submitted!',
            })
            
def random_page(request):
    request.session["entries"] = util.list_entries()
    random_choice = choice(request.session["entries"])
    
    return HttpResponseRedirect(
        reverse('entry_page', kwargs={'entry':random_choice})
        )
