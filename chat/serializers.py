
from django.core import serializers


class StartSerializer(serializers.Serializer):
    topic = serializers.CharField(min_length=5, max_length=300)


class ReviewSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "reject"])
    feedback = serializers.CharField(required=False, allow_blank=True, max_length=1000)

    def validate(self, data):
        if data["action"] == "reject" and not data.get("feedback", "").strip():
            raise serializers.ValidationError({"feedback": "Required when rejecting."})
        return data