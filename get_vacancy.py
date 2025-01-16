from requests import get
from collections import Counter
from pprint import pprint
import json
from pycbrf import ExchangeRates
import statistics

# Константы для доступа к API и регион поиска вакансий
DOMAIN = 'https://api.hh.ru/'
url_vacancies = f'{DOMAIN}vacancies'
requirements_dict = {
    'python developer': ['django', 'flask', 'sqlalchemy'],
    'жестянщик': ['стрессоустойчивость', 'опыт работы', 'ответственность']
}
region = 'Москва'
rate = ExchangeRates()

# Функция для получения вакансий и анализа требований и зарплат
def get_vacancies(vacancy, requirements, region, pages):
    # Задаем параметры запроса
    params = {'text': vacancy}
    response = get(url_vacancies, params=params).json()
    count_pages = response.get('pages', 1)

    # Инициализируем результат
    result = {
        'keywords': vacancy,
        'count': 0,
        'requirements': []
    }

    # Создаем словарь для хранения данных о зарплатах по каждому требованию
    salary_data = {req: {'from': [], 'to': []} for req in requirements}
    requirements_counter = Counter()

    # Проходим по страницам вакансий
    for page in range(min(count_pages, pages)):
        print(f"Обрабатывается страница {page + 1} для вакансии '{vacancy}'")
        params['page'] = page
        response = get(url_vacancies, params=params).json()

        # Проходим по каждой вакансии на странице
        for item in response.get('items', []):
            # Пропускаем вакансии, которые не относятся к заданному региону
            if item['area']['name'] != region:
                continue
            # Получаем подробную информацию о вакансии
            vacancy_details = get(item['url']).json()
            description = vacancy_details.get('description', '').lower()
            # Ищем совпадения с требованиями в описании вакансии
            found_requirements = [req for req in requirements if req in description]
            if found_requirements:
                result['count'] += 1
                requirements_counter.update(found_requirements)

                # Обрабатываем данные о зарплате
                if vacancy_details['salary']:
                    code = vacancy_details['salary']['currency']
                    if rate[code] is None:
                        code = 'RUR'
                    k = 1 if code == 'RUR' else float(rate[code].value)

                    salary_from = k * (vacancy_details['salary']['from'] or vacancy_details['salary']['to'])
                    salary_to = k * (vacancy_details['salary']['to'] or vacancy_details['salary']['from'])

                    # Добавляем зарплатные данные к соответствующим требованиям
                    for req in found_requirements:
                        salary_data[req]['from'].append(salary_from)
                        salary_data[req]['to'].append(salary_to)

    # Рассчитываем медианные зарплаты по каждому требованию и добавляем в результат
    total_requirements = sum(requirements_counter.values())
    for requirement, count in requirements_counter.items():
        from_salaries = salary_data[requirement]['from']
        to_salaries = salary_data[requirement]['to']

        result['requirements'].append({
            'name': requirement,
            'count': count,
            'percent': round((count / total_requirements) * 100, 1),
            'down': round(statistics.median(from_salaries), 2) if from_salaries else None,
            'up': round(statistics.median(to_salaries), 2) if to_salaries else None
        })

    return result

# Преобразуем данные по каждой вакансии
final_results = []
for vacancy, requirements in requirements_dict.items():
    data = get_vacancies(vacancy, requirements, region, 10)
    if data['count'] > 0:
        final_results.append(data)


# Сохраняем результаты в файл JSON
with open('vacancies_results.json', 'w', encoding='utf-8') as f:
    json.dump(final_results, f, ensure_ascii=False)

# Печатаем результат для проверки
with open('vacancies_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(json.dumps(data, ensure_ascii=False, indent=2))
