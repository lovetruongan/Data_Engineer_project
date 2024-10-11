import json
import re
import unicodedata

def normalize_text(text):
    text = text.replace('\n', ' ').replace('\t', ' ')
    text = text.replace('đ', 'd').replace('Đ', 'D')
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return text

def convert_usd_to_vnd(salary_str):
    exchange_rate = 25000
    match = re.match(r'\$\s*([\d,]+)\s*-\s*([\d,]+)\s*/tháng', salary_str)
    if match:
        min_salary_usd = int(match.group(1).replace(',', ''))
        max_salary_usd = int(match.group(2).replace(',', ''))
        min_salary_vnd = min_salary_usd * exchange_rate
        max_salary_vnd = max_salary_usd * exchange_rate
        return f"{min_salary_vnd:,} - {max_salary_vnd:,} VND /thang"
    return salary_str

def convert_vnd_to_usd(salary_str):
    exchange_rate = 25000
    match = re.match(r'([\d,.]+)tr\s*-\s*([\d,.]+)tr\s*₫/tháng', salary_str)
    if match:
        min_salary_vnd = float(match.group(1).replace(',', '')) * 1000000
        max_salary_vnd = float(match.group(2).replace(',', '')) * 1000000
        min_salary_usd = round(min_salary_vnd / exchange_rate)
        max_salary_usd = round(max_salary_vnd / exchange_rate)
        return f"${min_salary_usd:,} - ${max_salary_usd:,} /thang"
    return salary_str

def normalize_location(location):
    normalized = normalize_text(location)
    if 'ha noi' in normalized:
        return 'ha noi'
    elif 'ho chi minh' in normalized:
        return 'ho chi minh'
    elif 'da nang' in normalized:
        return 'da nang'
    else:
        return 'other'

def is_valid_value(v):
    if v is None or v == 'N/A' or v == '':
        return False
    if isinstance(v, str) and v.strip() == '':
        return False
    return True

def process_json(data):
    if not isinstance(data, dict):
        return None

    processed_data = {}
    for k, v in data.items():
        if k == "Lĩnh vực" or k == "Url":
            continue
        if not is_valid_value(v):
            return None  # If any value is invalid, return None for the entire record
        elif k == "Mức lương":
            processed_data[k] = v
        elif k == "Địa điểm làm việc":
            processed_data[k] = normalize_location(v)
        elif isinstance(v, str):
            normalized_v = normalize_text(v)
            processed_data[k] = normalized_v if normalized_v else "other"
        elif isinstance(v, (list, dict)):
            processed_v = process_json(v)
            if processed_v is None:
                return None  # If any nested value is invalid, return None for the entire record
            processed_data[k] = processed_v
        else:
            processed_data[k] = v
    
    return processed_data


with open('data/job_listings_06_07.json', 'r', encoding='utf-8') as file:
    data = json.load(file)


normalized_data = []
for job in data:
    normalized_job = process_json(job)
    
    if normalized_job:  
        if 'Mức lương' in normalized_job:
            salary = normalized_job['Mức lương']
            if salary.strip() == "Thương lượng":
                continue
            elif 'tr' in salary and '₫' in salary:
                normalized_job['Mức lương'] = convert_vnd_to_usd(salary)
        
        normalized_data.append(normalized_job)

with open('data/job_normalized_6_7.json', 'w', encoding='utf-8') as file:
    json.dump(normalized_data, file, ensure_ascii=False, indent=4)

print(f"Success process {len(data)} records, kept {len(normalized_data)} records.")