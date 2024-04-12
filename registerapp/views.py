import json, os
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from .models import Scenario
import logging

logger = logging.getLogger('django')

@login_required
@csrf_protect
def upload_files(request):
    logger.info("upload_files 뷰가 호출되었습니다.")
    if request.method == 'GET':
        return render(request, 'registerapp/register.html')
    elif request.method == 'POST':
        logger.info("POST 요청 처리 시작")
        files = request.FILES.getlist('files[]')
        overwrite = request.POST.get('overwrite', 'false').lower() == 'true'

        file_dict = {}
        for file in files:
            base_name = file.name.rsplit('.', 1)[0]
            file_dict.setdefault(base_name, []).append(file)

        missing_files = []
        for base_name, files in file_dict.items():
            if len(set(f.name.split('.')[-1] for f in files)) == 1:
                missing_files.append(f"{base_name} (필요한 파일: 상응하는 확장자 파일)")

        if missing_files:
            return JsonResponse({'error': 'Missing file pairs', 'missing_files': missing_files}, status=400)

        base_save_path = "G:/공유 드라이브/010_ADUS/220_Development/910_Data/010_LoggingData/900_Legacy/"
        duplicate_files = []

        for base_name, files in file_dict.items():
            for file in files:
                file_path = os.path.join(base_save_path, file.name)
                logger.info(f"file_path: {file_path}")
                if os.path.exists(file_path) and not overwrite:
                    duplicate_files.append(file.name)

        if duplicate_files:
            return JsonResponse({'status': 'duplicate', 'duplicate_files': duplicate_files}, status=409)

        upload_results = []
        for base_name, files in file_dict.items():
            for file in files:
                if not overwrite and file.name in duplicate_files:
                    continue
                upload_result = handle_uploaded_file(file, request.user, base_save_path, overwrite)
                upload_results.append(upload_result)

        success_uploads = [result for result in upload_results if result['status'] == 'success']
        error_uploads = [result for result in upload_results if result['status'] == 'error']

        if error_uploads:
            return JsonResponse({'error': 'Some files failed to process', 'details': error_uploads}, status=500)

        return JsonResponse({'success': True, 'uploadedFiles': success_uploads})


def handle_uploaded_file(file, user, base_save_path, overwrite):
    save_path = os.path.join(base_save_path, file.name)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    if os.path.exists(save_path) and not overwrite:
        return {'status': 'error', 'message': f'File already exists and overwrite is not allowed: {file.name}'}

    try:
        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # 바이너리 쓰기 후 텍스트로 읽기 위해 파일을 닫았다가 다시 엽니다.
        if file.name.endswith('.json'):
            with open(save_path, 'r', encoding='utf-8') as json_file:  # UTF-8 인코딩 지정
                data = json.load(json_file)

                scenario, created = Scenario.objects.update_or_create(
                    file_name=file.name,
                    defaults={
                        'user': user,
                        'test_case_ids': data.get('Test_Case_IDs', []),
                        'usernames': data.get('usernames', []),
                        'eADP': data.get('eADP', ''),
                        'project_code': data.get('project_code', ''),
                        'location': data.get('location', ''),
                        'sw_version': data.get('sw_version', ''),
                        'weather': data.get('weather', ''),
                        'road_type': data.get('road_type', ''),
                        'road_status': data.get('road_status', ''),
                        'sun_status': data.get('sun_status', ''),
                        'test_mode': data.get('test_mode', ''),
                        'temperature': data.get('temperature', ''),
                        'description': data.get('description', '')
                    }
                )
        return {'status': 'success', 'message': file.name}
    except json.JSONDecodeError as e:
        return {'status': 'error', 'message': f'JSON decode error - {str(e)}'}
    except FileNotFoundError:
        return {'status': 'error', 'message': 'File not found error'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
@login_required
def search_scenarios(request):
    query_params = {
        'test_case_id': request.GET.get('test_case_id', ''),
        'username': request.GET.get('username', ''),
        'eADP': request.GET.get('eADP', ''),
        'project_code': request.GET.get('project_code', ''),
        'location': request.GET.get('location', ''),
        'sw_version': request.GET.get('sw_version', ''),
        'weather': request.GET.get('weather', ''),
        'road_type': request.GET.get('road_type', ''),
        'road_status': request.GET.get('road_status', ''),
        'sun_status': request.GET.get('sun_status', ''),
        'test_mode': request.GET.get('test_mode', ''),
        'temperature': request.GET.get('temperature', '')
    }

    scenarios = Scenario.objects.all()
    for param, value in query_params.items():
        if value:
            scenarios = scenarios.filter(**{f'{param}__icontains': value})

    return render(request, 'registerapp/scenario_search.html', {'scenarios': scenarios})

@login_required
def homepage(request):
    return render(request, 'registerapp/home.html', {})
