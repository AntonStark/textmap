from rest_framework import serializers


class SentenceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    raw = serializers.CharField(allow_blank=False, trim_whitespace=False)
