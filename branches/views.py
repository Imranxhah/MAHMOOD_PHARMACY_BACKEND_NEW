from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly
import math
from .models import Branch
from .serializers import BranchSerializer

class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.filter(is_active=True)
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] # Admin can edit, others read

    def get_permissions(self):
         if self.action in ['create', 'update', 'partial_update', 'destroy']:
             return [IsAdminUser()]
         return [AllowAny()]

class NearestBranchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            user_lat = float(request.query_params.get('lat'))
            user_long = float(request.query_params.get('long'))
        except (TypeError, ValueError):
            return Response({"error": "Invalid or missing 'lat' and 'long' parameters."}, status=status.HTTP_400_BAD_REQUEST)

        branches = Branch.objects.filter(is_active=True)
        if not branches.exists():
            return Response({"error": "No branches found."}, status=status.HTTP_404_NOT_FOUND)

        branch_distances = []
        for branch in branches:
            dist = self.haversine(user_lat, user_long, branch.latitude, branch.longitude)
            branch_distances.append((branch, dist))

        # Sort by distance
        branch_distances.sort(key=lambda x: x[1])

        # Get all sorted branches
        sorted_branches = branch_distances

        data = []
        for branch, dist in sorted_branches:
            serializer = BranchSerializer(branch)
            branch_data = serializer.data
            branch_data['distance_km'] = round(dist, 2)
            # Add Google Maps Navigation URL for convenience
            branch_data['google_maps_url'] = f"https://www.google.com/maps/dir/?api=1&destination={branch.latitude},{branch.longitude}"
            data.append(branch_data)
            
        return Response(data, status=status.HTTP_200_OK)

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in kilometers

        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(d_lat / 2) * math.sin(d_lat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(d_lon / 2) * math.sin(d_lon / 2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance
