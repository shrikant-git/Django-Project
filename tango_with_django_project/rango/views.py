from django.template import RequestContext
from django.shortcuts import render_to_response

from rango.models import Category
from rango.models import Page, UserProfile

from django.http import HttpResponse, HttpResponseRedirect

from rango.forms import CategoryForm, UserForm, UserProfileForm
from xml.dom.domreg import registered
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from pip._vendor.requests.models import Response

from datetime import datetime
from rango.bing_search import run_query
from _codecs import encode
 

def index(request):
                    #request.session.set_test_cookie()
                    
                    context = RequestContext(request) 
                    category_list = Category.objects.order_by('-likes')[:5]  #sorts the likes in descending order, by including minus sign.
                    context_dict = {'categories': category_list}
                    for category in category_list:
                        category.url = category.name.replace(' ','_')
                    return render_to_response('rango/index.html', context_dict, context)
                       
                       #### CLIENT-SIDE COOKIE ####
                    response = render_to_response('rango/index.html', context_dict, context)
                    visits = int(request.COOKIES.get('visits','0'))
                    if request.COOKIES.has_key('last_visit'):
                        last_visit = request.COOKIES['last_visit']
                        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
                        if(datetime.now() - last_visit_time).days > 0:
                            response.set_cookie('visits', visits+1)
                            response.set_cookie('last_visit',datetime.now())
                    else:
                        response.set_cookie('last_visit', datetime.now())
                        
                    return response
                        #### SERVER-SIDE COOKIE ####
                    #if request.session.get('last_visit'):
                    #    last_visit_time = request.session.get('last_visit')
                    #    visits = request.session.get('visits',0)
                        
                    #    if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days>0:
                    #        request.session['visits'] = visits + 1
                    #        request.session['last_vist'] = str(datetime.now())
                            
                    #else:
                    #    request.session['last_visit'] = str(datetime.now())
                    #    request.session['visits'] = 1
                    #return render_to_response('rango/index.html',context_dict,context)

def about(request):
                    context = RequestContext(request)
                    
                    if request.session.get('visits'):
                        count = request.session.get('visits')
                    else:
                        count = 0
                    return render_to_response('rango/about.html',{'visits': count}, context)
                    

def category(request, category_name_url):
                    context = RequestContext(request)
                    category_name = category_name_url.replace('_',' ')
                    context_dict = {'category_name':category_name}
                    try:
                        category = Category.objects.get(name = category_name)
                        pages = Page.objects.filter(category=category)
                        context_dict['pages'] = pages
                        context_dict['category'] = category
                    except Category.DoesNotExist:
                        pass
                    return render_to_response('rango/category.html', context_dict, context)
                
def add_category(request):
                    context = RequestContext(request)
                    
                    if request.method == 'POST':
                        form = CategoryForm(request.POST)
                        
                        if form.is_valid():
                            form.save(commit=True)
                            return index(request)
                        
                        else:
                            print form.errors
                            
                    else:
                        form = CategoryForm()
                        
                    return render_to_response('rango/add_category.html',{'form':form},context)
                
def register(request):
                    #if request.session.test_cookie_worked():
                    #    print ">>> TEST COOKIE WORKED..."
                    #    request.session.delete_test_cookie()
                        
                    context = RequestContext(request)
                    
                    registered = False
                    if request.method =='POST':
                        user_form = UserForm(data=request.POST)     #gets the information entered into the form
                        profile_form = UserProfileForm(data=request.POST)
                        
                        if user_form.is_valid() and profile_form.is_valid():
                            user = user_form.save()
                            user.set_password(user.password)
                            user.save()
                            profile = profile_form.save(commit=False)
                            profile.user = user
                            
                            if 'picture' in request.FILES:
                                profile.picture = request.FILES['picture']
                                profile.save()
                            registered = True
                        
                        else:
                            print user_form.errors, profile_form.errors
                        
                    else:
                        user_form = UserForm()
                        profile_form = UserProfileForm()
                        
                    return render_to_response(
                            'rango/register.html',
                            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
                            context)
                
def user_login(request):
                    context = RequestContext(request)
                    
                    if request.method == 'POST':
                        username = request.POST['username']
                        password = request.POST['password']
                        user = authenticate(username=username, password=password)
                        
                        if user is not None:
                            if user.is_active:
                                print 'reached here...'
                                login(request, user)
                                return HttpResponseRedirect('/rango/')
                            else:
                                return HttpResponse("Your Rango account is disabled")
                        else:
                            print "Invalid login details: {0}, {1}". format(username, password)
                            return HttpResponse("Invalid login details supplied")
                    else:
                        return render_to_response('rango/login.html', {}, context)
                    
@login_required
def restricted(request):
                    return HttpResponse("Since you're logged in, you can see this text...")
                
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')                
                        
                                        
def search(request):
    context = RequestContext(request)
    result_list = []
    
    if request.method == 'POST':
        query = request.POST['query'].strip()
        
        if query:
            result_list = run_query(query)
            
    return render_to_response('rango/search.html',{'result_list':result_list}, context)

def get_category_list():
    cat_list = Category.objects.all()
    
    for cat in cat_list:
        return cat_list
        #cat.url = encode_url(cat.name)    #encode function not defined...hence the issue of cat_list    
    
    #return cat_list

@login_required
def profile(request):
    context = RequestContext(request)
    cat_list = get_category_list()
    context_dict = {'cat_list': cat_list}
    u = User.objects.get(username = request.user)
    try:
        up = UserProfile.objects.get(user=u)
    except:
        up = None
        
    context_dict['user'] = u
    context_dict['userprofile'] = up
    return render_to_response('rango/profile.html', context_dict, context)


    