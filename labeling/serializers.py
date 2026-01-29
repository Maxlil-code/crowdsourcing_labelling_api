from rest_framework import serializers
from .models import DataItem, Label, Annotation, Validation


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['id', 'name']
        
class DataItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataItem
        fields = ['id', 'content', 'data_type', 'is_active']
                
class AnnotationSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    
    
    class Meta:
        model = Annotation
        fields = ['id', 'item', 'user', 'label', 'created_at']
        
    def validate(self, data):
        request = self.context.get('request')
        item = data.get('item')
        
        if Annotation.objects.filter(item=item, user=request.user).exists():
            raise serializers.ValidationError("Vous avez déjà annoté cet élément.")
        
        return data
    
class ValidationSerializer(serializers.ModelSerializer):
    validator = serializers.ReadOnlyField(source='validator.username')
    
    class Meta:
        model = Validation
        fields = ['id', 'annotation', 'validator', 'is_approved', 'feedback', 'validated_at']