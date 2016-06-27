from django.shortcuts import render
from django.http import HttpResponse
# Import the Category model
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime
from rango.bing_search import run_query
from django.shortcuts import redirect

# INMPORTANT NOTE: A function defined is a page/view to show
# It will interact with the corresponding models to gather the data
# And pass the data to the HTML template, using a context dictionary
# finally it should call render()
# Don't forget to map the url in urls.py for each funciton

# index view page
def index(request):
    request.session.set_test_cookie()
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]
    most_viewed_pages = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages':most_viewed_pages}

    visits = request.session.get('visits') #request.session is a dictionary storing cookies
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit') # create a bool determines if need to reset the cookies?
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits


    response = render(request,'rango/index.html', context_dict)

    return response


#about view page
def about(request):
    # If the visits session varible exists, take it and use it.
    # If it doesn't, we haven't visited the site so set the count to zero.
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0

    # remember to include the visit data
    return render(request, 'rango/about.html', {'visits': count})
        #return HttpResponse('Rango says it is the about page! <a href="/rango/">Index</a>')

#category view page
def category(request, category_name_slug):
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

            context_dict['result_list'] = result_list
            context_dict['query'] = query

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass

    if not context_dict['query']:
        context_dict['query'] = category.name

    return render(request, 'rango/category.html', context_dict)

# the page for the forms to add new categories
def add_category(request):
    # A HTTP POST: TO submit data to the sever
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form? Validation process
        if form.is_valid():
            # Save the new category to the database.  NOW SUBMIT!!!!!
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.  JUMP TO THE INDEX
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

from rango.forms import UserForm, UserProfileForm

def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})

def track_url(request):
    # Examine the HTTP GET request parameters and pull out the page_id. 
    # The HTTP GET requests will look something like /rango/goto/?page_id=1.
    page_id = None
    url = '/rango/' # to redirect
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views +=1
                page.save()
                url = page.url # to redirect to the page url
            except:
                pass

    return redirect(url) # imported from django.shortcuts

def get_category_list(max_results=0, starts_with=''):
        cat_list = []
        if starts_with:
                cat_list = Category.objects.filter(name__istartswith=starts_with)

        if max_results > 0:
                if cat_list.count() > max_results:
                        cat_list = cat_list[:max_results]

        return cat_list

def suggest_category(request):

        cat_list = []
        starts_with = ''
        if request.method == 'GET':
                starts_with = request.GET['suggestion']

        cat_list = get_category_list(8, starts_with)

        return render(request, 'rango/category_list.html', {'cat_list': cat_list })

@login_required
def like_category(request):

    context = RequestContext(request)
    cat_id = None  # initialize
    if request.method == 'GET':
        cat_id = request.GET['category_id'] # GET the id of the category which the user likes

    likes = 0 # initialize
    if cat_id:
        cat = Category.objects.get(id=int(cat_id)) # cast string to int
        if cat: # if the category exists
            likes = cat.likes + 1 
            cat.likes =  likes
            cat.save()

    return HttpResponse(likes)

@login_required
def restricted(request): # a simulated page to illustrate the example on accessing restricting
    return render(request, 'rango/restricted.html', {})
    #return HttpResponse("Since you're logged in, you can see this text!")

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/rango/')
