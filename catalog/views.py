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
from .forms import GenreForm,BookSearchForm

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
def do_export_books(request):
    exported_books=""
    count=0;
    for book in Book.objects.all():
        exported_books +="\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"\n"%(book.title,book.list_authors(),book.summary,book.display_genre(),book.isbn,book.language)
        count +=1
    send_mail("Exported %d books"%count,exported_books,'richardkellam@cox.net',['richardkellam@cox.net',],fail_silently=True)    
    return render(request,'catalog/books_exported.html',{'count':count})
from catalog.models import Language
def import_books(request):
    import csv
    csvfile=open("exported_books.csv",newline='')
    csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
    count=0
    for row in csvreader:
        print("row length: ",len(row),"\nrow: ",row)
        if len(row) < 6:
            break
        book=Book.objects.filter(title=row[0])
        if len(book) == 0: #no book with that title
            book= Book()
            book.title = row[0]
            book.isbn = row[4]
            book.save()
            s_authors=row[1].split(';')
            print(s_authors)
            found=False
            for author in Author.objects.all():
                for s_author in s_authors:
                    a_author = s_author.split(',')
                    if author.first_name == s_author[0] and author.last_name == s_author[1]:
                        found=True;
                        book.author.add(author)
            if not found:
                for s_author in s_authors:
                    a_author = s_author.split(',')
                    author=Author(first_name=a_author[0],last_name=a_author[1])
                    author.save()
                    print(author," saved")
                    book.author.add(author)
            book.summary = row[2]
            book.save()
            genres=row[3].split(',')
            for agenre in genres:
                found = False
                for genre in Genre.objects.all():
                    if genre.name == agenre:
                        book.genre.add(genre)
                        found = True
                        break
                if not found:
                    genre = Genre(name=agenre)
                    genre.save()
                    book.genre.add(genre)
            print('isbn: ',row[4],"length: ",len(row[4]),"book.isbn: ",book.isbn)
            found = False
            for lang in Language.objects.all():
                if lang.name == row[5]:
                    book.language = lang
                    found = True
            if not found:
                lang = Language(name=row[5])
                lang.save()
                book.language =lang
            book.save()
            count +=1
    return render(request,'catalog/books_imported.html',{'count':count})
def search_books(request):
    """View function for renewing a specific BookInstance by librarian."""

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = BookSearchForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            choice = request.POST['choice']
            title_search = request.POST['title_search']
            thegenre= request.POST['genre']
            author = request.POST['author']
            print("choice: ",choice," title_search: ",title_search," thegenre: ",thegenre," author: ",author)
                
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('search-results',args=[choice,title_search,thegenre,author] ) )
            #return HttpResponseRedirect(reverse('search-results',kwargs={'choice':choice,'search':search,'thegenre':thegenre,'author':author} ) )

    # If this is a GET (or any other method) create the default form.
    else:
        form = BookSearchForm()

    context = {
        'form': form,
    }
    return render(request,'catalog/search_books.html',context)

    return render(request, 'catalog/search_books.html', context)
def search_results(request,choice,title_search,thegenre,author):
    theauthor=""
    print ("choice: '",choice,"' title_search: '",title_search,'\' thegenre: \'',thegenre,"' author: '",author,"'")
    if choice.find('Genre') >= 0:
        book_list = Book.objects.filter(genre__name=thegenre)
    elif choice.find('Title') >= 0:
        book_list =[]
        title_search=title_search.strip()
        for book in Book.objects.all():
            if book.title.find(title_search) >= 0:
                book_list.append(book)
    elif choice.find('Author') >= 0:
        fields = author.split(',')
        fields[1] = fields[1].strip()
        book_list=[]
        for book in Book.objects.all():
            for author in book.author.all():
                if author.first_name.find(fields[1]) >=0 and author.last_name.find(fields[0]) >= 0:
                    theauthor = author.first_name.strip()+" "+author.last_name
                    book_list.append(book)
                    
        #book_list = Book.objects.filter(author__last_name=fields[0]).filter(author__first_name=fields[1])
    paginator = Paginator(book_list, 4) # Show 4 bookss per page.
    print ('total ',paginator.count)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context ={
        'book_list':book_list,
        'choice':choice,
        'title_search':title_search,
        'thegenre':thegenre,
        'theauthor':theauthor,
        'size': len(book_list),
        'page_obj':page_obj
        }
    for book in book_list:
        print(book.title)
    # redirect to a new URL:
    return render(request,'catalog/found_books.html',context)
    
