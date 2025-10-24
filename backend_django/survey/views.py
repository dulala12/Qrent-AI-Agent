# survey/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SurveySerializer
from .utils import build_data_json, save_data_json

class SurveyView(APIView):
    def post(self, request):
        ser = SurveySerializer(data=request.data)
        if not ser.is_valid():
            return Response({"ok": False, "errors": ser.errors}, status=status.HTTP_400_BAD_REQUEST)
        data_dict = build_data_json(ser.validated_data)
        filename = request.query_params.get("filename")  # 可选：?filename=my_case
        file_path = save_data_json(data_dict, filename_stem=filename)
        return Response({
            "ok": True,
            "message": "data saved",
            "filename": file_path.name,
            "path": str(file_path),
            "url": f"/files/{file_path.name}",
            "for_agent": {"data": str(file_path)}
        })
