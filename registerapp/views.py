import json, os, re

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

from .models import Scenario, DtcCode, ErrCompId
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
        logger.info(f"first files_list : {files}")
        overwrite = request.POST.get('overwrite', 'false').lower() == 'true'

        logger.info(f"overwrite : {overwrite}")

        json_files = {file.name.rsplit('.', 1)[0]: file for file in files if file.name.endswith('.json')}
        mat_files = {file.name.rsplit('.', 1)[0]: file for file in files if file.name.endswith('.mat')}
        missing_files = []
        for name in json_files:
            if name not in mat_files:
                missing_files.append(f"{name}.mat")
        for name in mat_files:
            if name not in json_files:
                missing_files.append(f"{name}.json")

        if missing_files:
            return JsonResponse({'error': 'Missing file pairs', 'missing_files': missing_files}, status=400)

        base_save_path = "G:/공유 드라이브/010_ADUS/220_Development/910_Data/010_LoggingData/vDMS/"

        duplicate_files = []
        for file in files:
            pattern = r'(eADP\d+)_(\d{8})_(\d{3})\.(json|mat)'
            match = re.match(pattern, file.name)
            if not match:
                return JsonResponse({'error': 'Invalid file name format', 'file_name': file.name}, status=400)

            eadp, date, sequence, extension = match.groups()
            file_dir = os.path.join(base_save_path, eadp, date)
            file_path = os.path.join(file_dir, file.name)
            logger.info(f"file_path: {file_path}")

            if os.path.exists(file_path) and not overwrite: #파일이 이미 존재하고 사용자가 덮어쓰기를 허용하지 않았을 때
                duplicate_files.append(file.name)
                logger.info(f"Duplicate file: {duplicate_files}")
        if duplicate_files:
            return JsonResponse({'status': 'duplicate', 'duplicate_files': duplicate_files}, status=409)

        upload_results = []
        for file in files:
            if not overwrite and file.name in duplicate_files:
                continue  # 중복 파일이면서 덮어쓰기 옵션이 아닐 때는 건너뛰기
            upload_result = handle_uploaded_file(file, request.user, base_save_path, overwrite)
            logger.info(f"upload_result: {upload_result}")
            upload_results.append(upload_result)

        success_uploads = [result for result in upload_results if result['status'] == 'success']
        error_uploads = [result for result in upload_results if result['status'] == 'error']

        if error_uploads:
            return JsonResponse({'error': 'Some files failed to process', 'details': error_uploads}, status=500)

        return JsonResponse({'success': True, 'uploadedFiles': success_uploads})

def handle_uploaded_file(file, user, base_save_path, overwrite):
    pattern = r'(eADP\d+)_(\d{8})_(\d{3})\.(json|mat)'
    match = re.match(pattern, file.name)
    if not match:
        return {'status': 'error', 'message': f'Invalid file name format for {file.name}'}

    eadp, date, sequence, extension = match.groups()
    save_path = os.path.join(base_save_path, eadp, date, file.name)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    if os.path.exists(save_path) and not overwrite:
        return {'status': 'error', 'message': f'File already exists and overwrite is not allowed: {file.name}'}

    try:
        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        if file.name.endswith('.json'):
            with open(save_path, 'r') as json_file:
                data = json.load(json_file) # 중복 시 기존 데이터 업데이트 로직 필요 (여기서 구현)
                scenario, created = Scenario.objects.update_or_create(
                    file_name=file.name,  # 파일 이름으로 기존 레코드를 식별
                    defaults={  # 업데이트할 필드 목록
                        'user': user,
                        'eADP': data['eADP'],
                        'project_code': data['project_code'],
                        'location': data['location'],
                        'simulation_type': data['simulation_type'],
                        'test_Scenario_ID': data['test_Scenario_ID'],
                        'sw_version': data['sw_version'],
                        'weather': data['weather'],
                        'road_type': data['road_type'],
                        'sun_status': data['sun_status'],
                        'temperature': int(data['temperature']),
                    }
                )

                for dtc_code_name in data.get('dtc_code', []):
                    dtc_code, _ = DtcCode.objects.get_or_create(name=dtc_code_name)
                    scenario.dtc_code.add(dtc_code)

                for err_comp_id_name in data.get('err_comp_id', []):
                    err_comp_id, _ = ErrCompId.objects.get_or_create(name=err_comp_id_name)
                    scenario.err_comp_id.add(err_comp_id)

        return {'status': 'success', 'message': file.name}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@login_required
def search_scenarios(request):
    eADP = request.GET.get('eADP', '')
    project_code = request.GET.get('project_code', '')
    location = request.GET.get('location', '')
    sw_version = request.GET.get('sw_version', '')
    weather = request.GET.get('weather', '')
    road_type = request.GET.get('road_type', '')
    user = request.GET.get('username', '')

    scenarios = Scenario.objects.all()

    if eADP:
        scenarios = scenarios.filter(eADP__icontains=eADP)
    if project_code:
        scenarios = scenarios.filter(project_code__icontains=project_code)
    if location:
        scenarios = scenarios.filter(location__icontains=location)
    if sw_version:
        scenarios = scenarios.filter(sw_version__icontains=sw_version)
    if weather:
        scenarios = scenarios.filter(weather__icontains=weather)
    if road_type:
        scenarios = scenarios.filter(road_type__icontains=road_type)
    if user:
        scenarios = scenarios.filter(user__username__icontains=user)

    return render(request, 'registerapp/scenario_search.html', {'scenarios': scenarios})
@login_required
def homepage(request):
    return render(request, 'registerapp/home.html', {})