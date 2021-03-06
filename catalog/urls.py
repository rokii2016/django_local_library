from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
]
urlpatterns += [
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
]
urlpatterns += [
    path('borrowed/', views.LoanedBooksListView.as_view(), name='all-borrowed'),
]
urlpatterns += [
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]
urlpatterns += [
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),
]
urlpatterns += [
    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
]
urlpatterns += [
    path('book',views.BookGenreListView.as_view(),name='books-genre'),
]
urlpatterns += [
    path('book/booksbygenre',views.get_genre,name='books-by-genre'),
]
#urlpatterns += [
#    path('book/listbooksbygenre/<str:genre>',views.BookByGenreListView.as_view(),name='list-books-by-genre'),
#]
urlpatterns += [
    path('book/listbooksbygenre<str:genre>',views.show_books_by_genre,name='list-books-by-genre'),
]
urlpatterns += [
    path('book/books',views.get_book_borrow_id,name='borrow-renew'),
]
urlpatterns += [
    path('book/bookborrow',views.set_book_borrow,name='my-borrow'),
]
urlpatterns += [
    path('book/exportbooks',views.do_export_books,name='export-books'),
]
urlpatterns += [
    path('book/importbooks',views.import_books,name='import-books'),
]
urlpatterns += [
    path('book/searchbooks',views.search_books,name='search-books'),
]
urlpatterns += [
    path('book/<str:choice>/<str:title_search>/<str:thegenre>/<str:author>/searchresults',views.search_results,name='search-results'),
]
