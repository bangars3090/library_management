from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Book, Member, Circulation, Reservation
from django.db import transaction
import hashlib
from django.core.cache import cache



def generate_cache(request):
    request_data = str(request.data) if request.data else ''
    request_path = request.path
    cache_key = hashlib.md5((request_path+request_data).encode()).hexdigest()
    return cache_key


class IssueBookAPIView(APIView):
    def post(self, request):
        book_id=request.POST.get('book_id')
        cache_key = generate_cache(request)
        
        cache_resp = cache.get(cache_key)
        if cache_resp:
            return cache_resp

        try:
            book = Book.objects.get(BookID=book_id)
        except Book.DoesNotExist:
            response = JsonResponse({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND, safe=True)
            cache.set(cache_key, response, timeout=60)
            return response 
        with transaction.atomic():
            if book.NumberOfCopies > 0:
                Circulation.objects.create(book=book, event_type=1)
                book.NumberOfCopies -= 1
                book.save()
                response = JsonResponse({"messgae": "Book issues successfully"}, status=status.HTTP_200_OK, safe=True)
                cache.set(cache_key, response, timeout=60)
                return response
            elif book.NumberOfCopies == 0:
                Reservation.objects.create(book=book, member_id=request.user.id, event_type='PENDING')
                response = JsonResponse({"messgae": "Book added to reservation"}, status=status.HTTP_200_OK, safe=True)
                cache.set(cache_key, response, timeout=60)
                return response 
            else:
                response = JsonResponse({"message": "Invalid Request"},status=status.HTTP_400_BAD_REQUEST, safe=True)
                cache.set(cache_key, response, timeout=60)
                return response
        
class ReturnBookAPIView(APIView):
    def post(self, request):
        book_id=request.POST.get('book_id')
        cache_key = generate_cache(request)
        #check for cache
        cache_resp = cache.get(cache_key)
        if cache_resp:
            return cache_resp
        
        try:
            circulation = Circulation.objects.get(book_id=book_id, member_id=request.user.id)
        except Circulation.DoesNotExist:
            response = JsonResponse({"message":"Book not checked out by the given user"}, status=status.HTTP_404_NOT_FOUND, safe=True)
            cache.set(cache_key, response, timeout=60)
            return response
        with transaction.atomic():
            book = circulation.book
            book.NumberOfCopies += 1
            circulation.event_type=2
            circulation.save()
            # check if any reservation exist for the book returned if yes fulfill the first reservation created
            reservation = Reservation.objects.filter(book=book, status='PENDING').first()
            reservation.status = 'FULFILLED'
            reservation.save()
            book.save()
            response = JsonResponse({"message":"Book returned successfully"}, status=status.HTTP_200_OK, safe=True)
            cache.set(cache_key, response, timeout=60)
            return response

class FulFillAPIView(APIView):
    def post(self, request):
        book_id = request.POST.get('book_id')
        cache_key = generate_cache(request)
        cache_resp = cache.get(cache_key)
        if cache_resp:
            return cache_resp
        try:
            reservation = Reservation.objects.filter(book_id=book_id, status='PENDING').first()
        except Reservation.DoesNotExist:
            response = JsonResponse({"message": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND, safe=True)
            cache.set(cache_key, response, timeout=60)
            return response
        reservation.status='FULFILLED'
        reservation.save()
        response = JsonResponse({"message": "Reservation fulfilled"}, status=status.HTTP_200_OK, safe=True)
        cache.set(cache_key, response, timeout=60)
        return response
    