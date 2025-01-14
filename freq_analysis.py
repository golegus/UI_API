key_skills={}
skills=['python', 'python', 'django', 'python', 'sql', 'sql', 'flask']

#частотный анализ
for item in skills:
    if item in key_skills:
        key_skills[item] += 1
    else:
        key_skills[item] = 1
print(key_skills)

# Сортировка
result = sorted(key_skills.items(), key=lambda x: x[1], reverse=True)
print(result)

# сбор данных по вакансиям в класс Vacancy
class Vacancy:
    def __init__(self, name, salary):
        self.name=name
        self.salary=salary

vacancies =[{'name':'python', 'salary':200}, {'name':'django', 'salary':150}]
objs=[]

for item in  vacancies:
    vacancy = Vacancy(item['name'], item['salary'])
    objs.append(vacancy)

for item in objs:
    print(f"Вакансия: {item.name}, Зарплата: {item.salary}")    




