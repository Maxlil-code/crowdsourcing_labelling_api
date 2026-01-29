from collections import Counter

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import DataItem, Annotation, Validation
from .permissions import IsContributor, IsValidator
from .serializers import DataItemSerializer, AnnotationSerializer, ValidationSerializer


# Create your views here.

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
