from collections import Counter

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from .models import DataItem, Annotation, Validation, User, Label
from .permissions import IsContributor, IsValidator, IsAdminOrReadOnly
from .serializers import DataItemSerializer, AnnotationSerializer, ValidationSerializer, UserSerializer, LabelSerializer, UserRegistrationSerializer
from labeling import permissions


# Create your views here.

class LabelViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gerer les labels.
    - Recuperer: Tout utilisateur authentifié
    - Create,Update,Delete pour les administrateurs uniquement
    """
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    permission_classes = [IsAdminOrReadOnly]


class DataItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DataItem.objects.filter(is_active=True)
    serializer_class = DataItemSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def pending(self, request):
        """Liste des items en attente de labelisation"""
        annotated_ids = Annotation.objects.filter(user=request.user).values_list('item_id', flat=True)
        pending_items = DataItem.objects.exclude(id__in=annotated_ids)
        serializer = self.get_serializer(pending_items, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def progress(self, request, pk=None):
        """Obtenir la progression de l'annotation et de la validation pour un élément de données spécifique."""
        item = self.get_object()
        return Response({
            "item_id": item.id,
            "annotation_count": item.annotation_count,
            "validated_count": item.validated_annotation_count,
            "approved_count": item.approved_annotation_count,
            "is_fully_validated": item.is_fully_validated,
            "validation_progress": f"{item.validation_progress:.2f}%"
        })

class AnnotationViewSet(viewsets.ModelViewSet):
    queryset = Annotation.objects.all().select_related('item', 'label', 'user')
    serializer_class = AnnotationSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsContributor()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def consensus(self, request, pk=None):
        """
        Endpoint
        """
        annotations = Annotation.objects.filter(item_id=pk)

        if not annotations.exists():
            return Response({"error": "Aucun label soumis."}, status=404)

        label_names = [a.label.name for a in annotations]
        counts = Counter(label_names)
        majority_label, vote_count = counts.most_common(1)[0]

        return Response({
            "consensus_label": majority_label,
            "confidence": f"{(vote_count/len(label_names)) * 100:.2f}%",
            "total_votes": len(label_names)
        })

class ValidationViewSet(viewsets.ModelViewSet):
    queryset = Validation.objects.all()
    serializer_class = ValidationSerializer
    permission_classes = [IsValidator]

    def perform_create(self, serializer):
        serializer.save(validator=self.request.user)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'register':
            return [AllowAny()]
        if self.action == 'create':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'register':
            return UserRegistrationSerializer
        return UserSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        Endpoint public pour l'enregistrement des utilisateurs.
        Les nouveaux utilisateurs sont créés avec le rôle 'contributeur' par défaut.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Utilisateur créé avec succès.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Recuperer les stats d'annotation pour un utilisateur donné."""
        user = self.get_object()
        total_annotations = Annotation.objects.filter(user=user).count()

        approved_annotations = Annotation.objects.filter(
            user=user,
            validation__is_approved=True
        ).count()

        rejected_annotations = Annotation.objects.filter(
            user=user,
            validation__is_approved=False
        ).count()

        pending_validations = total_annotations - approved_annotations - rejected_annotations
        precision = (approved_annotations / total_annotations * 100) if total_annotations > 0 else 0

        return Response({
            "user": user.username,
            "role": user.role,
            "total_annotations": total_annotations,
            "approved_annotations": approved_annotations,
            "rejected_annotations": rejected_annotations,
            "pending_validations": pending_validations,
            "precision": f"{precision:.2f}%"
        })