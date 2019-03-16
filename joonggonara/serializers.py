from rest_framework import serializers
from joonggonara.models import Joonggonara


class JoonggonaraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Joonggonara
        fields = ('id', 'title', 'username', 'category', 'created_at')
