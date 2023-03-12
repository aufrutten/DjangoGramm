from rest_framework import serializers


class ExistInValidator:

    def __init__(self, queryset, message):
        self.queryset = queryset
        self.message = message or self.message

    def __call__(self, value):
        if not self.queryset.filter(id=value).exists():
            raise serializers.ValidationError(self.message.format(value))

