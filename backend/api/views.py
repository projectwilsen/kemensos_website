from django.shortcuts import render
from django.http import Http404
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()
from supabase.client import Client, create_client

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# SERVE AS API (used in react or js)
class Berita(APIView):
    def get(self, request, *args, **kwargs):
        try:
            response = supabase.table('berita').select('*').execute()
            data = response.data
            return Response(data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class KataMasyarakatDetail(APIView):
    def post(self, request, id):
        try:
            response = supabase.table('kata_masyarakat').select('*').eq('id',id).execute()
            data = response.data
            return Response(data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


def index(request):
    response = supabase.table('berita').select('*').execute()
    data = response.data
    
    def get_date(item):
        return datetime.strptime(item['published_date'], '%Y-%m-%d')
    
    sorted_data = sorted(data, key=get_date, reverse = True)
    return render(request, 'index.html', {'data': sorted_data})

def kata_masyarakat(request, program_id, template_name):
    response = supabase.table('kata_masyarakat').select('*').eq('id', program_id).execute()
    data = response.data
    print(data)
    if not data:
        return render(request, '404.html', status=404)
    return render(request, template_name, data[0])





    

