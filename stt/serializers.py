from rest_framework import serializers

from .models import Book, BookProgress, Shelf


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = '__all__'


class BookProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookProgress
        fields = '__all__'


class ShelfSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    bookprogresses = BookProgressSerializer(many=True)
    current_page = serializers.IntegerField()

    class Meta:
        model = Shelf
        fields = ['id', 'page', 'user', 'status', 'book', 'created_at', 'bookprogresses', 'current_page']
