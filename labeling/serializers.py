from rest_framework import serializers
from .models import DataItem, Label, Annotation, Validation, User


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['id', 'name']
        
class DataItemSerializer(serializers.ModelSerializer):
    annotation_count = serializers.ReadOnlyField()
    validation_progress = serializers.ReadOnlyField()
    is_fully_validated = serializers.ReadOnlyField()

    class Meta:
        model = DataItem
        fields = ['id', 'content', 'data_type', 'is_active', 'annotation_count', 'validation_progress', 'is_fully_validated']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'role', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'contributor')
        )
        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'enregistrement des utilisateurs.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'role']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Les mots de passe ne correspondent pas."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'contributor')
        )
        return user
                
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