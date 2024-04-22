import json, os
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from .models import Scenario
import logging

logger = logging.getLogger('django')

@login_required
@csrf_protect
def upload_files(request):
    logger.info("Upload files view called.")
    if request.method == 'GET':
        return render(request, 'registerapp/register.html')
    elif request.method == 'POST':
        logger.info("Processing POST request")
        files = request.FILES.getlist('files[]')
        base_folder = request.POST.get('base_folder', '')
        overwrite = json.loads(request.POST.get('overwrite', 'false'))

        file_paths = [generate_file_path(file.name, base_folder) for file in files]
        existing_files = [file_path for file_path in file_paths if os.path.exists(file_path)]
        new_files = [file for file, file_path in zip(files, file_paths) if file_path not in existing_files]

        if existing_files and not overwrite:
            return JsonResponse({
                'error': 'Duplicates detected',
                'duplicates': [os.path.basename(path) for path in existing_files]
            }, status=409)

        results = []
        for file, file_path in zip(files, file_paths):
            if file_path in existing_files and not overwrite:
                results.append({'status': 'error', 'message': 'File exists and overwrite not allowed',
                                'file': os.path.basename(file_path)})
            else:
                result = handle_uploaded_file(file, request.user, file_path, overwrite)
                results.append(result)

        return JsonResponse({
            'success': True,
            'uploaded_files': [result['file'] for result in results if result['status'] == 'success'],
            'errors': [result for result in results if result['status'] == 'error']
        })


def generate_file_path(filename, base_folder):
    base_path = "G:/공유 드라이브/010_ADUS/220_Development/910_Data/010_LoggingData/"
    folder = "999_Others"  # Default 폴더
    if 'eADP(eADM1)' in filename:
        folder = "101_eADP_eADM1"
    elif 'eADP(TCar)' in filename:
        folder = "100_eADP_TCar"
    elif 'ETC' in filename:
        folder = "200_Etc"

    complete_path = os.path.join(base_path, folder, base_folder, filename)
    logger.info(f"Generated file path: {complete_path}")
    return complete_path


def handle_uploaded_file(file, user, save_path, overwrite):
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        if os.path.exists(save_path) and not overwrite:
            logger.warning(f"File already exists and overwrite not allowed: {file.name}")
            return {'status': 'error', 'message': f'File already exists and overwrite not allowed: {file.name}',
                    'file': file.name}

        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        if file.name.endswith('.json'):
            with open(save_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                Scenario.objects.update_or_create(
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
        return {'status': 'success', 'message': f'File {file.name} uploaded successfully', 'file': file.name}
    except Exception as e:
        logger.exception("Failed to upload file")
        return {'status': 'error', 'message': str(e), 'file': file.name}

@require_POST
def check_duplicate(request):
    data = json.loads(request.body)
    file_path = data.get('filePath')
    is_duplicate = os.path.exists(file_path)
    return JsonResponse({'isDuplicate': is_duplicate})



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
        'temperature': request.GET.get('temperature', ''),
        'user': request.GET.get('user', ''),
    }

    scenarios = Scenario.objects.all()
    for param, value in query_params.items():
        if value:
            if param == 'user':
                scenarios = scenarios.filter(user__username__icontains=value)
            else:
                scenarios = scenarios.filter(**{f'{param}__icontains': value})

    return render(request, 'registerapp/scenario_search.html', {'scenarios': scenarios})
@login_required
def homepage(request):
    return render(request, 'registerapp/home.html', {})
