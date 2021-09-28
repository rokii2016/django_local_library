from django.shortcuts import render

# Create your views here.
from .models import Book, Author, BookInstance, Genre

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_genres = Genre.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
        'num_genres':num_genres,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)
from django.views import generic

class BookListView(generic.ListView):
    model = Book
    paginate_by = 4
class BookDetailView(generic.DetailView):
    model = Book    
class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 4
class AuthorDetailView(generic.DetailView):
    model = Author    
from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
# Added as part of challenge!
from django.contrib.auth.mixins import PermissionRequiredMixin
class LoanedBooksListView(PermissionRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed.html'
    paginate_by = 4
    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')
import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author,Book

class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}

class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('books')

class BookCreate(CreateView):
    model = Book
    fields = ['title','author','summary','isbn','genre']
    initial = {'date_of_death': '11/06/2020'}

class BookUpdate(UpdateView):
    model = Book
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('authors')
#class BookByGenreListView(generic.ListView):
#    """Generic class-based view listing books on loan to current user."""
#    model = Book
#    template_name ='catalog/list_books_by_genre.html'
#    paginate_by = 10
#    #def get_queryset(self):
#    #    return Book.objects.filter(genre='Bible Study')
class BookGenreListView(generic.ListView):
    model = Genre
    #template_name ='catalog/genre_list.html'
    paginate_by = 4
from .forms import GenreForm

from django.core.paginator import Paginator
def show_books_by_genre(request,genre):
    book_list = Book.objects.filter(genre__name = genre)
    paginator = Paginator(book_list, 4) # Show 4 bookss per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={
        'page_obj': page_obj,
        'genre': genre,
        #'book_list' : book_list,
        }
    return render(request,'catalog/list_books_by_genre.html',context)
def get_genre(request):
    """View function for renewing a specific BookInstance by librarian."""

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = GenreForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            genre = request.POST['choice']
            print("Genre is ",genre)
            context ={
                'genre':genre,
                'book_list':Book.objects.all(),
                }

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('list-books-by-genre',kwargs={'genre':genre}) )

    # If this is a GET (or any other method) create the default form.
    else:
        form = GenreForm()

    context = {
        'form': form,
    }

    return render(request, 'catalog/books_by_genre.html', context)
from catalog.forms import BookForm,BookInstanceForm
from django.contrib.auth.models import User
def get_book_borrow_id(request):
    """View function for renewing a specific BookInstance by librarian."""

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = BookInstanceForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            title = request.POST['choice']
            print("Book title is ",title)
            bookinstances = BookInstance.objects.all()
            for bookinstance in bookinstances:
                if bookinstance.book.title == title:
                    pk = bookinstance.id
            context ={
                'pk':pk,
                'book_list':Book.objects.all(),
                }

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('renew-book-librarian',kwargs={'pk':pk}) )

    # If this is a GET (or any other method) create the default form.
    else:
        form = BookInstanceForm()

    context = {
        'form': form,
    }

    return render(request, 'catalog/books_by_title.html', context)
from django.core.mail import send_mail
def set_book_borrow(request):
    """View function for renewing a specific BookInstance by librarian."""

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = BookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            title = request.POST['choice']
            print("Book title is ",title)
            bookinstances = BookInstance.objects.all()
            found = False
            for bookinstance in bookinstances:
                if bookinstance.book != None and bookinstance.book.title == title:
                    found = True
                    break
            for book in Book.objects.all():
                if book.title == title:
                    break
            if not found:
                send_mail('Borrow "'+title+'"','I would like to borrow: \n"'+title+'"\n'+request.user.username,request.user.email,['richardkellam@cox.net',],fail_silently = False)
#                n_bookinstance = BookInstance.objects.create()
#                n_bookinstance.book = book
#                print(n_bookinstance.borrower)
#                n_bookinstance.borrower = request.user
#                n_bookinstance.status ='o'
#                n_bookinstance.due_back = datetime.date.today() + datetime.timedelta(weeks=3)
#
#                n_bookinstance.save()
            

            # redirect to a new URL:
            return render(request,'catalog/book_borrowed.html',{'title':title})

    # If this is a GET (or any other method) create the default form.
    else:
        form = BookForm()

    context = {
        'form': form,
    }

    return render(request, 'catalog/books_by_title.html', context)
