from django import template
import re

register = template.Library()

@register.filter(name='extract_path_from_filename')
def extract_path_from_filename(file_name):
    match = re.match(r'(eADP\d+)_(\d{8})_(\d{3})\.json', file_name)
    if not match:
        return "파일 경로 정보를 가져올 수 없습니다."
    eadp, date, _ = match.groups()
    return f"{eadp} 폴더의 {date}에 저장되었습니다."
