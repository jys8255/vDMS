import json
import os
import re

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

from .models import Scenario, DtcCode, ErrCompId

def userName(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        return render(request, 'templates/header.html', {'user_id': user_id})
    else:
        # 로그인하지 않은 경우의 처리
        return render(request, 'templates/header.html', {'user_id': '로그인이 필요합니다'})
def handle_uploaded_file(file, user=None):
    base_save_path = "G:/공유 드라이브/010_ADUS/220_Development/910_Data/010_LoggingData/vDMS_TEST/"

    match = re.match(r'(eADP\d+)_(\d{8})_(\d{3})\.json', file.name)
    if not match:
        return {'status': 'error', 'message': f'Invalid file name format for {file.name}'}

    eadp, date, sequence = match.groups()
    save_path = os.path.join(base_save_path, eadp, date)
    os.makedirs(save_path, exist_ok=True)
    full_path = os.path.join(save_path, file.name)
    with open(full_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    try:
        file.seek(0)
        data = json.load(file)

        scenario = Scenario(
            user=user,
            file_name=file.name,
            eADP=data['eADP'],
            project_code=data['project_code'],
            location=data['location'],
            simulation_type=data['simulation_type'],
            test_Scenario_ID=data['test_Scenario_ID'],
            sw_version=data['sw_version'],
            weather=data['weather'],
            road_type=data['road_type'],
            sun_status=data['sun_status'],
            temperature=int(data['temperature']),
        )
        scenario.save()

        for dtc_code_name in data.get('dtc_code', []):
            dtc_code, _ = DtcCode.objects.get_or_create(name=dtc_code_name)
            scenario.dtc_code.add(dtc_code)

        for err_comp_id_name in data.get('err_comp_id', []):
            err_comp_id, _ = ErrCompId.objects.get_or_create(name=err_comp_id_name)
            scenario.err_comp_id.add(err_comp_id)

        return {'status': 'success', 'message': f'File {file.name} processed successfully and saved in {save_path}'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@login_required
@csrf_protect
def upload_json(request):
    if request.method == 'GET':

        return render(request, 'registerapp/register.html')
    elif request.method == 'POST':
        files = request.FILES.getlist('files[]')
        results = {'success': [], 'error': []}

        for file in files:
            result = handle_uploaded_file(file, request.user)
            if result['status'] == 'success':
                results['success'].append(result['message'])
            else:
                results['error'].append(result['message'])

        return JsonResponse(results)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


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

def homepage(request):
    return render(request, 'registerapp/home.html', {})