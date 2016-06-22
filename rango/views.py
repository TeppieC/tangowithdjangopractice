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

	# Create a context dictionary which we can pass to the template rendering engine.
	context_dict = {}

	try:
		# Can we find a category name slug with the given name?
		# If we can't, the .get() method raises a DoesNotExist exception.
		# So the .get() method returns one model instance or raises an exception.
		category = Category.objects.get(slug=category_name_slug)
		context_dict['category_name'] = category.name

		# Retrieve all of the associated pages.
		# Note that filter returns >= 1 model instance.
		pages = Page.objects.filter(category=category)

		# Adds our results list to the template context under name pages.
		context_dict['pages'] = pages
		# We also add the category object from the database to the context dictionary.
		# We'll use this in the template to verify that the category exists.
		context_dict['category'] = category
	except Category.DoesNotExist:
		# We get here if we didn't find the specified category.
		# Don't do anything - the template displays the "no category" message for us.
		pass

	# Go render the response and return it to the client.
	return render(request, 'rango/category.html', context_dict)
	from rango.forms import CategoryForm

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
