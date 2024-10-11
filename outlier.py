import json
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


with open('data/job_normalized.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

def extract_salary(salary_string):
    if isinstance(salary_string, str):
        match = re.search(r'\$\s*([\d,]+(?:\s*-\s*[\d,]+)?)', salary_string)
        if match:
            salary_range = match.group(1).replace(',', '').split('-')
            if len(salary_range) == 2:
                return (int(salary_range[0]) + int(salary_range[1])) / 2
            elif len(salary_range) == 1:
                return int(salary_range[0])
    return None


salaries = [extract_salary(job.get('Mức lương', '')) for job in data]
salaries = [s for s in salaries if s is not None]


Q1 = np.percentile(salaries, 25)
Q3 = np.percentile(salaries, 75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR


outliers = [s for s in salaries if s < lower_bound or s > upper_bound]
non_outliers = [s for s in salaries if lower_bound <= s <= upper_bound]

plt.figure(figsize=(10, 6))
sns.boxplot(x=salaries)
plt.title('Box Plot of Salaries')
plt.xlabel('Salary (USD)')
plt.show()

print(f"Số lượng mẫu: {len(salaries)}")
print(f"Số lượng giá trị ngoại lai: {len(outliers)}")
print(f"Ngưỡng dưới: ${lower_bound:.2f}")
print(f"Ngưỡng trên: ${upper_bound:.2f}")
print("Các giá trị ngoại lai:")
for outlier in outliers:
    print(f"${outlier:.2f}")